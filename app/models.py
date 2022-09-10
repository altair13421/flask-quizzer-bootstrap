from datetime import datetime
from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(64), index=True)
    type = db.Column(db.String(32), index=True)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.now())
    quizzes = db.relationship('Quiz', backref='invigilator', lazy='dynamic')
    submissions = db.relationship('SubmittedAnswers', backref='submit_user', lazy='dynamic')

    @login.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    def set_password(self, passwordtoset):
        self.password = generate_password_hash(passwordtoset)
    
    def check_password(self, passwordtocheck):
        return check_password_hash(self.password, passwordtocheck)

    def __repr__(self) -> str:
        return f'<User {self.username} || Type {self.type}>'
    
    def is_admin(self) -> bool:
        return self.type == "admin"

    def is_student(self) -> bool:
        return self.type == 'student'
    
    def is_teacher(self) -> bool:
        return self.type == 'teacher'

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(64), index=True)
    quiz_writer = db.Column(db.Integer, db.ForeignKey("users.id"))
    questions = db.relationship('Questions', backref='quiz_name', lazy='dynamic')

    def __repr__(self) -> str:
        return f"<Quiz {self.quiz_name} || By {self.quiz_writer}>"

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(128), index = True)
    correct_answer = db.Column(db.String(128), index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    submitted_answers = db.relationship('SubmittedAnswers', backref='submitted_answer', lazy='dynamic')

    def __repr__(self) -> str:
        return f"<Question {self.question}>"

class SubmittedAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submittedanswer = db.Column(db.String(64), index=True)
    submitted_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    def __repr__(self) -> str:
        return f"<Answer {self.submittedanswer} || Question Id {self.question_id} || by {self.submitted_user}>"
