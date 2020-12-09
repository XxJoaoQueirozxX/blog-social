from flask import Blueprint


api = Blueprint('api', __name__)

from . import comments, posts, users, authentication,\
    errors
