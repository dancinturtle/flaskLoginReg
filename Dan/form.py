from flask_wtf import Form
from wtforms import validators, StringField, PasswordField, TextAreaField
from wtforms.fields.html5 import EmailField

class RegisterForm(Form):
    firstname = StringField('First Name', [
    validators.Required(),
    validators.Length(min=2, max=255)
    ])
    lastname = StringField('Last Name', [
    validators.Required(),
    validators.Length(min=2, max=255)
    ])
    email = EmailField('Email', [validators.Required()])
    password = PasswordField('New Password',[
    validators.Required(),
    validators.EqualTo('confirm', message='Passwords must match'),
    validators.Length(min=2, max=255)
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    email = EmailField('Email', [validators.Required()])
    password = PasswordField('Password',[
    validators.Required(),
    validators.Length(min=2, max=255)
    ])
