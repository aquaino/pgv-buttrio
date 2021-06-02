from flask import Blueprint, flash, abort, redirect, url_for, render_template, request
from app.auth.views import login_required
from app.models import db, User, UserSubtypeAssociation, UserSubtype, UserType
from datetime import datetime
from app.users.forms import NewUserForm, ConfirmUserDeletionForm, UpdateUserForm
from sqlalchemy.orm.session import make_transient
import random

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/")
@login_required
def index():
    """Show all users, organized by type."""

    def users_by_type(type_name):
        """General query structure for different type of users."""
        users = User.query\
            .with_entities(User.id, User.firstname, User.lastname, User.gender, User.born_on, User.born_in, User.zip, User.city, User.address, User.email1, User.email2, User.tel1, User.tel2, User.notes, UserSubtype.name.label("subtype_name"), UserSubtype.id.label("subtype_id"))\
            .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
            .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
            .join(UserType, UserType.id == UserSubtype.type_id)\
            .filter(UserType.name == type_name)\
            .order_by(User.lastname)\
            .all()

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
    subtype_choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    form = NewUserForm(subtype=[subtype_choices[0][0]])
    form.gender.choices = ["Non specificato", "Uomo", "Donna"]
    form.subtype.choices = subtype_choices
    form.subtype.default = [1]

    if form.validate_on_submit():
        # Create the user
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, gender=form.gender.data, born_on=form.born_on.data, born_in=form.born_in.data, zip=form.zip.data, city=form.city.data, address=form.address.data, email1=form.email1.data, email2=form.email2.data, tel1=form.tel1.data, tel2=form.tel2.data, notes=form.notes.data)
        db.session.add(user)
        db.session.commit()

        # Set user's subtype/s
        for subtype_id in form.subtype.data:
            assoc = UserSubtypeAssociation(user_id=user.id, subtype_id=subtype_id)
            db.session.add(assoc)

        db.session.commit()

        flash("Utente \"{} {}\" aggiunto.".format(user.firstname, user.lastname), "info")
        return redirect(url_for("users.new_user", action="new"))

    return render_template("users/new_update_user.html", form=form, action="new")

@bp.route('/<int:user_id>/delete', methods=("GET", "POST"))
@login_required
def delete_user(user_id):
    """Confirm the deletion of a user."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    fullname = "{} {}".format(user.firstname, user.lastname)
    form = ConfirmUserDeletionForm(subtype=[int(request.args.get("subtype_id"))])

    subtype_choices = UserSubtypeAssociation.query\
        .with_entities(UserSubtype.id, UserSubtype.name)\
        .join(UserSubtypeAssociation, UserSubtypeAssociation.subtype_id == UserSubtype.id)\
        .filter(UserSubtypeAssociation.user_id==user_id)\
        .all()
    form.subtype.choices = [(row.id, row.name) for row in subtype_choices]

    if form.validate_on_submit():
        # Remove specified user subtype association/s
        for subtype_id in form.subtype.data:
            assoc = UserSubtypeAssociation.query.filter_by(user_id=user_id, subtype_id=subtype_id).first()
            db.session.delete(assoc)

        # If all the subtypes were selected, remove also the user
        removed_from_all = False
        if len(form.subtype.data) == len(form.subtype.choices):
            db.session.delete(user)
            removed_from_all = True

        db.session.commit()

        if removed_from_all:
            flash("Volontario \"{}\" rimosso dal sistema.".format(fullname), "info")
        else:
            flash("Volontario \"{}\" eliminato dai gruppi selezionati.".format(fullname), "info")

        return redirect(url_for("users.index"))

    return render_template("users/confirm_user_deletion.html", form=form, active_page="users.index", page_title="Eliminazione volontario", item_name=fullname)

@bp.route('/<int:user_id>/duplicate')
@login_required
def duplicate_user(user_id):
    """Duplicate a user."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    # Colne only the current subtype association
    assoc = UserSubtypeAssociation.query.filter_by(user_id=user_id, subtype_id=int(request.args.get("subtype_id"))).first()
    old_email = user.email1

    # Clone the user with a new id and also his subtype association
    db.session.expunge(user)
    db.session.expunge(assoc)
    make_transient(user)
    make_transient(assoc)
    user.id = None
    user.email1 = "{}-{}".format(old_email, str(random.randint(0, 999)))
    assoc.id = None
    db.session.add(user)
    db.session.commit()

    assoc.user_id = user.id
    db.session.add(assoc)
    db.session.commit()

    fullname = "{} {}".format(user.firstname, user.lastname)
    flash("Utente \"{}\" duplicato.".format(fullname), "info")

    return redirect(url_for("users.index"))

@bp.route("/<int:user_id>/update", methods=("GET", "POST"))
@login_required
def update_user(user_id):
    """Update existing user informations."""

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    # Populate fields with current user info
    subtype_choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    # Get the subtype ids to populate multiselect field
    subtype_defaults = [row[0] for row in UserSubtypeAssociation.query.with_entities(UserSubtypeAssociation.subtype_id).filter_by(user_id=user_id)]

    form = UpdateUserForm(validate_email1=False, subtype=subtype_defaults, firstname=user.firstname, lastname=user.lastname, gender=user.gender, born_on=user.born_on, born_in=user.born_in, zip=user.zip, city=user.city, address=user.address, email1=user.email1, email2=user.email2, tel1=user.tel1, tel2=user.tel2, notes=user.notes)

    form.gender.choices = ["Non specificato", "Uomo", "Donna"]
    form.subtype.choices = subtype_choices

    if form.validate_on_submit():
        # Update the user
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.gender = form.gender.data
        user.born_on = form.born_on.data
        user.born_in = form.born_in.data
        user.zip = form.zip.data
        user.city = form.city.data
        user.address = form.address.data
        user.email1 = form.email1.data
        user.email2 = form.email2.data
        user.tel1 = form.tel1.data
        user.tel2 = form.tel2.data
        user.notes = form.notes.data

        # Update his subtype associations (create new or delete)
        associations_to_delete = list(set(subtype_defaults) - set(form.subtype.data))
        associations_to_create = list(set(form.subtype.data) - set(subtype_defaults))
        for subtype_id in associations_to_delete:
            assoc = UserSubtypeAssociation.query.filter_by(user_id=user_id, subtype_id=subtype_id).first()
            db.session.delete(assoc)
        for subtype_id in associations_to_create:
            assoc = UserSubtypeAssociation(user_id=user_id, subtype_id=subtype_id)
            db.session.add(assoc)

        db.session.commit()

        fullname = "{} {}".format(user.firstname, user.lastname)
        flash("Volontario \"{}\" modificato.".format(fullname), "info")
        return redirect(url_for("users.index"))

    return render_template("users/new_update_user.html", form=form, action="update")

@bp.route("/all")
@login_required
def all_users():
    """Show all users."""

    users = User.query\
        .with_entities(User.id, User.firstname, User.lastname, User.gender, User.born_on, User.born_in, User.zip, User.city, User.address, User.email1, User.email2, User.tel1, User.tel2, User.notes, UserSubtype.name.label("subtype_name"))\
        .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
        .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
        .order_by(UserSubtype.name, User.lastname)\
        .all()

    return render_template("users/all_users.html", users=users)
