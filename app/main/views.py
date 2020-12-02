from datetime import datetime
from flask import render_template
from flask_login import login_required
from ..decorators import permission_required, admin_required, Permission
from . import main


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

