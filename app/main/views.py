from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user
from ..decorators import permission_required, admin_required, Permission
from . import main
from ..models import User, db, Role, Post
from .forms import EditProfileForm, EditProfileAdminForm, PostForm


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

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
        error_out=False
    )

    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)



@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/admin')
@login_required
@admin_required
def admin():
    return "For admins only"


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    return "For moderate only"


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


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", posts=[post])


@main.route('/edit/<int:id>', methods=['GEt', 'POST'])
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
    user = User.query.filter_by(username=username).fiest_or_404()

    paginate = user.followers.paginate()
    return render_template("followers.html", paginate=paginate)


@main.route('/followed_by/<username>')
def followed_by(username):
    pass
