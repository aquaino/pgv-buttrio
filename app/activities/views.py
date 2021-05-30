from flask import Blueprint
from flask import render_template
from app.auth.views import login_required
from app.models import db, ActivityRecord, User, UserSubtypeAssociation, UserSubtype, Activity, Event

bp = Blueprint("activities", __name__)

@bp.route("/")
@login_required
def index():
    """Show recent activities."""
    activities = ActivityRecord.query\
        .with_entities(ActivityRecord.date, User.firstname, User.lastname, UserSubtype.name.label("subtype"), Event.name.label("event"), Activity.name.label("activity"), ActivityRecord.start_time, ActivityRecord.end_time, ActivityRecord.location, ActivityRecord.notes)\
        .join(User, User.id == ActivityRecord.user_id)\
        .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == ActivityRecord.user_id)\
        .join(UserSubtype, UserSubtype.id == UserSubtypeAssociation.subtype_id)\
        .join(Activity, Activity.id == ActivityRecord.activity_id)\
        .join(Event, Event.id == ActivityRecord.event_id)\
        .order_by(ActivityRecord.date)\
        .all()

    return render_template("activities/index.html", activities=activities)
