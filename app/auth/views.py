import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from app.models import db, User
from app.auth.forms import LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            User.query.filter_by(id=user_id).first()
        )

@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in an admin user by adding the user id to the session."""
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        error = None
        user = User.query.filter_by(email1=email).first()

        if user is None:
            error = "Indirizzo email non presente."
        elif not check_password_hash(user.password, password):
            error = "Password sbagliata."
        elif user.admin is False:
            error = "Non sei un amministratore."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error, "error")

    return render_template("auth/login.html", form=form);


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("activities.index"))
