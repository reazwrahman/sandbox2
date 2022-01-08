from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth') 

    from .gameSetup import gameSetup as gameSetup_blueprint
    app.register_blueprint(gameSetup_blueprint, url_prefix='/gameSetup') 

    from .squadSelection import squadSelection as squadSelection_blueprint
    app.register_blueprint(squadSelection_blueprint, url_prefix='/squadSelection') 

    from .fantasyContest import fantasyContest as fantasyContest_blueprint
    app.register_blueprint(fantasyContest_blueprint, url_prefix='/fantasyContest')


    return app
