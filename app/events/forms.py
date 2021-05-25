from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, ValidationError
from app.models import Event

class NewUpdateEventForm(FlaskForm):
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')

    def validate_name(form, name):
        """Validate the uniqueness of the event name."""
        if Event.query.filter_by(name=name.data).first():
            raise ValidationError("Esiste già un evento con questo nome.")
