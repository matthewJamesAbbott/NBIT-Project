from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

# create flask application, set key for communications with database and set database type and address
def create_app():
    app = Flask(__name__) # instantiate flask object
    app.config['SECRET_KEY'] = 'Th0zeWhoEatz@{h!ll!' # set flask objects key for communications
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # set flasks database type and url
    db.init_app(app) # initialise database passing it the flask object for linkage

    from .views import views
    from .auth import auth

    # register views and the authentication objects to the main blueprints root url
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Receipt
    
    # create database
    with app.app_context():
        db.create_all()

    # create user database
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # function for returning user objects from database
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# create database in flask app
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
