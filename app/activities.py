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


bp = Blueprint("activities", __name__)


@bp.route("/")
@login_required
def index():
    """Show recent activities."""
    return render_template("activities/index.html")
