from flask import Blueprint
from flask import render_template
from app.auth import login_required
from app.models import User
from datetime import datetime

bp = Blueprint("users", __name__, url_prefix="/users")

# TODO: setup user types queries

@bp.route("/")
@login_required
def index():
    """Show all users, organized by type."""
    users = User.query.order_by(User.lastname).all()
    # Change dates format
    for user in users:
        if user.born_on:
            user.born_on = datetime.strptime(str(user.born_on), "%Y-%m-%d").strftime("%d/%m/%Y")
    return render_template("users/index.html", users=users)
