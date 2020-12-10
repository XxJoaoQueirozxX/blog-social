from . import api
from ..models import User
from flask import jsonify


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'posts': [ post.to_json() for post in user.posts]
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'timeline_posts': [post.to_json() for post in user.followed_posts]
    })
