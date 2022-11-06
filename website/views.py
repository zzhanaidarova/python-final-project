from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Posts
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required,logout_user, current_user, logout_user
from . import db

views = Blueprint('views', __name__)

@views.route('/mainpage')
def home():
    return render_template("mainpage.html")

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
@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@login_required
@views.route('/create-post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        link = request.form.get('link')
        desc = request.form.get('desc')
        data = Posts(by=current_user.username, link=link, desc=desc)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('views.posts'))
    return render_template('createpost.html')

@login_required
@views.route('/posts')
def posts():
    posts = Posts.query.all()
    return render_template('posts.html', posts=posts[::-1])
