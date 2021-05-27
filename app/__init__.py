from flask import Flask
from flask_migrate import Migrate
from app.models import db
from flask_moment import Moment
import os

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    # Create and configure the app (from .flaskenv file)
    app = Flask(__name__)
    app.config.update (
        FLASK_APP=os.environ.get("FLASK_APP"),
        FLASK_ENV=os.environ.get("FLASK_ENV"),
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Initialize Moment extension for formatting dates and times
    moment = Moment(app)

    # Set up the database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Apply the blueprints to the app
    from app import auth, users, events, activities
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(activities.bp)

    # Import CLI commands
    from app.commands import recreate_db_command, setup_db_command
    app.cli.add_command(recreate_db_command)
    app.cli.add_command(setup_db_command)

    # Home = activity records
    app.add_url_rule('/', endpoint='index')

    return app
