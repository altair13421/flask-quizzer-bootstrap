from datetime import datetime
from app import app, db
from flask import Response, render_template, redirect, render_template_string, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from app.forms import LoginForm, SignupForm, QuestionForm, AnswerForm, QuizForm, StartTest
from werkzeug.urls import url_parse
from app.models import Users, SubmittedAnswers, Quiz, Questions

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User': Users}

@app.route('/')
@app.route('/index')
def base():
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first() or \
            Users.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_page')
        return redirect(next_page)
    return render_template(
        'form.html', 
        title="Login",
        name_form='Sign In',
        form = form,
    )

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
@login_required
def main_page():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_page'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher_page'))
        elif current_user.is_student():
            return redirect(url_for('student_page'))

# ADMIN
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    if current_user.is_admin():
        return render_template(
            'main.html',
            title = "Home",
            user = current_user,
            option_1 = "Sign Up Student/Teacher",
            link_option_1 = url_for('signup'),
            option_2 = "Stats",
            link_option_2 = url_for('stats')
        )
    return redirect(url_for('main_page'))

@app.route('/admin/signup', methods=["GET", "POST"])
@login_required
def signup():
    if not current_user.is_admin():
        flash('You are Not Admin')
        return redirect(url_for('main_page'))
    form = SignupForm()
    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first() != None or Users.query.filter_by(email=form.email.data).first() != None:
            flash('User Exists, Please Login')
        user = Users(username=f'{form.username.data}', email=f'{form.email.data}', type=f'{form.type_user.data}', name=f'{form.name.data}')
        user.set_password(f'{form.password.data}')
        db.session.add(user)
        db.session.commit()
        flash(f'User {form.username.data} Registered')
    return render_template(
        'form.html',
        name_form="Signup",
        title = "Signup",
        form=form,
    )

@app.route('/admin/stats')
@login_required
def stats():
    users = Users.query.all()
    return render_template(
        'stats.html',
        title = "Stats",
        users=users,
    )

@app.route('/delete/<id>', methods=['GET', "POST"])
@login_required
def delete_user(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("stats"))

# TEACHER
@app.route('/teacher', methods=['GET', 'POST'])
@login_required
def teacher_page():
    if current_user.is_teacher():
        return render_template(
            'main.html',
            title = "Home",
            user = current_user,
            option_1 = "Make Quiz",
            link_option_1 = url_for('quiz_start'),
            option_2 = "About",
            link_option_2 = url_for('about', id=current_user.id)
        )
    return redirect(url_for('main_page'))

@app.route('/teacher/quiz_start', methods=['GET', "POST"])
@login_required
def quiz_start():
    form = QuizForm()
    if form.validate_on_submit():
        quiz_name = form.quiz_name.data
        quiz = Quiz(quiz_name=quiz_name, invigilator=current_user)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for('make_quiz', quiz_id=quiz.id))
    return render_template(
        'card_template.html',
        title = "Set Quiz Name",
        form=form,
    )

@app.route('/teacher/make_quiz/<quiz_id>', methods=['GET', 'POST'])
@login_required
def make_quiz(quiz_id: int):
    form = QuestionForm()
    if form.validate_on_submit():
        data = {
            "quiz": Quiz.query.get(quiz_id),
            "question": form.question.data,
            "answer": form.answer.data,
        }
        if form.next.data:
            add_question(data=data, quiz_id=quiz_id, final=False)
            return redirect(url_for('make_quiz', quiz_id=quiz_id))
        if form.submit.data:
            add_question(data=data, quiz_id=quiz_id, final=True)
            return redirect(url_for('main_page'))
    return render_template(
        'card_template.html',
        title = "Add Questions",
        form=form,
    )

@login_required
def add_question(data: dict, quiz_id:int, final: bool = False):
    question = Questions(
        quiz_name=data['quiz'],
        question=data['question'],
        correct_answer=data['answer'],
    )
    db.session.add(question)
    db.session.commit()
    if not final:
        flash('Question Added')
    else:
        flash('Quiz Added')

@app.route('/teacher/show_quizzes/<id>', methods=['GET', 'POST'])
@login_required
def show_quizzes(id: int):
    quizzes = Quiz.query.filter_by(invigilator=Users.query.get(id))
    return render_template(
        'list_template.html',
        title='Show_quizzes',
        data=quizzes,
    )

@app.route('/teacher/<teacher_id>/show_quizzes/<quiz_id>/questions', methods=['GET', 'POST'])
@login_required
def show_questions(teacher_id, quiz_id):
    user = Users.query.get(teacher_id)
    quiz = Quiz.query.get(quiz_id)
    data = []
    questions = quiz.questions.all()
    for question in questions:
        answers = question.submitted_answers.all()
        if len(answers) != 0:
            for answer in answers:
                item = {
                    "question": question.question,
                    "answer": answer.submittedanswer,
                    "quiz_name": quiz.quiz_name,
                    'invigilator': user.name,
                    'submitted_user': answer.submit_user.name,
                }
                data.append(item)
        item = {
            "question": question.question,
            "answer": f"(P) {question.correct_answer}",
            "quiz_name": quiz.quiz_name,
            "submitted_user": user.name,
            'invigilator': user.name,
        }
        data.append(item)
    return render_template(
        'list_part.html',
        data=data,
    )

# STUDENT
@app.route('/student', methods=['GET', 'POST'])
@login_required
def student_page():
    if current_user.is_student():
        return render_template(
            'main.html',
            user = current_user,
            title = "Home",
            option_1 = "Show Quizzes",
            link_option_1 = url_for('show_quiz'),
            option_2 = "About Me",
            link_option_2 = url_for('about', id=current_user.id)
        )
    return redirect(url_for('main_page'))

@login_required
@app.route('/student/show_quizzes')
def show_quiz():
    quizzes = Quiz.query.all()
    return render_template(
        'list_template.html',
        title = "Quiz",
        data = quizzes
    )

@login_required
@app.route('/student/solved_quizzes/<id>')
def solved_quizzes(id):
    submittedanswers = SubmittedAnswers.query.filter_by(submit_user=Users.query.get(int(id)))
    answers = []
    for item in submittedanswers:
        data = {
            "question": item.submitted_answer.question,
            "answer": item.submittedanswer,
            "quiz_name": item.submitted_answer.quiz_name.quiz_name,
            'invigilator': item.submitted_answer.quiz_name.invigilator.name,
            'submitted_user': item.submit_user.name,
        }
        answers.append(data)
    return render_template(
        'list_part.html',
        data=answers,
    )

@login_required
@app.route('/student/show_quiz/<quiz_id>/start_quiz', methods=['GET', 'POST'])
def start_attempt_quiz(quiz_id:int):
    quiz = Quiz.query.get(quiz_id)
    questions = quiz.questions.all()
    first_id = questions[0].id
    form = StartTest()
    if form.validate_on_submit():
        return redirect(url_for('answer_question', quiz_id=quiz_id, q_id=first_id))
    return render_template(
        'form.html',
        title='Start',
        form=form,
    )

@app.route('/student/show_quiz/<quiz_id>/start_quiz/<q_id>', methods=['GET', 'POST'])
@login_required
def answer_question(quiz_id:int, q_id: int):
    quiz = Quiz.query.get(quiz_id)
    questions = quiz.questions.all()
    if int(q_id) in [x.id for x in questions]:
        form = AnswerForm()
        if form.validate_on_submit():
            if form.next.data:
                add_answer(form.answer.data, q_id, quiz_id)
                flash('Answer Submitted')
                return redirect(url_for('answer_question', quiz_id=quiz_id, q_id=int(q_id)+1))
            if form.submit.data:
                add_answer(form.answer.data, q_id, quiz_id)
                flash('Quiz Submitted, If there were any more Questions in the paper, they are all None Now')
                return redirect(url_for('student_page'))
        return render_template(
            'card_template.html',
            question=Questions.query.get(q_id).question,
            form=form
        )
    else:
        return redirect(url_for('main_page'))

@login_required
def add_answer(answer:str, q_id:int, quiz_id:int):
    subanswer = SubmittedAnswers(
        submittedanswer=answer,
        submit_user=current_user,
        submitted_answer=Questions.query.get(q_id)
    )
    db.session.add(subanswer)
    db.session.commit()
    pass

# Mixed
@app.route('/about/<id>')
@login_required
def about(id):
    user = Users.query.filter_by(id=id).first()
    if id == current_user.id:
        return render_template(
            'about.html',
            title = f"About",
            user=current_user,
        )
    return render_template(
        'about.html',
        title = f"About",
        user=user,
    )

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

# (username - password - type)
# yeager - helpme - admin