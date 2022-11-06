from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def createapp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super secret secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    loginmanager = LoginManager(app)
    loginmanager.login_view = '/'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    from .models import User
    createDatabase(app)

    @loginmanager.user_loader
    def userloader(id):
        return User.query.filter_by(id=int(id)).first()

    with app.app_context():
        db.create_all()

    return app

def createDatabase(app):
    if not path.exists("website/database.db"):
        db.create_all(app=app)
        print('DB created')