CREATE USER 'mysql'@'localhost' IDENTIFIED WITH mysql_native_password BY 'mysql';

CREATE DATABASE IF NOT EXISTS FLASK DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

GRANT ALL PRIVILEGES ON FLASK.* TO 'mysql'@'localhost';

FLUSH PRIVILEGES;

USE FLASK;

CREATE TABLE IF NOT EXISTS users (
    id int(11) NOT NULL AUTO_INCREMENT,
    username varchar(50) NOT NULL,
    email varchar(100) NOT NULL,
    pwd_with_salt varchar(255) NOT NULL,
    salt blob NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


