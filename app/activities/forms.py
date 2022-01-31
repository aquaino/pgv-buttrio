from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, ValidationError

class NewUpdateActivityRecordForm(FlaskForm):
    subtype = SelectField("Tipologia volontario*", validators=[InputRequired()])
    user = SelectField("Volontario*", validators=[InputRequired()])
    date = DateField("Data*", validators=[InputRequired()])
    event = SelectField("Evento*", validators=[InputRequired()])
    activity = SelectField("Tipo di attività*", validators=[InputRequired()])
    start_time = TimeField("Inizio*", validators=[InputRequired()])
    end_time = TimeField("Fine*", validators=[InputRequired()])
    province = SelectField("Provincia*", validators=[InputRequired()])
    # Avoid validation because towns are loaded dynamically from file
    town = SelectField("Comune*", validators=[InputRequired()], validate_choice=False)
    location = StringField("Luogo")
    notes = TextAreaField("Note", filters=[lambda x: x or None])
    submit = SubmitField("OK")

    def validate_end_time(form, end_time):
        """Check if end time is greater than start time."""
        if form.end_time.data <= form.start_time.data:
            raise ValidationError("L'orario di fine attività non può precedere quello d'inizio.\
                                  Se l'attività è a cavallo tra due giorni è necessario suddividerla in due attività distinte.")
