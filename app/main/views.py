from datetime import datetime
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..decorators import permission_required, admin_required, Permission
from . import main
from ..models import User, db
from .forms import EditProfileForm

@main.route('/', methods=["GET", "POST"])
def index():
    return render_template("index.html", current_time=datetime.utcnow())


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
    form.about_me = current_user.about_me
    return render_template('edit_profile.html', form=form)
