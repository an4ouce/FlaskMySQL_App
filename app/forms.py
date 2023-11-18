from flask_wtf import FlaskForm
from flask_wtf import RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm): 
    name = StringField('Имя', validators=[DataRequired(message="Пожалуйста, введите имя")])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    message = TextAreaField('Текст сообщения', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Отправить')