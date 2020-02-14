import os

from flask import Flask, flash, jsonify, session, g

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


@app.route('/users/follow/<int:followed_user_id>', methods=['POST'])
def add_follow(followed_user_id):
    """Add a follow for the currently-logged-in user."""

    followed_user = User.query.get_or_404(followed_user_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return jsonify({"id": followed_user_id, "action": "followed"})


@app.route('/users/stop-following/<int:followed_user_id>', methods=['POST'])
def stop_following(followed_user_id):
    """Have currently-logged-in-user stop following this user."""

    followed_user = User.query.get_or_404(followed_user_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return jsonify({"id": followed_user_id, "action": "unfollowed"})


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
        action = "un-retweet"

    else:
        retweet = Retweet(user_id=g.user.id, msg_id=msg_id)
        db.session.add(retweet)
        action = "retweet"

    db.session.commit()

    return jsonify({"msg_id": msg_id, "action": action, "g_user_username": g.user.username})