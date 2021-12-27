from flask import Flask
from flask_breadcrumbs import Breadcrumbs
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
breadcrumbs = Breadcrumbs()
moment = Moment()
toolbar = DebugToolbarExtension()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""

    # Create and configure the app (from .flaskenv file)
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # Set up extensions
    db.init_app(app)
    migrate.init_app(app, db)
    breadcrumbs.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)

    # Apply blueprints
    from . import auth, users, events, activities, reports, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(activities.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(main.bp)

    # Import CLI commands
    from app.commands import recreate_db_command, setup_db_command, compile_scss_watch_command
    app.cli.add_command(recreate_db_command)
    app.cli.add_command(setup_db_command)
    app.cli.add_command(compile_scss_watch_command)

    return app
