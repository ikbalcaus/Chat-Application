from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(
	__name__,
	template_folder = "../templates",
	static_folder = "../static"
)
app.config["SECRET_KEY"] = "O6nvNyL75LIc6lbpTXJ3O6nvNyL75LIc6lbpTXJ4"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

#------------------------------------ DATA TO MODIFY ------------------------------------
"""
    Create google account.
    Enable 2-Step Verification.
    Go to "https://myaccount.google.com/apppasswords"
    Create app password for this application
    Set your email below
    Set your APP PASSWORD below (not your email password)
"""
app_url = "http://localhost:5000"
app.config["MAIL_USERNAME"] = "" #set EMAIL
app.config["MAIL_PASSWORD"] = "" #set APP PASSWORD (not email password)
app.config["MAIL_DEFAULT_SENDER"] = "noreply@chat-app.com"
#----------------------------------------------------------------------------------------

db = SQLAlchemy(app)
socket_io = SocketIO(app)
login_manager = LoginManager(app)
mail = Mail(app)

from .models import Users
@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)

email_regex = "^[a-zA-Z0-9-_\.]+@([a-zA-Z0-9-_\.])+\.[a-zA-Z0-9]+$"
password_regex = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).{8,}$"