from flask import Blueprint, render_template, flash, abort, redirect, url_for, request, jsonify
from app.auth.views import login_required
from app.models import db, ActivityRecord, User, UserSubtypeAssociation, UserSubtype, Activity, Event
from app.activities.forms import NewUpdateActivityRecordForm
from app.forms import ConfirmActionForm
from sqlalchemy.orm.session import make_transient
from sqlalchemy import desc

bp = Blueprint("activities", __name__)

@bp.route("/")
@login_required
def index():
    """Show recent activities."""
    activities = ActivityRecord.query\
        .with_entities(ActivityRecord.id, ActivityRecord.date, User.firstname, User.lastname, UserSubtype.name.label("subtype"), Event.name.label("event"), Activity.name.label("activity"), ActivityRecord.start_time, ActivityRecord.end_time, ActivityRecord.location, ActivityRecord.notes)\
        .join(User, User.id == ActivityRecord.user_id)\
        .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == ActivityRecord.user_id)\
        .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
        .join(Activity, Activity.id == ActivityRecord.activity_id)\
        .join(Event, Event.id == ActivityRecord.event_id)\
        .order_by(desc(ActivityRecord.date))\
        .all()

    return render_template("activities/index.html", activities=activities)

@bp.route('/<int:activity_id>/delete', methods=("GET", "POST"))
@login_required
def delete_activity(activity_id):
    """Confirm the deletion of an activity record."""
    activity = ActivityRecord.query.filter_by(id=activity_id).first()
    if activity is None:
        abort(404)

    # Get activity record useful info
    user = User.query.filter_by(id=activity.user_id).first()
    event = Event.query.filter_by(id=activity.event_id).first()
    activity_type = Activity.query.filter_by(id=activity.activity_id).first()

    activity_record_name = "{} - {} {} - {} - {}".format(activity.date, user.firstname, user.lastname, event.name, activity_type.name)

    form = ConfirmActionForm()
    if form.validate_on_submit():
        db.session.delete(activity)
        db.session.commit()

        flash("Record attività \"{}\" eliminato.".format(activity_record_name), "info")
        return redirect(url_for("activities.index"))

    return render_template("confirm_deletion.html", form=form, active_page="activities.index", page_title="Eliminazione record attività", item_name=activity_record_name)

@bp.route('/<int:activity_id>/duplicate')
@login_required
def duplicate_activity(activity_id):
    """Duplicate an activity record."""
    activity = ActivityRecord.query.filter_by(id=activity_id).first()
    if activity is None:
        abort(404)

    # Clone the activity with a new id
    db.session.expunge(activity)
    make_transient(activity)
    activity.id = None
    db.session.add(activity)
    db.session.commit()

    # Get activity record useful info
    user = User.query.filter_by(id=activity.user_id).first()
    event = Event.query.filter_by(id=activity.event_id).first()
    activity_type = Activity.query.filter_by(id=activity.activity_id).first()

    activity_record_name = "{} - {} {} - {} - {}".format(activity.date, user.firstname, user.lastname, event.name, activity_type.name)

    flash("Record attività \"{}\" duplicato.".format(activity_record_name), "info")

    return redirect(url_for("activities.index"))

@bp.route("/new-activity", methods=("GET", "POST"))
@login_required
def new_activity():
    """Create a new activity record."""
    form = NewUpdateActivityRecordForm()

    # Populate select fields
    form.subtype.choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    form.user.choices = [(row.id, row.lastname + " " + row.firstname) for row in User.query.filter(User.email1 != "admin@admin.it").order_by(User.lastname)]
    form.event.choices = [(row.id, row.name) for row in Event.query.with_entities(Event.id, Event.name)]
    form.activity.choices = [(row.id, row.name) for row in Activity.query.with_entities(Activity.id, Activity.name)]

    if form.validate_on_submit():
        # Create the record
        record = ActivityRecord(date=form.date.data, user_id=form.user.data, event_id=form.event.data, activity_id=form.activity.data, start_time=form.start_time.data, end_time=form.end_time.data, location=form.location.data, notes=form.notes.data)
        db.session.add(record)
        db.session.commit()

        flash("Record attività aggiunto.", "info")
        return redirect(url_for("activities.new_activity", action="new"))

    return render_template("activities/new_update_activity.html", form=form, action="new")

@bp.route("/_get_users/")
def _get_users():
    subtype = request.args.get("subtype", "01", type=int)
    users = [(row.id, row.lastname + " " + row.firstname) for row in User.query.join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id).filter(UserSubtypeAssociation.subtype_id == subtype).order_by(User.lastname)]
    return jsonify(users)
