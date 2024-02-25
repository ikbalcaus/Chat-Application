from flask import render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from . import app, db, app_url, mail, load_user, email_regex, password_regex
from .models import Users, Friends, Messages
from re import fullmatch
from secrets import token_hex

@app.route("/", methods = ("GET", "POST"))
@login_required
def index_route():
    friends = Users.query.filter(
        Friends.user_id == current_user.id,
        Friends.friend_id == Users.id
    ).order_by(Users.last_active.desc())
    if request.method == "POST":
        current_friend = Users.query.filter_by(username = request.form.get("username")).first()
        if current_friend:
            return render_template("index.html",
                current_user = current_user.username,
                current_friend = current_friend.username,
                friends = friends.all(),
                messages = Messages.query.filter(
                    db.or_(
                        db.and_(
                            Messages.sender_id == current_user.id,
                            Messages.receiver_id == current_friend.id
                        ),
                        db.and_(
                            Messages.sender_id == current_friend.id,
                            Messages.receiver_id == current_user.id
                        )
                    )
                ).all()
            )
    if not friends.first():
        return redirect("/manage-friends")
    current_friend = friends.first()
    return render_template("index.html",    
        current_user = current_user.username,
        current_friend = current_friend.username,
        friends = friends.all(),
        messages = Messages.query.filter(
            db.or_(
                db.and_(
                    Messages.sender_id == current_user.id,
                    Messages.receiver_id == current_friend.id
                ),
                db.and_(
                    Messages.sender_id == current_friend.id,
                    Messages.receiver_id == current_user.id
                )
            )
        ).all()
    )

@app.route("/signup", methods = ("GET", "POST"))
def signup_route():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        if Users.query.filter_by(username = username).first():
            flash("Somebody use this username", "danger")
            return redirect("/signup")
        if Users.query.filter_by(email = email).first():
            flash("Somebody use this email", "danger")
            return redirect("/signup")
        if password != request.form.get("confirm-password"):
            flash("Passwords are not the same", "danger")
            return redirect("/signup")
        if(
            len(username) == 0 or len(username) > 30 or
            len(email) > 50 or not fullmatch(email_regex, email) or
            not fullmatch(password_regex, password)
        ):
            flash("Data do not match validation rules", "danger")
            return redirect("/signup")
        user = Users(
            username = username,
            email = email,
            password = generate_password_hash(password),
            token = token_hex(20)
        )
        db.session.add(user)
        db.session.commit()
        if request.form.get("remember"):
            login_user(user, remember = True)
        else:
            login_user(user, remember = False)
        return redirect("/")
    return render_template("signup.html",
        password_regex = password_regex
    )

@app.route("/login", methods = ("GET", "POST"))
def login_route():
    if request.method == "POST":
        user = Users.query.filter_by(email = request.form.get("email")).first()
        if not user:
            flash("Incorrect email", "danger")
            return redirect("/login")
        if not check_password_hash(user.password, request.form.get("password")):
            flash("Incorrect password", "danger")
            return redirect("/login")
        if request.form.get("remember"):
            login_user(user, remember = True)
        else:
            login_user(user, remember = False)
        return redirect("/")
    return render_template("login.html",
        password_regex = password_regex
    )

@app.route("/manage-friends")
@login_required
def manage_friends_route():
    if request.args.get("username"):
        return render_template("manage-friends.html",
            is_current_manage_friends = True,
            friends = Users.query.filter(
                Users.username.contains(request.args.get("username")),
                Users.id == Friends.user_id,
                Users.id != current_user.id
            ).order_by(Users.last_active.desc()).all(),
            not_friends = [user for user in Users.query.filter(
                Users.username.contains(request.args.get("username")),
                Users.id != current_user.id
            ).all() if user not in Users.query.filter(
                Friends.user_id == current_user.id,
                Friends.friend_id == Users.id
            ).order_by(Users.last_active.desc()).all()]
        )
    return render_template("manage-friends.html",
        is_current_manage_friends = True,
        friends = Users.query.filter(
            Friends.user_id == current_user.id,
            Friends.friend_id == Users.id
        ).order_by(Users.last_active.desc()).all(),
        not_friends = [user for user in Users.query.filter(Users.id != current_user.id).all() if user not in Users.query.filter(
            Friends.user_id == current_user.id,
            Friends.friend_id == Users.id
        ).order_by(Users.last_active.desc()).all()]
    )

@app.route("/manage-friends/add", methods = ("GET", "POST"))
@login_required
def manage_friends_add_route():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            db.session.add(Friends(
                user_id = current_user.id,
                friend_id = Users.query.filter_by(username = username).first().id
            ))
            db.session.add(Friends(
                user_id = Users.query.filter_by(username = username).first().id,
                friend_id = current_user.id
            ))
            db.session.commit()
        except:
            pass
    return redirect("/manage-friends")

@app.route("/manage-friends/remove", methods = ("GET", "POST"))
@login_required
def manage_friends_remove_route():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            db.session.delete(Friends.query.filter_by(
                user_id = current_user.id,
                friend_id = Users.query.filter_by(username = username).first().id
            ).first())
            db.session.delete(Friends.query.filter_by(
                user_id = Users.query.filter_by(username = username).first().id,
                friend_id = current_user.id
            ).first())
            db.session.commit()
        except:
            pass
    return redirect("/manage-friends")

@app.route("/settings", methods = ("GET", "POST"))
@login_required
def settings_route():
    if request.method == "POST":
        new_username = request.form.get("new-username").strip()
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")
        if not check_password_hash(current_user.password, old_password):
            flash("Incorrect old password", "danger")
            return redirect("/settings")
        if(
            new_username and
            Users.query.filter_by(username = new_username).first()
        ):
            flash("Somebody use this username", "danger")
            return redirect("/settings")
        if new_password != request.form.get("confirm-new-password"):
            flash("New passwords are not the same", "danger")
            return redirect("/settings")
        if(
            len(new_username) > 30 or
            (len(new_password) != 0 and not fullmatch(password_regex, new_password))
        ):
            flash("Data do not match validation rules", "danger")
            return redirect("/settings")
        user = current_user
        if len(new_username) != 0:
            user.username = new_username
        if len(new_password) != 0:
            user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Your data are successfully updated", "success")
        return redirect("/settings")
    return render_template("settings.html",
        password_regex = password_regex,
        is_current_settings = True,
        friends = Users.query.filter(
            Friends.user_id == current_user.id,
            Friends.friend_id == Users.id
        ).order_by(Users.last_active.desc()).all(),
    )

@app.route("/logout")
@login_required
def logout_route():
    logout_user()
    return redirect("/login")

@app.route("/delete-account", methods = ("GET", "POST"))
@login_required
def delete_account_route():
    if request.method == "POST":
        if not check_password_hash(current_user.password, request.form.get("password")):
            flash("Incorrect old password", "danger")
            return redirect("/settings")
        db.session.delete(current_user)
        [db.session.delete(friend) for friend in Friends.query.filter_by(friend_id = current_user.id).all()]
        [db.session.delete(message) for message in Messages.query.filter_by(receiver_id = current_user.id).all()]
        db.session.commit()
        flash("Your account is successfully deleted", "success")
        return redirect("/login")
    return redirect("/settings")

@app.route("/forgot-password", methods = ("GET", "POST"))
def forgot_password_route():
    if not app.config["MAIL_USERNAME"] or not app.config["MAIL_PASSWORD"]:
        flash("This option is disabled by admin", "danger")
        return redirect("/login")
    if request.method == "POST":
        user = Users.query.filter_by(email = request.form.get("email")).first()
        if not user:
            flash("Incorrect email", "danger")
            return redirect("/login")
        msg = Message("Password reset", recipients = [user.email])
        msg.body = "To reset your password, please click the link below.\n\n" + app_url + "/reset-password/" + user.token
        mail.send(msg)
        flash("Please check your email address", "success")
    return render_template("forgot-password.html")

@app.route("/reset-password/<token>", methods = ("GET", "POST"))
def reset_password_route(token):
    user = Users.query.filter_by(token = token).first()
    if request.method == "POST":
        new_password = request.form.get("new-password")
        if new_password != request.form.get("confirm-new-password"):
            flash("Passwords are not the same", "danger")
            return redirect("/reset-password/" + token)
        user.password = generate_password_hash(new_password)
        user.token = token_hex(20)
        db.session.commit()
        login_user(user)
        flash("Your password is successfully updated", "success")
        return redirect("/")
    if user:
        return render_template("reset-password.html",
            token = token
        )
    return redirect("/login")

@app.errorhandler(401)
def unauthorized_route(error):
    return redirect("/login")