from datetime import datetime
from flask import render_template, flash, redirect, url_for
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
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)



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
    return render_template("user.html", user=user)


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
