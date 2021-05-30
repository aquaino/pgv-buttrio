from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    gender = db.Column(db.String())
    born_on = db.Column(db.Date())
    born_in = db.Column(db.String())
    zip = db.Column(db.String())
    city = db.Column(db.String())
    address = db.Column(db.String())
    email1 = db.Column(db.String(), unique=True)
    email2 = db.Column(db.String())
    tel1 = db.Column(db.String())
    tel2 = db.Column(db.String())
    notes = db.Column(db.Text())
    admin = db.Column(db.Boolean(), default=False)
    password = db.Column(db.String())

class UserSubtype(db.Model):
    __tablename__ = "user_subtypes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'), nullable=False)
    type = db.relationship('UserType', backref=db.backref('user_subtypes', lazy=True))
    descr = db.Column(db.Text())

class UserType(db.Model):
    __tablename__ = "user_types"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(), nullable=False)
    descr = db.Column(db.Text())

class UserSubtypeAssociation(db.Model):
    __tablename__ = "user_subtype_associations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('user_subtype_associations', lazy=True))
    subtype_id = db.Column(db.Integer, db.ForeignKey('user_subtypes.id'), nullable=False)
    subtype = db.relationship('UserSubtype', backref=db.backref('user_subtype_associations', lazy=True))

class GreenBookCategory(db.Model):
    __tablename__ = "green_book_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    descr = db.Column(db.Text())

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    green_book_cat_id = db.Column(db.Integer, db.ForeignKey('green_book_categories.id'), nullable=False)
    green_book_cat = db.relationship('GreenBookCategory', backref=db.backref('events', lazy=True))
    name = db.Column(db.String(), nullable=False, unique=True)
    descr = db.Column(db.Text())

class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    descr = db.Column(db.Text())

class ActivityRecord(db.Model):
    __tablename__ = "activity_records"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('activity_records', lazy=True))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('activity_records', lazy=True))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    activity = db.relationship('Activity', backref=db.backref('activity_records', lazy=True))
    start_time = db.Column(db.Time(), nullable=False)
    end_time = db.Column(db.Time(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    notes = db.Column(db.Text())
