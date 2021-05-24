import functools
from flask import Blueprint
from flask import render_template
from app.auth.views import login_required

bp = Blueprint("activities", __name__)

@bp.route("/")
@login_required
def index():
    """Show recent activities."""
    return render_template("activities/index.html")
