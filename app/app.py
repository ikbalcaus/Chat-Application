from flask_app import app, socket_io, db
import flask_app.models
import flask_app.routes
import flask_app.events
import os

if __name__ == "__main__":
	with app.app_context():
		if not os.path.isfile("instance/database.sqlite3"):
			db.create_all()
	socket_io.run(app, host = "0.0.0.0", port = 5000, allow_unsafe_werkzeug = True)