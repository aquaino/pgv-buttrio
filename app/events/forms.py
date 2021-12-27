from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import InputRequired, ValidationError

from app.models import Event


class NewEventForm(FlaskForm):
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')

    def validate_name(form, name):
        """Validate the uniqueness of the event name."""
        if Event.query.filter_by(name=name.data).first():
            raise ValidationError("Esiste già un evento con questo nome.")

class UpdateEventForm(FlaskForm):
    id = HiddenField()
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')

    def validate_name(form, name):
        """Validate the uniqueness of the event name."""
        searched_by_name = Event.query.filter_by(name=name.data).first()
        if searched_by_name and searched_by_name.id != int(form.id.data):
            raise ValidationError("Esiste già un evento con questo nome.")
