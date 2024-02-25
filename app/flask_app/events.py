from flask import request
from flask_socketio import emit
from . import socket_io, db
from .routes import current_user
from .models import Users, Messages
from datetime import datetime

@socket_io.on("connect", namespace = "/")
def on_connect_event():
    current_user.last_active = datetime.utcnow()
    current_user.session_id = request.sid
    db.session.commit()

@socket_io.on("disconnect", namespace = "/")
def on_disconnect_event():
    current_user.session_id = None
    db.session.commit()

@socket_io.on("send_message", namespace = "/")
def on_send_message_event(current_friend, message, datetime):
    if len(message) <= 200:
        db.session.add(Messages(
            sender_id = current_user.id,
            receiver_id = Users.query.filter_by(username = current_friend).first().id,
            message = message,
            datetime = datetime
        ))
        db.session.commit()
        emit("message_received", {
            "username": current_user.username,
            "message": message,
            "datetime": datetime
        }, room = (request.sid, Users.query.filter_by(username = current_friend).first().session_id))