from flask import Blueprint, render_template, flash, abort, redirect, url_for, request, jsonify
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu
from sqlalchemy import desc
from sqlalchemy.orm.session import make_transient
import requests

from app.activities.forms import NewUpdateActivityRecordForm
from app.auth.views import login_required
from app.forms import ConfirmActionForm
from app.models import db, ActivityRecord, User, UserSubtypeAssociation, UserSubtype, Activity, Event

bp = Blueprint("activities", __name__, url_prefix="/activities")

@bp.route("/")
@login_required
@register_menu(bp, '.activities', 'Attività')
@register_breadcrumb(bp, '.', 'Attività')
def index():
    """Show recent activities."""
    activities = ActivityRecord.query\
        .with_entities(
            ActivityRecord.id, ActivityRecord.date, User.firstname, User.lastname, UserSubtype.name.label("subtype"),
            Event.name.label("event"), Activity.name.label("activity"), ActivityRecord.start_time,
            ActivityRecord.end_time, ActivityRecord.region, ActivityRecord.province, ActivityRecord.town,
            ActivityRecord.location, ActivityRecord.notes)\
        .join(User, User.id == ActivityRecord.user_id)\
        .join(UserSubtype, UserSubtype.id == ActivityRecord.subtype_id)\
        .join(Activity, Activity.id == ActivityRecord.activity_id)\
        .join(Event, Event.id == ActivityRecord.event_id)\
        .order_by(desc(ActivityRecord.date), desc(ActivityRecord.start_time))\
        .all()

    return render_template("activities/index.html", activities=activities)

def activity_eac(*args, **kwargs):
    activity_id = request.view_args['activity_id']
    return {'activity_id': activity_id}

@bp.route('/<int:activity_id>/delete', methods=("GET", "POST"))
@register_breadcrumb(bp, '.delete', 'Elimina attività', endpoint_arguments_constructor=activity_eac)
@login_required
def delete_activity(activity_id):
    """Confirm the deletion of an activity record."""
    activity = ActivityRecord.query.filter_by(id=activity_id).first()
    if activity is None:
        abort(404)

    # Get activity record useful info
    user = User.query.filter_by(id=activity.user_id).first()
    event = Event.query.filter_by(id=activity.activity_id).first()
    activity_type = Activity.query.filter_by(id=activity.activity_id).first()

    activity_record_name = "{} - {} {} - {} - {}".format(activity.date, user.firstname, user.lastname, event.name, activity_type.name)

    form = ConfirmActionForm()
    if form.validate_on_submit():
        db.session.delete(activity)
        db.session.commit()

        flash("Record attività \"{}\" eliminato.".format(activity_record_name), "info")
        return redirect(url_for("activities.index"))

    return render_template("confirm_deletion.html", form=form, page_title="Eliminazione record attività", item_name=activity_record_name)

@bp.route('/<int:activity_id>/duplicate', methods=('GET', 'POST'))
@register_breadcrumb(bp, '.duplicate-activity', 'Duplica attività', endpoint_arguments_constructor=activity_eac)
@login_required
def duplicate_activity(activity_id):
    """Confirm and duplicate an activity record."""
    activity = ActivityRecord.query.filter_by(id=activity_id).first()
    if activity is None:
        abort(404)

    form = ConfirmActionForm()

    # Get activity record useful info
    user = User.query.filter_by(id=activity.user_id).first()
    event = Event.query.filter_by(id=activity.event_id).first()
    activity_type = Activity.query.filter_by(id=activity.activity_id).first()

    activity_record_name = "{} - {} {} - {} - {}".format(activity.date, user.firstname, user.lastname, event.name, activity_type.name)
    
    if form.validate_on_submit():
        # Clone the activity with a new id
        db.session.expunge(activity)
        make_transient(activity)
        activity.id = None
        db.session.add(activity)
        db.session.commit()

        flash("Record attività \"{}\" duplicato.".format(activity_record_name), "info")

        return redirect(url_for("activities.index"))

    return render_template("confirm_duplication.html", form=form, page_title="Duplicazione attività", item_name=event.name)

@bp.route("/new-activity", methods=("GET", "POST"))
@register_breadcrumb(bp, '.new-activity', 'Nuova attività')
@login_required
def new_activity():
    """Create a new activity record."""
    form = NewUpdateActivityRecordForm()

    # Populate select fields
    form.subtype.choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    form.user.choices = [(row.id, row.lastname + " " + row.firstname) for row in User.query.filter(User.email != "admin@admin.it").order_by(User.lastname)]
    form.event.choices = [(row.id, row.name) for row in Event.query.with_entities(Event.id, Event.name)]
    form.activity.choices = [(row.id, row.name) for row in Activity.query.with_entities(Activity.id, Activity.name)]
    form.region.choices = _get_regions().json
    form.province.choices = _get_provinces().json
    form.town.choices = _get_towns().json

    if form.validate_on_submit():
        # Create the record
        record = ActivityRecord(
            date=form.date.data, subtype_id=form.subtype.data, user_id=form.user.data,
            event_id=form.event.data, activity_id=form.activity.data, start_time=form.start_time.data,
            end_time=form.end_time.data, region=form.region.data, province=form.province.data,
            town=form.town.data, location=form.location.data, notes=form.notes.data
        )
        db.session.add(record)
        db.session.commit()

        flash("Record attività aggiunto.", "info")
        return redirect(url_for("activities.index"))

    return render_template("activities/new_update_activity.html", form=form, action="new")

@bp.route("/_get_users/")
@login_required
def _get_users():
    subtype = request.args.get("subtype", type=int)
    if subtype:
        users = [(row.id, row.lastname + " " + row.firstname) for row in User.query.join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id).filter(UserSubtypeAssociation.subtype_id == subtype).order_by(User.lastname)]
        return jsonify(users)
    else:
        return ""

@bp.route("/<int:activity_id>/update", methods=("GET", "POST"))
@register_breadcrumb(bp, '.update-activity', 'Modifica attività', endpoint_arguments_constructor=activity_eac)
@login_required
def update_activity(activity_id):
    """Update existing activity record informations."""

    activity = ActivityRecord.query.filter_by(id=activity_id).first()
    if activity is None:
        abort(404)

    # Populate fields with current record info
    form = NewUpdateActivityRecordForm(
        subtype=activity.subtype_id, user=activity.user_id, date=activity.date, event=activity.event,
        activity=activity.activity_id, start_time=activity.start_time, end_time=activity.end_time, region=activity.region,
        province=activity.province, town=activity.town, location=activity.location, notes=activity.notes
    )

    form.subtype.choices = [(row.id, row.name) for row in UserSubtype.query.with_entities(UserSubtype.id, UserSubtype.name)]
    form.user.choices = [(row.id, row.lastname + " " + row.firstname) for row in User.query.filter(User.email != "admin@admin.it").order_by(User.lastname)]
    form.event.choices = [(row.id, row.name) for row in Event.query.with_entities(Event.id, Event.name)]
    form.activity.choices = [(row.id, row.name) for row in Activity.query.with_entities(Activity.id, Activity.name)]
    form.region.choices = _get_regions().json
    form.province.choices = _get_provinces().json
    form.town.choices = _get_towns().json

    if form.validate_on_submit():
        activity.subtype_id = form.subtype.data
        activity.user_id = form.user.data
        activity.date = form.date.data
        activity.event_id = form.event.data
        activity.activity_id = form.activity.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.region = form.region.data
        activity.province = form.province.data
        activity.town = form.town.data
        activity.location = form.location.data
        activity.notes = form.notes.data

        db.session.commit()

        flash("Record attività modificato.", "info")
        return redirect(url_for("activities.index"))

    return render_template("activities/new_update_activity.html", form=form, action="update")

COMUNI_ITA_API = "https://comuni-ita.herokuapp.com/api"

@bp.route("/_get_regions/")
@login_required
def _get_regions():
    """Get all regions."""
    return jsonify([(x, x) for x in requests.get(COMUNI_ITA_API + "/regioni").json()])

@bp.route("/_get_provinces/")
@login_required
def _get_provinces():
    """Get all provinces or provinces of the specified region."""
    region = request.args.get("region")
    if region:
        provinces = [(x, x) for x in requests.get(COMUNI_ITA_API + "/province/" + region + "?onlyname=true").json()]
    else:
        provinces = [(x, x) for x in requests.get(COMUNI_ITA_API + "/province?onlyname=true").json()]
    return jsonify(provinces)

@bp.route("/_get_towns/")
@login_required
def _get_towns():
    """Get all towns or towns of the specified province."""
    province = request.args.get("province", type=str)
    if province:
        towns = [(x, x) for x in requests.get(COMUNI_ITA_API + "/comuni/provincia/" + province + "?onlyname=true").json()]
    else:
        towns = [(x, x) for x in requests.get(COMUNI_ITA_API + "/comuni?onlyname=true").json()]
    return jsonify(towns)
