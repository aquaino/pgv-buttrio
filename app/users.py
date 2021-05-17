from flask import Blueprint
from flask import render_template
from app.auth import login_required
from app.models import User

bp = Blueprint("users", __name__, url_prefix="/users")

# TODO: setup user types queries

@bp.route("/")
@login_required
def index():
    """Show all users, organized by type."""
    users = User.query.order_by(User.lastname).all()
    return render_template("users/index.html", users=users)
