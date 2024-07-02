import os
from controllers import UserController, DiaryController, ChatController, AnalysisController
from models import db
from flask import Flask
from flask import render_template, request, redirect, url_for, abort
from functools import wraps

from flask_login import LoginManager, login_required, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary_app.db'
app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loginPage'

db.init_app(app)
with app.app_context():
    db.create_all()

userController = UserController()
diaryController = DiaryController()
chatController = ChatController()
analysisController = AnalysisController()

def diary_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        diary_id = kwargs.get('diary_id', None)
        if not diaryController.is_diary_owner(diary_id, current_user.id):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return userController.user_load_control(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('loginPage'))

@app.route("/")
@login_required
def indexPage():
    username = current_user.username
    return render_template('index.html', username=username)

@app.route("/signup", methods=['GET', 'POST'])
def signUpPage():
    if request.method == 'GET':
        return render_template('sign_up.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userController.sign_up(username, password)

        return redirect(url_for('loginPage'))

@app.route("/login", methods=['GET', 'POST'])
def loginPage():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if userController.login(username, password):
            return redirect(url_for('indexPage'))
        else:
            return 'Invalid username or password'

@app.route("/logout")
@login_required
def logout():
    userController.logout()
    return redirect(url_for('loginPage'))


        

@app.route("/create_diary", methods=['GET', 'POST'])
@login_required
def createDiaryPage():
    if request.method == 'GET':
        return render_template('create_diary.html')
    
    if request.method == 'POST':
        body = request.form['body']

        if len(body) == 0:
            return 'body needs strings.'
        else:    
            diaryController.create_diary(current_user.id, body)
     
        return redirect(url_for('diariesPage'))

# DiaryController
@app.route("/diaries")
@login_required
def diariesPage():
    diaries = diaryController.get_user_diaries(current_user.id)
    return render_template('diaries.html', diaries=diaries)

@app.route("/diaries/<int:diary_id>")
@login_required
@diary_owner_required
def diaryPage(diary_id):
    diary = diaryController.get_diary(diary_id)
    return render_template('diary.html', diary=diary)

@app.route("/diaries/<int:diary_id>/edit", methods=['GET', 'POST'])
@login_required
@diary_owner_required
def editDiaryPage(diary_id):
    if request.method == 'GET':
        diary = diaryController.get_diary(diary_id)
        return render_template('edit_diary.html', diary=diary)
    
    if request.method == 'POST':
        new_body = request.form['body']

        if len(new_body) == 0:
            return 'body needs strings.'
        else:
            diaryController.edit_diary(diary_id, new_body)
            return redirect(url_for('diariesPage'))

@app.route("/diaries/<int:diary_id>/delete")
@login_required
@diary_owner_required
def deleteDiary(diary_id):
    diaryController.delete_diary(diary_id)
    return redirect(url_for('diariesPage'))

# ChatController
@app.route("/chat")
@login_required
def chatPage():
    return render_template('chat.html')

# AnalysisController
@app.route("/analysis")
@login_required
def analysisPage():
    return render_template('analysis.html')


if __name__ == ('__main__'):
    app.run(debug=True)