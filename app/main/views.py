from flask import render_template, flash, redirect, url_for, request, current_app, abort, make_response
from flask_login import login_required, current_user
from ..decorators import permission_required, admin_required, Permission
from . import main
from ..models import User, db, Role, Post, Comment
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm


@main.route('/', methods=["GET", "POST"])
def index():
    form = PostForm()

    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(
            body=form.body.data,
            author=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)




    show_followed = False

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out=False
    )

    posts = pagination.items
    return render_template(
        'index.html',
        form=form,
        posts=posts,
        show_followed=show_followed,
        pagination=pagination
    )


@main.route("/all")
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route("/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out=False
    )

    posts = pagination.items

    return render_template("user.html", user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.username = form.username.data
        user.email = form.email.data
        user.about_me = form.about_me.data
        user.location = form.location.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("Profile has been updated.")
        return redirect(url_for('.user', username=user.username))

    form.name.data = user.name
    form.username.data = user.username
    form.email.data = user.email
    form.about_me.data = user.about_me
    form.location.data = user.location
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id

    return render_template("edit_profile.html", form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object()
        )

        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() -1) // current_app.config["FLASKY_COMMENTS_PER_PAGE"] + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out=False
    )
    comments = pagination.items

    return render_template(
        "post.html",
        posts=[post],
        form=form,
        pagination=pagination,
        comments=comments
    )


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("The post has been updated.")
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash("You already following this user.")
    else:
        current_user.follow(user)
        db.session.commit()
        flash(f"You are following {username}")
    return redirect(url_for('.user', username=username))


@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user != user:
        current_user.unfollow(user)
        db.session.commit()
    return redirect(url_for('.user', username=user.username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    paginate = user.followers.paginate(
        page,
        per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in paginate.items]
    return render_template(
        "followers.html",
        user=user,
        title="Followers of",
        endpoint='.followers',
        paginations=paginate,
        follows=follows
    )


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    paginate = user.followed.paginate(
        page,
        per_page=current_app.config["FLASKY_FOLLOWED_PER_PAGE"],
        error_out=False
    )
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in paginate.items]
    return render_template(
        "followers.html",
        user=user,
        title="Followed by",
        endpoint='.followed_by',
        pagination=paginate,
        follows=follows
    )


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)

    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out=False
    )

    comments = pagination.items
    return render_template("moderate.html", comments=comments, page=page, pagination=pagination)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(
        url_for(
            '.moderate',
            page=request.args.get('page', 1, type=int)
        )
    )


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(
        url_for(
            '.moderate',
            page=request.args.get('page', 1, type=int)
        )
    )
