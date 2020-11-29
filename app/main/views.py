from datetime import datetime
from flask import render_template, redirect, session, url_for
from . import  main
from ..models import User
from .. import db
from .forms import NameForm


@main.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            # if app.config["FLASK_ADMIN"]:
            #     send_email(app.config["FLASK_ADMIN"], "New User", "mail/new_user", user=user)
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template(
        "index.html",
        current_time=datetime.utcnow(),
        form=form,
        name=session.get('name'),
        known=session.get("known", False)
    )
