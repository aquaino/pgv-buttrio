from flask import Blueprint, render_template
from app.auth.views import login_required
from app.models import db, User

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/")
@login_required
def index():
    """Show all the reports."""
    users_count = User.query.count()

    return render_template("reports/index.html", users_count=users_count)
