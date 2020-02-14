import os

from flask import Flask, render_template, request, flash, redirect, jsonify, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message, Like, Retweet

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.errorhandler(404)
def page_not_found(e):
    # custom page for 404 error

    return render_template('404.html'), 404

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    flash(f"{g.user.username} has successfully logged out.", "success")
    do_logout()

    return redirect('/login')


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.
    Can take a 'q' param in querystring to search by that username.
    """

    current_url = '/users'
    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html',
                           users=users, current_url=current_url)



@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    current_url = f'/users/{user_id}'
    user = User.query.get_or_404(user_id)

    retweeted_msg_ids = {msg.id for msg in user.messages_retweeted}

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(or_(Message.user_id == user_id, Message.id.in_(retweeted_msg_ids)))
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user,
                           messages=messages, current_url=current_url)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    current_url = f'/users/{user_id}/following'
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html',
                           user=user, current_url=current_url)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    current_url = f'/users/{user_id}/followers'
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html',
                           user=user, current_url=current_url)


@app.route('/users/<int:user_id>/messages-liked')
def users_liked_messages(user_id):
    """Show list of messages liked by this user."""

    current_url = f'/users/{user_id}/messages-liked'

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    
    return render_template('users/liked-messages.html',
                           user=user, current_url=current_url)

@app.route('/users/<int:user_id>/messages-retweeted')
def users_retweeted_messages(user_id):
    """Show list of messages retweeted by this user."""

    current_url = f'/users/{user_id}/messages-retweeted'

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    
    return render_template('users/retweeted-messages.html',
                           user=user, current_url=current_url)


@app.route('/users/follow/<int:followed_user_id>', methods=['POST'])
def add_follow(followed_user_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(followed_user_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return jsonify({"id": followed_user_id, "action": "followed"})


@app.route('/users/stop-following/<int:followed_user_id>', methods=['POST'])
def stop_following(followed_user_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(followed_user_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return jsonify({"id": followed_user_id, "action": "unfollowed"})


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        g.username = form.username.data
        g.email = form.email.data
        g.image_url = form.image_url.data
        g.location = form.location.data
        g.bio = form.bio.data
        g.header_image_url = form.header_image_url.data

        user = User.authenticate(g.user.username, form.password.data)
        if not user:
            flash("Please enter correct user password", "danger")
            return redirect('/users/profile')

        db.session.commit()
        return redirect(f"/users/{g.user.id}")

    return render_template('users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["POST"])
def messages_add():
    msg = Message(text=request.json.text)
    g.user.messages.append(msg)
    db.session.commit()

    return jsonify({"msg_id": msg.id, "g_user_username": g.user.username, "status": "added"})


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)

    if msg.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    current_url = '/'

    if g.user:

        following_ids = {user.id for user in g.user.following}
        following_ids.update({g.user.id})
        retweeted_msg_ids = {msg.id for msg in g.user.messages_retweeted}

        messages = (Message
                    .query
                    .filter(or_(Message.user_id.in_(following_ids), Message.id.in_(retweeted_msg_ids)))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages, current_url=current_url)

    else:
        return render_template('home-anon.html')


##############################################################################
# Like Routes 


@app.route('/messages/<int:msg_id>/toggle-like', methods=["POST"])
def like_message(msg_id):

    liked_msg_ids = {msg.id for msg in g.user.messages_liked}

    if msg_id in liked_msg_ids:
        # way to issue one delete without two queries
        like = Like.query.filter_by(user_id=g.user.id, msg_id=msg_id).first()
        db.session.delete(like)
        action = "unlike"

    else:
        like = Like(user_id=g.user.id, msg_id=msg_id)
        db.session.add(like)
        action = "like"

    db.session.commit()

    return jsonify({"msg_id": msg_id, "action": action, "g_user_username": g.user.username})

@app.route('/messages/<int:msg_id>/toggle-retweet', methods=["POST"])
def retweet_message(msg_id):

    retweeted_msg_ids = {msg.id for msg in g.user.messages_retweeted}

    if msg_id in retweeted_msg_ids:
        # way to issue one delete without two queries
        retweet = Retweet.query.filter_by(user_id=g.user.id, msg_id=msg_id).first()
        db.session.delete(retweet)
        action = "unretweet"

    else:
        retweet = Retweet(user_id=g.user.id, msg_id=msg_id)
        db.session.add(retweet)
        action = "retweet"

    db.session.commit()

    return jsonify({"msg_id": msg_id, "action": action, "g_user_username": g.user.username})

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
