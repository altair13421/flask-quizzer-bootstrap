from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from app.models import Users

# Forms Here
class LoginForm(FlaskForm):
    username = StringField('Username Or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Submit")
    pass

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_re = PasswordField('Re enter Password', validators=[DataRequired(), EqualTo('password')])
    type_user = StringField('User_type', validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please Use a Different Username. Username Already Exists')
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please Use a Different Email. Email Already Exists')
    
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Please Use a Stronger Password (min length: 8)')
    
    def validate_type_user(self, type_user):
        if type_user.data not in ('teacher', 'student'):
            raise ValidationError('Type Can Be Either "teacher", or "student"')

class QuizForm(FlaskForm):
    quiz_name = StringField('Quiz Name', validators=[DataRequired()])
    submit = SubmitField("Start")

class QuestionForm(FlaskForm):
    question = StringField('Enter Question', validators=[DataRequired()])
    answer = StringField('Enter Preferable Answer')
    next = SubmitField('Next')
    submit = SubmitField("Done")

class AnswerForm(FlaskForm):
    answer = StringField('Enter Answer', validators=[DataRequired()])
    next = SubmitField('Next')
    submit = SubmitField('Done')

class StartTest(FlaskForm):
    submit = SubmitField('Start')