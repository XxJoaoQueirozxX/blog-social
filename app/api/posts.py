from flask import request, g, jsonify, url_for
from .. import db
from . import api
from ..models import Post, Permission
from .decorators import permission_required
from .errors import forbidden
from flask import  current_app


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'location': url_for('api.get_post', id=post.id)}


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page,
        per_page= current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out=False
    )

    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1)

    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1)

    return jsonify(
        {
            "posts": [post.to_json() for post in posts],
            "prev_url": prev,
            "next_url": next,
            "count": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "items_per_page": pagination.per_page
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
