from flask import Blueprint, flash, abort, redirect, url_for
from flask import render_template
from app.auth import login_required
from app.models import db, User, UserSubtypeAssociation, UserSubtype, UserType
from datetime import datetime
from app.forms import NewUpdateUserForm, ConfirmActionForm
from sqlalchemy.orm.session import make_transient

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/")
@login_required
def index():
    """Show all users, organized by type."""

    def users_by_type(type):
        users = User.query\
            .with_entities(User.id, User.firstname, User.lastname, User.gender, User.born_on, User.born_in, User.zip, User.city, User.address, User.email1, User.email2, User.tel1, User.tel2, User.notes, UserSubtype.name.label("subtype_name"))\
            .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
            .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
            .join(UserType, UserType.id == UserSubtype.type_id)\
            .filter(UserType.name == type)\
            .all()

        # Change date format
        # for user in users:
        #     if user[3]:
        #         user[3] = datetime.strptime(str(user.born_on), "%Y-%m-%d").strftime("%d/%m/%Y")
        return users


    pc = users_by_type("Protezione Civile")
    alpini = users_by_type("Alpini")
    occasionali = users_by_type("Volontari occasionali")
    non_assicurati = users_by_type("Esterni non assicurati")

    return render_template("users/index.html", pc=pc, alpini=alpini, occasionali=occasionali, non_assicurati=non_assicurati)

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

@bp.route('/<int:user_id>/confirm_deletion', methods=("GET", "POST"))
@login_required
def confirm_deletion(user_id):
    """Confirm the deletion of a user."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    fullname = "{} {}".format(user.firstname, user.lastname)
    form = ConfirmActionForm()
    if form.validate_on_submit():
        # Remove user subtype association
        subtype_assoc = UserSubtypeAssociation.query.filter_by(user_id=user.id).first()
        db.session.delete(subtype_assoc)
        db.session.delete(user)
        db.session.commit()

        flash("Volontario \"{}\" eliminato.".format(fullname), "info")
        return redirect(url_for("users.index"))

    return render_template("confirm_action.html", form=form, active_page="users.index", page_title="Conferma eliminazione volontario", item_name=fullname)

@bp.route('/<int:user_id>/duplicate')
@login_required
def duplicate_user(user_id):
    """Duplicate a user."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    assoc = UserSubtypeAssociation.query.filter_by(user_id=user.id).first()
    old_email = user.email1
    
    # Clone the user with a new id and also his subtype association
    db.session.expunge(user)
    db.session.expunge(assoc)
    make_transient(user)
    make_transient(assoc)
    user.id = None
    user.email1 = old_email + "-copy"
    assoc.id = None
    db.session.add(user)
    db.session.commit()

    assoc.user_id = user.id
    db.session.add(assoc)
    db.session.commit()

    fullname = "{} {}".format(user.firstname, user.lastname)
    flash("Utente \"{}\" duplicato.".format(fullname), "info")

    return redirect(url_for("users.index"))
