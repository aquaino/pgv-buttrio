from flask import Blueprint
from flask import render_template
from app.auth import login_required
from app.models import db, Event, GreenBookCategory
from app.forms import NewUpdateEventForm, ConfirmActionForm
from flask import flash, redirect, url_for, abort
from sqlalchemy.orm.session import make_transient

bp = Blueprint("events", __name__, url_prefix="/events")


@bp.route("/")
@login_required
def index():
    """Show all the events."""
    events = Event.query.with_entities(GreenBookCategory.name.label("cat_name"), Event.id, Event.name, Event.descr).join(GreenBookCategory, Event.green_book_cat_id == GreenBookCategory.id).order_by(GreenBookCategory.name).all()

    return render_template("events/index.html", events=events)

@bp.route("/new-event", methods=("GET", "POST"))
@login_required
def new_event():
    """Create a new event."""
    form = NewUpdateEventForm()
    # Flatten the query result to a list of tuples (id, name)
    # This way the option values of the select field in the form are the GB categories ids
    form.gb_category.choices = [(row.id, row.name) for row in GreenBookCategory.query.with_entities(GreenBookCategory.id, GreenBookCategory.name)]

    if form.validate_on_submit():
        event = Event(green_book_cat_id=form.gb_category.data, name=form.name.data, descr=form.descr.data)
        db.session.add(event)
        db.session.commit()

        flash("Evento \"{}\" aggiunto.".format(event.name), "info")
        return redirect(url_for("events.new_event", action="new"))

    return render_template("events/new_update_event.html", form=form, action="new")

# @bp.route('/<int:event_id>/delete', methods=("GET", "DELETE"))
# @login_required
# def delete_event(event_id):
#     """Delete an event."""
#     event = Event.query.filter_by(id=event_id).first()
#     if event is None:
#         abort(404)
#
#     db.session.delete(event)
#     db.session.commit()
#     flash("Evento \"{}\" eliminato.".format(event.name), "info")
#
#     return redirect(url_for("events.index"))

@bp.route('/<int:event_id>/confirm_deletion', methods=("GET", "POST"))
@login_required
def confirm_deletion(event_id):
    """Confirm the deletion of an event."""
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        abort(404)

    form = ConfirmActionForm()
    if form.validate_on_submit():
        db.session.delete(event)
        db.session.commit()
        flash("Evento \"{}\" eliminato.".format(event.name), "info")
        return redirect(url_for("events.index"))

    return render_template("confirm_action.html", form=form, active_page="events.index", page_title="Conferma eliminazione evento", item_name=event.name)

@bp.route('/<int:event_id>/update', methods=("GET", "POST"))
@login_required
def update_event(event_id):
    """Update an event."""
    # Populate fields with current data
    event = Event.query.filter_by(id=event_id).first()
    current_cat = GreenBookCategory.query.filter_by(id=event.green_book_cat_id).first()
    form = NewUpdateEventForm(gb_category=current_cat.id, name = event.name, descr = event.descr)

    form.gb_category.choices = [(row.id, row.name) for row in GreenBookCategory.query.with_entities(GreenBookCategory.id, GreenBookCategory.name)]

    if event is None:
        abort(404)

    if form.validate_on_submit():
        event.green_book_cat_id = form.gb_category.data
        event.name = form.name.data
        event.descr = form.descr.data

        db.session.add(event)
        db.session.commit()

        flash("Evento \"{}\" modificato.".format(event.name), "info")
        return redirect(url_for("events.index"))

    return render_template("events/new_update_event.html", form=form, action="update")

@bp.route('/<int:event_id>/duplicate')
@login_required
def duplicate_event(event_id):
    """Duplicate an event."""
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        abort(404)

    # Clone the event with a new id
    db.session.expunge(event)
    make_transient(event)
    event.id = None
    db.session.add(event)
    db.session.commit()
    flash(("success", "Evento \"{}\" duplicato.".format(event.name)))

    return redirect(url_for("events.index"))
