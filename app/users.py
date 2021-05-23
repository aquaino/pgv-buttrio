from flask import Blueprint
from flask import render_template
from app.auth import login_required
from app.models import User
from datetime import datetime
from app.forms import NewUpdateUserForm

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

@bp.route("/new-user", methods=("GET", "POST"))
@login_required
def new_user():
    """Create a new user."""
    form = NewUpdateUserForm()
    # Flatten the query result to a list of tuples (id, name)
    # This way the option values of the select field in the form are the GB categories ids
    # form.gb_category.choices = [(row.id, row.name) for row in GreenBookCategory.query.with_entities(GreenBookCategory.id, GreenBookCategory.name)]

    if form.validate_on_submit():
        user = User()
        db.session.add(user)
        db.session.commit()

        flash("Utente \"{} {}\" aggiunto.".format(user.firstname, user.lastname), "info")
        return redirect(url_for("users.new_user", action="new"))

    return render_template("users/new_update_user.html", form=form, action="new")
