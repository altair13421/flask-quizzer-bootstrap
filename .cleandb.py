from app import db
from app.models import Questions, SubmittedAnswers, Quiz

for item in Questions.query.all():
    db.session.delete(item)
    db.session.commit()

for item in SubmittedAnswers.query.all():
    db.session.delete(item)
    db.session.commit()

for item in Quiz.query.all():
    db.session.delete(item)
    db.session.commit()