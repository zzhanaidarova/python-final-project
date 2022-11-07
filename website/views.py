from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Posts, Messages
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required,logout_user, current_user, logout_user
from . import db, socketio
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
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

@login_required
@views.route('/message')
def message():
    data1 = Messages.query.filter_by(to=current_user.username).all()
    data2 = Messages.query.filter_by(by=current_user.username).all()
    data = []
    for da in data1:
        data.append(da.by)
    for da in data2:
        data.append(da.to)
    data = list(dict.fromkeys(data))
    return render_template('message.html', people=data)

@login_required
@views.route('/message-to/to=<string:to>')
def message_to(to):
    exists = User.query.filter_by(username=to).first()
    if exists:
        l1 = Messages.query.filter_by(to=current_user.username).all()
        l2 = Messages.query.filter_by(by=current_user.username).all()
        d = []
        for da in l1:
            d.append(da.by)
        for da in l2:
            d.append(da.to)
        d = list(dict.fromkeys(d))
        
        data1 = Messages.query.filter_by(room=f'{to}-{current_user.username}').all()
        data2 = Messages.query.filter_by(room=f'{current_user.username}-{to}').all()
        data = []
        for da in data1:
            data.append(da)
        for da in data2:
            data.append(da)
        data.sort(key = lambda d:d.id)
        return render_template('message-to.html', to=to, data=data, uname=current_user.username, people=d)
    return redirect(url_for('views.message'))

@socketio.on('join_room')
def handle_loin_room_event(data):
    room = data['room']
    data = room.split('-')
    room2 = f'{data[1]}-{data[0]}'
    join_room(room)
    join_room(room2)
    print('Joined')

@socketio.on('send_message')
def handle_send_message(data):
    room = data['room']
    d = room.split('-')
    room2 = f'{d[1]}-{d[0]}'
    time = data['time']
    time_obj = datetime.strptime(time, '%d-%m-%Y@%H:%M')
    message_data = Messages(room=room, to=d[0], by=d[1], message=data['message'], time=time_obj)
    db.session.add(message_data)
    db.session.commit()
    socketio.emit('receive_message', data, room=(room, room2))