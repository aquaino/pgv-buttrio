from flask import Blueprint, render_template
from flask import current_app
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu
from sqlalchemy import create_engine
from sqlalchemy import func, desc

from app.auth.views import login_required
from app.models import User, UserSubtypeAssociation, UserSubtype, UserType, Event, ActivityRecord

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/")
@login_required
@register_menu(bp, '.reports', 'Report')
@register_breadcrumb(bp, '.', 'Report')
def index():
    """Show all the reports."""
    # For raw SQL queries
    db_path = current_app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(db_path)
    connection = engine.connect()

    # Number of users
    users_count = User.query.filter(User.email!='admin@admin.it').count()

    # Amount of hours in different activities
    ah_query = "SELECT end_time - start_time FROM activity_records"
    result = connection.execute(ah_query).fetchall()
    activity_hours = sum([item[0].seconds/3600 for item in result])

    # Users by type
    users_by_type = User.query\
        .with_entities(UserType.name, func.count(User.id))\
        .join(UserSubtypeAssociation, UserSubtypeAssociation.user_id == User.id)\
        .join(UserSubtype, UserSubtypeAssociation.subtype_id == UserSubtype.id)\
        .join(UserType, UserType.id == UserSubtype.type_id)\
        .group_by(UserType.name)\
        .order_by(desc(func.count(User.id)))\
        .all()

    # Events count
    events_count = Event.query.count()

    # Days count
    days_count = ActivityRecord.query.distinct(ActivityRecord.date).count()

    # Admins
    admins = User.query.filter(User.admin==True).order_by(User.lastname).all()

    # Most active users
    most_active_users = User.query\
        .with_entities(User.firstname, User.lastname, func.count(User.id))\
        .join(ActivityRecord, ActivityRecord.user_id == User.id)\
        .group_by(User.firstname, User.lastname)\
        .order_by(desc(func.count(User.id)))\
        .limit(3).all()

    # Most active groups
    most_active_groups = UserSubtype.query\
        .with_entities(UserSubtype.name, func.count(UserSubtype.id))\
        .join(ActivityRecord, ActivityRecord.subtype_id == UserSubtype.id)\
        .group_by(UserSubtype.name)\
        .order_by(desc(func.count(UserSubtype.id)))\
        .limit(3).all()

    return render_template("reports/index.html",
        users_count=users_count,
        activity_hours=activity_hours,
        users_by_type=users_by_type,
        events_count=events_count,
        days_count=days_count,
        admins=admins,
        most_active_users=most_active_users,
        most_active_groups=most_active_groups
    )
