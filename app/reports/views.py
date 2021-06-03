from flask import Blueprint, render_template
from app.auth.views import login_required
from app.models import db, ActivityRecord, User, UserSubtypeAssociation, UserSubtype, Activity, Event

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/")
@login_required
def index():
    """Show all the reports."""
    activities = ActivityRecord.query\
        .with_entities(ActivityRecord.id, ActivityRecord.date, User.firstname, User.lastname, UserSubtype.name.label("subtype"), Event.name.label("event"), Activity.name.label("activity"), ActivityRecord.start_time, ActivityRecord.end_time, ActivityRecord.location, ActivityRecord.notes)\
        .join(User, User.id == ActivityRecord.user_id)\
        .join(UserSubtype, UserSubtype.id == ActivityRecord.subtype_id)\
        .join(Activity, Activity.id == ActivityRecord.activity_id)\
        .join(Event, Event.id == ActivityRecord.event_id)\
        .order_by(ActivityRecord.date, ActivityRecord.start_time)\
        .all()

    return render_template("reports/index.html", activities=activities)
