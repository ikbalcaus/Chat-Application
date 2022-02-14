from flask import *
import flask_socketio, flask_sqlalchemy, socket, os


app = Flask(__name__)
app.config["SECRET_KEY"] = "OkyfqGSFgskbzDbBwsmbyaALmQ88FpVn6jKgaNtX"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///messages.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = flask_sqlalchemy.SQLAlchemy(app)
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*")


class table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(30), nullable=False)
    nickname = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(22), nullable=False)
    message = db.Column(db.String(200), nullable=False)
	

@socketio.on("message")
def handleMessage(data):
	db.session.add(table(
		room = data.split("|")[0],
		nickname = data.split("|")[1],
		date = data.split("|")[2],
		message = data[getMessage(data):]
	))
	db.session.commit()
	flask_socketio.send(data, broadcast=True)


@app.route("/", methods=("GET", "POST"))
def indexRoute():
	if request.form.get("nickname") and request.form.get("room"):
		if len(request.form.get("nickname")) > 30:
			return render_template("index.html")
		return redirect("/" + request.form.get("room")), 307
	return render_template("index.html")
	

@app.route("/<room>", methods=("GET", "POST"))
def roomRoute(room):
	if request.method == "POST":
		return render_template("room.html",
			nickname = request.form.get("nickname"),
			room = room,
			database = table.query.filter_by(room = room).all(),
			ipAdrress = socket.gethostbyname(socket.gethostname())
		)
	return redirect("/")


def getMessage(str):
	numOfChars = 0
	for i, char in enumerate(str):
		if char == "|":
			numOfChars += 1
			if (numOfChars == 3):
				return i + 1


if __name__ == "__main__":
	if not os.path.isfile("messages.sqlite3"):
		db.create_all()
	print(socket.gethostbyname(socket.gethostname()))
	socketio.run(app, host="0.0.0.0", port=80)
