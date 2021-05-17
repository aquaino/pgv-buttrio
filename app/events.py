from flask import Blueprint
from flask import render_template
from app.auth import login_required
from app.models import Event, GreenBookCategory

bp = Blueprint("events", __name__, url_prefix="/events")


@bp.route("/")
@login_required
def index():
    """Show all the events."""
    events = Event.query.with_entities(GreenBookCategory.name.label("cat_name"), Event.name, Event.descr).join(GreenBookCategory, Event.green_book_cat_id == GreenBookCategory.id).order_by(GreenBookCategory.name).all()
    return render_template("events/index.html", events=events)

@bp.route("/new-event")
@login_required
def new_event():
    """Create a new event."""
    # TODO: create form
    return render_template("events/new_event.html")
