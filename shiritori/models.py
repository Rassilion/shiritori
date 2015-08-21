from shiritori import db
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
import datetime

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    username = db.Column(db.String(60), unique=True)
    token = db.Column(db.String(255), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    time_registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    bio = db.Column(db.UnicodeText)
    avatar = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    roles = db.relationship(
        'Role', secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'))

    def __unicode__(self):
        return self.username


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True)
    p1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    p2 = db.Column(db.Integer, db.ForeignKey('user.id'))
    dict = db.Column(db.String(2))
    mode = db.Column(db.String(64))
    p1_words = db.Column(db.String)
    p2_words = db.Column(db.String)
    p1_score = db.Column(db.Integer)
    p2_score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    length = db.Column(db.Integer)

    def __unicode__(self):
        return self.uuid


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
