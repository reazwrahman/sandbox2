from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


######## Database model to keep track of active game ############
class GameDetails(db.Model):
    __tablename__ = 'gameDetails'
    id = db.Column(db.Integer, primary_key=True)
    game_title = db.Column(db.String) 
    match_id=db.Column(db.BigInteger,unique=True,index=True)
    game_status=db.Column(db.String) 
    squad_link=db.Column(db.String,unique=True)  
    scorecard_link=db.Column(db.String)  
    points_per_run=db.Column(db.Float) 
    points_per_wicket=db.Column(db.Float)
    ## TODO
    #game_start_time : DateTime type from sqlAlchemy
    

    def __repr__(self):
        return '<GameDetails %r>' % self.match_id 


### Database model to store fantasy squad selection for each user ##### 
class SelectedSquad(db.Model): 
    __tablename__ = 'selectedSquad'
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    match_id = db.Column(db.BigInteger,index=True) 
    selected_squad=db.Column(db.String) 
    captain= db.Column(db.String)  
    vice_captain= db.Column(db.String) 
