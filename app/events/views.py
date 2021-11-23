from flask import Blueprint, request
from flask import render_template
from app.auth.views import login_required
from app.models import db, Event, GreenBookCategory
from app.events.forms import NewUpdateEventForm
from app.forms import ConfirmActionForm
from flask import flash, redirect, url_for, abort
from sqlalchemy.orm.session import make_transient
import random
from flask_menu import register_menu
from flask_breadcrumbs import register_breadcrumb

bp = Blueprint("events", __name__, url_prefix="/events")

@bp.route("/")
@login_required
@register_menu(bp, '.events', 'Eventi')
@register_breadcrumb(bp, '.', 'Eventi')
def index():
    """Show all the events."""
    events = Event.query.with_entities(GreenBookCategory.name.label("cat_name"), Event.id, Event.name, Event.descr).join(GreenBookCategory, Event.green_book_cat_id == GreenBookCategory.id).order_by(GreenBookCategory.name).all()

    return render_template("events/index.html", events=events)

@bp.route("/new-event", methods=("GET", "POST"))
@register_breadcrumb(bp, '.new-event', 'Nuovo evento')
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
        return redirect(url_for("events.index"))

    return render_template("events/new_update_event.html", form=form, action="new")

def event_eac(*args, **kwargs):
    event_id = request.view_args['event_id']
    return {'event_id': event_id}

@bp.route('/<int:event_id>/delete', methods=("GET", "POST"))
@register_breadcrumb(bp, '.delete-event', 'Elimina evento', endpoint_arguments_constructor=event_eac)
@login_required
def delete_event(event_id):
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

    return render_template("confirm_deletion.html", form=form, page_title="Eliminazione evento", item_name=event.name)

@bp.route('/<int:event_id>/update', methods=("GET", "POST"))
@register_breadcrumb(bp, '.update-event', 'Modifica evento', endpoint_arguments_constructor=event_eac)
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

        db.session.commit()

        flash("Evento \"{}\" modificato.".format(event.name), "info")
        return redirect(url_for("events.index"))

    return render_template("events/new_update_event.html", form=form, action="update")

@bp.route('/<int:event_id>/duplicate', methods=('GET', 'POST'))
@register_breadcrumb(bp, '.duplicate-event', 'Duplica evento', endpoint_arguments_constructor=event_eac)
@login_required
def duplicate_event(event_id):
    """Confirm and duplicate an event."""
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        abort(404)

    form = ConfirmActionForm()

    if form.validate_on_submit():
        # Clone the event with a new id
        old_name = event.name
        db.session.expunge(event)
        make_transient(event)
        event.id = None
        event.name = "{}-{}".format(old_name, str(random.randint(0, 999)))
        db.session.add(event)
        db.session.commit()
        flash("Evento \"{}\" duplicato.".format(old_name), "info")

        return redirect(url_for("events.index"))

    return render_template("confirm_update.html", form=form, page_title="Duplicazione evento", item_name=event.name)
