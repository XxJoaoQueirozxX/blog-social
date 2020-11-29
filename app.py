from datetime import datetime
from threading import Thread
import os

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate
from flask_mail import Mail, Message
from dotenv import load_dotenv

from db import db
from form import NameForm
from models import User, Role

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = "A secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["FLASKY_MAIL_SUBJECT_PREFIX"] = '[Flasky] '
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
app.config["FLASK_ADMIN"] = os.getenv("FLASK_ADMIN")

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("USER_EMAIL")
app.config["MAIL_PASSWORD"] = os.environ.get("USER_PASSWORD")

bootstrap = Bootstrap(app)
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(
        app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,
        sender=app.config["FLASKY_MAIL_SENDER"],
        recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr




@app.before_first_request
def gerar_banco():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            if app.config["FLASK_ADMIN"]:
                send_email(app.config["FLASK_ADMIN"], "New User", "mail/new_user", user=user)
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template(
        "index.html",
        current_time=datetime.utcnow(),
        form=form,
        name=session.get('name'),
        known=session.get("known", False)
    )


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


if __name__ == '__main__':
    app.run(debug=True)
