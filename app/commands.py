import subprocess
from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from app.models import db, User, UserType, UserSubtype, UserSubtypeAssociation, GreenBookCategory, Event, Activity


@click.command("recreate-db")
@with_appcontext
def recreate_db_command():
    """Recreate the database."""
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("Database recreated.")

@click.command("setup-db")
@with_appcontext
def setup_db_command():
    """Fill database with demo data."""

    # Add admin user and some fake users
    admin_user = User(firstname="Admin", lastname="Admin", email="admin@admin.it", admin=True, password=generate_password_hash("admin"))
    db.session.add(admin_user)

    fake_users = [
        ("Alan", "Quaino", "Uomo", datetime.strptime("14/03/1996", "%d/%m/%Y"), "Friuli Venezia Giulia", "Udine", "Buttrio", "alanquaino@gmail.com"),
        ("Utente", "Test", "Non specificato", None, "Friuli Venezia Giulia", "Udine", "Buttrio", "utente@test.com"),
    ]
    for fake_user in fake_users:
        user = User(firstname=fake_user[0], lastname=fake_user[1], gender=fake_user[2], born_on=fake_user[3],
            region=fake_user[4], province=fake_user[5], town=fake_user[6], email=fake_user[7])
        db.session.add(user)

    print("Admin and fake users created.")

    # Add user types
    user_types = ["Alpini", "Protezione Civile", "Volontari occasionali", "Esterni non assicurati"]
    for type in user_types:
        user_type = UserType(name=type)
        db.session.add(user_type)
    print("User types created.")

    # Add user subtypes
    user_subtypes = [("Soci degli Alpini", 1), ("Amici degli Alpini", 1), ("Aggregati degli Alpini", 1), ("PC Comunale", 2), ("PC ANA", 2), ("Volontari Civici", 3), ("Volontari Semplici", 3), ("Esterni", 4)]
    for subtype in user_subtypes:
        user_subtype = UserSubtype(name=subtype[0], type_id=subtype[1])
        db.session.add(user_subtype)
    print("User subtypes created.")

    # Associate users with some subtypes
    associations = [(2, 4), (3, 4), (4, 1)]
    for assoc in associations:
        association = UserSubtypeAssociation(user_id=assoc[0], subtype_id=assoc[1])
        db.session.add(association)

    # Add Green Book categories
    gb_categories = ["Alpini in Armi", "Anziani", "Banco Alimentare", "Comunit??", "Enti Benefici", "Manifestazioni Patriottiche", "Missioni", "Parrocchia", "Protezione Civile", "Scuole e Giovani"]
    for cat in gb_categories:
        gb_category = GreenBookCategory(name=cat)
        db.session.add(gb_category)
    print("Green Book categories created.")

    # Add events
    events = [("24 Ore", 4), ("Rally Cividale - Castelmonte", 4), ("Trasporto per vaccini", 2), ("Stand Telefono Azzurro", 5)]
    for ev in events:
        event = Event(name=ev[0], green_book_cat_id=ev[1])
        db.session.add(event)
    print("Events created.")

    # Add activities
    activities = ["Logistica", "Cucina", "Chioschi", "Viabilit??", "Segreteria", "Biglietteria", "Sicurezza"]
    for act in activities:
        activity = Activity(name=act)
        db.session.add(activity)
    print("Activities created.")

    # Commit all
    db.session.commit()

@click.command("compile-scss-watch")
@with_appcontext
def compile_scss_watch_command():
    """Watch to compile SCSS assets into CSS (Ctrl+C to stop)."""
    subprocess.call(["sass", "--watch", f"{current_app.root_path}/static/scss/main.scss:{current_app.root_path}/static/css/main.min.css", "--style", "compressed"])
