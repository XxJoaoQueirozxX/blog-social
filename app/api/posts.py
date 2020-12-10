from flask import request, g, jsonify, url_for
from .. import db
from . import api
from ..models import Post, Permission, Comment
from .decorators import permission_required
from .errors import forbidden


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'location':url_for('api.get_post', id=post.id)}


@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify(
        {
            "posts": [post.to_json() for post in posts]
        }
    )


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/<int:id>', methods=['PUT'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden("Insufficient permissions")
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
