from . import api
from ..models import Comment, Permission, Post
from flask import jsonify, g, request, current_app, url_for
from app.api.decorators import permission_required
from app import db


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.paginate(
        page,
        per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out=False
    )

    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1)

    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1)

    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        "prev_url": prev,
        "next_url": next,
        "count": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
        "items_per_page": pagination.per_page
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.paginate(
        page,
        per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out=False
    )

    comments = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1)

    next = None
    if pagination.has_prev:
        next = url_for('api.get_post_comments', id=id, page=page+1)

    return jsonify(
        {
            "comments": [comment.to_json for comment in comments],
            "prev_url": prev,
            "next_url": next,
            "count": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "items_per_page": pagination.per_page
        }
    )


@api.route('/posts/<int:id>/comments', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_json()), {'location': url_for('api.get_comment', id=comment.id)}
