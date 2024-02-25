from . import db
from flask_login import UserMixin
from datetime import datetime

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(30), nullable = False, unique = True)
	email = db.Column(db.String(50), nullable = False, unique = True)
	password = db.Column(db.String(102), nullable = False)
	token = db.Column(db.String(40), nullable = False, unique = True)
	session_id = db.Column(db.String(20))
	last_active = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
	friends = db.relationship("Friends", backref = "users", cascade = "all,delete")
	messages = db.relationship("Messages", backref = "users", cascade = "all,delete")

class Friends(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key = True)
    friend_id = db.Column(db.Integer, primary_key = True)
    
class Messages(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
	receiver_id = db.Column(db.Integer, nullable = False)
	message = db.Column(db.String(200), nullable = False)
	datetime = db.Column(db.String(20), nullable = False)