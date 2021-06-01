from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, ValidationError
from app.models import User

class NewUpdateActivityRecordForm(FlaskForm):
    subtype = SelectField("Gruppo vol.*", validators=[InputRequired()])
    user = SelectField("Volontario*", validators=[InputRequired()])
    date = DateField("Data*", validators=[InputRequired()])
    event = SelectField("Evento*", validators=[InputRequired()])
    activity = SelectField("Tipo di attività*", validators=[InputRequired()])
    start_time = TimeField("Inizio*", validators=[InputRequired()])
    end_time = TimeField("Fine*", validators=[InputRequired()])
    location = StringField("Luogo*", validators=[InputRequired()])
    notes = TextAreaField("Note", filters=[lambda x: x or None])
    submit = SubmitField("OK")

    def validate_end_time(form, end_time):
        """Check if end time is greater than start time."""
        if form.end_time.data <= form.start_time.data:
            raise ValidationError("L'orario di fine attività non può essere anteriore a quello d'inizio.")
