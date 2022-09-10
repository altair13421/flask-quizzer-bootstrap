from app import db
from app.models import Questions, SubmittedAnswers, Quiz

print("Questions")
for item in Questions.query.all():
    print(item.id)
    print(item.quiz_name)
    print(item.question)
    print(item.correct_answer)
    
print()
print('Submitted Answers')
for item in SubmittedAnswers.query.all():
    print(item.submittedanswer)
    print(item.submitted_answer.question)
    print(item.submit_user.username)

print()
print("quizzes")
for item in Quiz.query.all():
    print(item.id)
    print(item.quiz_name)