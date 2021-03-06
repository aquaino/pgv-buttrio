import random
import time

from flask import Blueprint, flash, abort, redirect, url_for, render_template, request
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu
from sqlalchemy.orm.session import make_transient
from werkzeug.security import generate_password_hash

from app.auth.views import login_required
from app.forms import ConfirmActionForm
from app.models import db, User, UserSubtypeAssociation, UserSubtype, UserType, ActivityRecord
from app.users.forms import NewUserForm, ConfirmUserDeletionForm, UpdateUserForm
from app.activities.views import _get_regions, _get_provinces, _get_towns

bp = Blueprint("users", __name__, url_prefix="/users")


def merge_subtypes(users, subtypes_count):
    """Merge subtype fields for same user belonging to multiple subcategories."""
    users_length = len(users)
    # Sort by id
    users = sorted(users, key=lambda x: x[0])

    to_delete = []
    i = 0
    while i <= users_length - 1:
        # To prevent index out of range
        if i + subtypes_count - 1 >= users_length - 1:
            subtypes_count = (users_length - 1) - i

        k = i + 1
        deleted_count = 0
        # Convert to list to make the record mutable
        users[i] = list(users[i])
        while k <= i + subtypes_count:
            if users[k][0] == users[i][0]:
                # Merge subtypes and sort them alphabetically
                users[i][12] += ', ' + users[k][12]

                deleted_count += 1
                to_delete.insert(0, k)

            k += 1

        users[i][12] = ', '.join(map(str, sorted([subtype for subtype in users[i][12].split(', ')], key=str.lower)))
        # Re-convert the record to TUPLE
        users[i] = tuple(users[i])

        if deleted_count > 0:
            i += deleted_count + 1
        else:
            i += 1

    # Remove duplicated user records
    for n in to_delete:
        del (users[n])

    # Sort by lastname
    users = sorted(users, key=lambda x: x[2])

    return users

@bp.route("/")
@login_required
@register_menu(bp, '.users', 'Volontari')
@register_breadcrumb(bp, '.', 'Volontari')
def index():
    """Show all users, organized by type."""

    def users_by_type(type_name):
        """General query structure for different type of users."""
        users = User.query\
            .with_entities(User.id, User.firstname, User.lastname, User.gender, User.born_on, User.region,
                           User.province, User.town, User.address, User.email, User.tel, User.notes,
                           UserSubtype.name.label("subtype_name"), UserSubtype.id.label("subtype_id"))\
            .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
            .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
            .join(UserType, UserType.id == UserSubtype.type_id)\
            .filter(UserType.name == type_name, User.deleted == False)\
            .all()

        return users

    # Prepare data to send
    pc_id = UserType.query.filter_by(name="Protezione Civile").first().id
    pc_subtypes_count = UserSubtype.query.filter_by(type_id=pc_id).count()
    pc = merge_subtypes(users_by_type("Protezione Civile"), pc_subtypes_count)

    alpini_id = UserType.query.filter_by(name="Alpini").first().id
    alpini_subtypes_count = UserSubtype.query.filter_by(type_id=alpini_id).count()
    alpini = merge_subtypes(users_by_type("Alpini"), alpini_subtypes_count)

    occ_id = UserType.query.filter_by(name="Volontari occasionali").first().id
    occ_subtypes_count = UserSubtype.query.filter_by(type_id=occ_id).count()
    occasionali = merge_subtypes(users_by_type("Volontari occasionali"), occ_subtypes_count)

    est_id = UserType.query.filter_by(name="Esterni non assicurati").first().id
    est_subtypes_count = UserSubtype.query.filter_by(type_id=est_id).count()
    non_assicurati = merge_subtypes(users_by_type("Esterni non assicurati"), est_subtypes_count)

    return render_template("users/index.html", pc=pc, alpini=alpini, occasionali=occasionali, non_assicurati=non_assicurati)

GENDER_CHOICES = [("Non specificato", "Non specificato"), ("Uomo", "Uomo"), ("Donna", "Donna")]

@bp.route("/new-user", methods=("GET", "POST"))
@login_required
@register_breadcrumb(bp, '.new-user', 'Nuovo volontario')
def new_user():
    """Create a new user."""
    subtype_choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    form = NewUserForm(subtype=[subtype_choices[0][0]])
    form.gender.choices = GENDER_CHOICES
    form.subtype.choices = subtype_choices
    form.region.choices = _get_regions().json
    form.province.choices = _get_provinces().json
    form.town.choices = _get_towns().json

    if form.validate_on_submit():
        # Create the user
        user = User(
            firstname=form.firstname.data, lastname=form.lastname.data, gender=form.gender.data,
            born_on=form.born_on.data, region=form.region.data, province=form.province.data, town=form.town.data,
            address=form.address.data, email=form.email.data, tel=form.tel.data, notes=form.notes.data, admin=form.admin.data
        )
        db.session.add(user)
        db.session.commit()

        # Set user's subtype/s
        for subtype_id in form.subtype.data:
            assoc = UserSubtypeAssociation(user_id=user.id, subtype_id=subtype_id)
            db.session.add(assoc)

        db.session.commit()

        flash("Utente \"{} {}\" aggiunto.".format(user.firstname, user.lastname), "info")
        return redirect(url_for("users.index"))

    return render_template("users/new_update_user.html", form=form, action="new")

def user_eac(*args, **kwargs):
    user_id = request.view_args['user_id']
    return {'user_id': user_id}

@bp.route('/<int:user_id>/delete', methods=("GET", "POST"))
@login_required
@register_breadcrumb(bp, '.delete-user', 'Elimina volontario')
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
            db.session.commit()

        # If all the subtypes were selected also the user will be deleted
        removed_from_all = (len(form.subtype.data) == len(form.subtype.choices))

        if removed_from_all:
            # To avoid future email collisions with new users emails
            user.email += '_deleted' + str(int(time.time()))
            user.deleted = True
            db.session.commit()
            flash("Volontario \"{}\" rimosso dal sistema.".format(fullname), "info")
        else:
            flash("Volontario \"{}\" eliminato dal/i gruppo/i selezionato/i.".format(fullname), "info")

        return redirect(url_for("users.index"))

    return render_template("users/confirm_user_deletion.html", form=form, page_title="Eliminazione volontario", item_name=fullname)

@bp.route('/<int:user_id>/duplicate', methods=("GET", "POST"))
@register_breadcrumb(bp, '.duplicate-user', 'Duplica volontario', endpoint_arguments_constructor=user_eac)
@login_required
def duplicate_user(user_id):
    """Confirm and duplicate a user."""

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    form = ConfirmActionForm()

    fullname = "{} {}".format(user.firstname, user.lastname)
    if form.validate_on_submit():
        # Clone only the current subtype association
        assoc = UserSubtypeAssociation.query.filter_by(user_id=user_id, subtype_id=int(request.args.get("subtype_id"))).first()
        old_email = user.email

        # Clone the user with a new id and also his subtype association
        db.session.expunge(user)
        db.session.expunge(assoc)
        make_transient(user)
        make_transient(assoc)
        user.id = None
        user.email = "{}-{}".format(old_email, str(random.randint(0, 999)))
        assoc.id = None
        db.session.add(user)
        db.session.commit()

        assoc.user_id = user.id
        db.session.add(assoc)
        db.session.commit()

        flash("Utente \"{}\" duplicato.".format(fullname), "info")

        return redirect(url_for("users.index"))

    return render_template("confirm_duplication.html", form=form, page_title="Duplicazione utente", item_name=fullname)

@bp.route("/<int:user_id>/update", methods=("GET", "POST"))
@register_breadcrumb(bp, '.update-user', 'Modifica volontario', endpoint_arguments_constructor=user_eac)
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

    form = UpdateUserForm(
        id=user_id , subtype=subtype_defaults, firstname=user.firstname, lastname=user.lastname, gender=user.gender,
        born_on=user.born_on, region=user.region, province=user.province, town=user.town, address=user.address, email=user.email,
        tel=user.tel, notes=user.notes, admin=user.admin
    )

    form.gender.choices = GENDER_CHOICES
    form.subtype.choices = subtype_choices
    form.region.choices = _get_regions().json
    form.province.choices = _get_provinces().json
    form.town.choices = _get_towns().json

    if form.validate_on_submit():
        # Update the user
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.gender = form.gender.data
        user.born_on = form.born_on.data
        user.region = form.region.data
        user.province = form.province.data
        user.town = form.town.data
        user.address = form.address.data
        user.email = form.email.data
        user.tel = form.tel.data
        user.notes = form.notes.data
        user.admin = form.admin.data
        # Avoid empty password on update
        if form.password.data:
            user.password = generate_password_hash(form.password.data)

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
@register_breadcrumb(bp, '.all', 'Tutti')
@login_required
def all_users():
    """Show all users."""
    users = User.query\
            .with_entities(User.id, User.firstname, User.lastname, User.gender, User.born_on, User.region,
                           User.province, User.town, User.address, User.email, User.tel, User.notes,
                           UserSubtype.name.label("subtype_name"), UserSubtype.id.label("subtype_id"))\
            .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
            .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
            .join(UserType, UserType.id == UserSubtype.type_id)\
            .filter(User.deleted == False)\
            .all()

    # Merge types to which the user belongs
    types = UserType.query.all()
    types_ids = [type.id for type in types]
    all_subtypes_count = []
    for type_id in types_ids:
        all_subtypes_count.append(UserSubtype.query.filter_by(type_id=type_id).count())

    users = merge_subtypes(users, sum(all_subtypes_count))

    return render_template("users/all_users.html", users=users)

