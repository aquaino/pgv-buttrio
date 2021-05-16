import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from app.auth import login_required
from app.models import db, User

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
@login_required
def index():
    """Show all users, organized by type."""
    users = User.query.order_by(User.lastname).all()
    return render_template("users/index.html", users=users)
