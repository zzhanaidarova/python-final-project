from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required,logout_user, current_user, logout_user
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>Main Page</h1>"

@views.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
        else:
            print('Username does not exist')

    return render_template("login.html")

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(username=username).first()
        if user:
            print('Username is already exists.')
        elif password1 != password2:
            print('Passwords do not match')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            print('Your account created')
            return redirect(url_for('views.home'))
    return render_template("register.html")

@login_required
@views.route('posts')
def posts():
    return "<h1>Posts Page</h1>"

@login_required
@views.route('logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

