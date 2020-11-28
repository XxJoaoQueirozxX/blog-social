from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment


from datetime import datetime

from form import NameForm


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)


app.config["SECRET_KEY"] = "A secret key"


@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get("name")
        if (old_name is not None) and (old_name != form.name.data):
            flash("Looks like you have changed your name! ")
        session["name"] = form.name.data
        return redirect(url_for('index'))
    return render_template(
        "index.html",
        current_time=datetime.utcnow(),
        form=form,
        name=session.get('name')
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


if __name__ == '__main__':
    print("Iniciando.......")
    app.run(debug=True)
