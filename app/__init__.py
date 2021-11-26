from flask import Flask
from flask_migrate import Migrate
from app.models import db
from flask_moment import Moment
from flask_breadcrumbs import Breadcrumbs
from flask import render_template
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from app.auth.views import login_required

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    # Create and configure the app (from .flaskenv file)
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # Initialize Moment extension for formatting dates and times
    moment = Moment(app)

    # Set up the database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Flask menu and breadcrumbs
    Breadcrumbs(app=app)

    # Apply the blueprints to the app
    from app import auth, users, events, activities, reports
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(activities.bp)
    app.register_blueprint(reports.bp)

    # Home route
    default_breadcrumb_root(app, '.')

    @app.route("/")
    @register_breadcrumb(app, '.', 'Home')
    @login_required
    def index():
        return render_template("index.html")

    app.add_url_rule('/', endpoint='index')

    # Import CLI commands
    from app.commands import recreate_db_command, setup_db_command, compile_scss_watch_command
    app.cli.add_command(recreate_db_command)
    app.cli.add_command(setup_db_command)
    app.cli.add_command(compile_scss_watch_command)

    return app
