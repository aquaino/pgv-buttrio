from flask import Flask
from flask_migrate import Migrate
from app.models import db
from flask_moment import Moment

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    # Create and configure the app (from .flaskenv file)
    app = Flask(__name__)
    app.config.from_object("app.settings")

    # Initialize Moment extension for formatting dates and times
    moment = Moment(app)

    # Set up the database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Apply the blueprints to the app
    from app import auth, users, events, activities, reports
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(activities.bp)
    app.register_blueprint(reports.bp)

    # Import CLI commands
    from app.commands import recreate_db_command, setup_db_command
    app.cli.add_command(recreate_db_command)
    app.cli.add_command(setup_db_command)

    # Home = activity records
    app.add_url_rule('/', endpoint='index')

    return app
