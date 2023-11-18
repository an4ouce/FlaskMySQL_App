from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_wtf.csrf import CSRFProtect
from forms import ContactForm
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import hashlib
import string
import os

letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation
csrf = CSRFProtect()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

csrf.init_app(app)

app.config['MYSQL_HOST'] = "db"
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')

mysql = MySQL(app)

@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg=''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('''SELECT salt FROM users WHERE username = "{}"'''.format(username))
            salt = cursor.fetchone()
            password_to_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt['salt'], 100000).hex()
            cursor.execute('SELECT * FROM users WHERE username = %s and pwd_with_salt = %s', (username, password_to_check))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg="Вы успешно вошли!"
                return redirect(url_for('home'))
            else:
                msg="Неверный пароль!"
        except:
            msg="Пользователь не найден!"
    return render_template('index.html', msg=msg)

@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/register/', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s or email = %s', (username, email))
        account = cursor.fetchone()

        if account:
            msg = 'Такой пользователь уже зарегистрирован'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Неверный формат e-mail'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Имя пользователя может содержать латинские буквы и цифры'
        elif len(password) < 8:
            msg = "Пароль слишком короткий!"
        elif (all(char in special_chars for char in password)):
            msg = "Пароль не может состоять только из спецсимволов!"
        elif not (any(char in digits for char in password)):
            msg = "Пароль не может состоять только из букв!"
        elif not (any(char in letters for char in password)):
            msg = "Пароль не может состоять только из цифр!"
        elif not (any(char in letters[26:] for char in password)):
            msg = "В пароле хотя бы одна буква должна быть в верхнем регистре!"
        elif not (any(char in special_chars for char in password)):
            msg = "В пароле отсутствует спецсимвол!"
        elif not username or not password or not email:
            msg = 'Пожалуйста, заполните все поля'
        else:
            salt = os.urandom(32)
            pwd_with_salt = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, email, pwd_with_salt, salt))
            mysql.connection.commit()
            msg = 'Вы успешно зарегистрированы!' 
    elif request.method == 'POST':
        msg = 'Пожалуйста, заполните все поля'
    return render_template('register.html', msg=msg)

@app.route('/contact', methods = ['GET', 'POST'])  
def contact():  
    form=ContactForm()
    mes = ''
    if request.method == "POST":
        if form.validate_on_submit():
            msg = MIMEMultipart()
            message = f"""Сообщение от {form.name}, {form.email}: {form.message}"""
            password = os.environ.get('POST_TOKEN')
            msg['From'] = os.environ.get('MESSAGE_FROM')
            msg['To'] = os.environ.get('MESSAGE_TO')
            msg['Subject'] = "Сообщение от пользователя сайта"
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP_SSL('smtp.mail.ru: 465')
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()
            mes = 'Спасибо! Ваше сообщение отправлено'
        else:
            mes = "Ошибка валидации!"
    return render_template('contact.html', form=form, mes=mes)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
