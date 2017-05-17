from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import DateTime
from datetime import datetime

from app import db, login_manager


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    allow_email = db.Column(db.Boolean, default=True)
    days_before_email = db.Column(db.Integer, default=3)
    is_doctor = db.Column(db.Boolean, default=True)
    doctor_id = db.Column(db.Integer)
    confirmed_at = db.Column(db.DateTime(), default=datetime.now())

    questionnaires = db.relationship("Questionnaire", backref='users', lazy='dynamic')
    quesanswers = db.relationship("QuesAnswer", backref='users', lazy='dynamic')


    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Questionnaire(db.Model):

    __tablename__ = 'questionnaires'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    description = db.Column(db.Text)
    create_time = db.Column(db.DateTime)
    schema = db.Column(db.PickleType)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    releases = db.relationship("Release", backref='questionnaires', lazy='dynamic')
    quesanswers = db.relationship("QuesAnswer", backref='questionnaires', lazy='dynamic')

    def get_last_release(self):
        releases = list(self.releases)
        if not releases:
            return None
        else:
            return releases[-1]


class Release(db.Model):

    __tablename__ = 'releases'

    id = db.Column(db.Integer, primary_key=True)
    ques_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'))


class QuesAnswer(db.Model):

    __tablename__ = 'ques_answers'

    id = db.Column(db.Integer, primary_key=True)
    ques_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime)

    probanswers = db.relationship("ProbAnswer", backref='ques_answers', lazy='dynamic')


class ProbAnswer(db.Model):

    __tablename__ = 'prob_answers'

    id = db.Column(db.Integer, primary_key=True)
    ques_ans_id = db.Column(db.Integer, db.ForeignKey('ques_answers.id'))
    prob_id = db.Column(db.Integer)
    ans = db.Column(db.Text)
    doctor_id = db.Column(db.Integer)

