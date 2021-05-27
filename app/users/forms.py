from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.fields.html5 import EmailField, TelField, DateField
from wtforms.validators import InputRequired, Optional, ValidationError
from app.models import User

def only_numbers(form, data):
    """Validate if a string is made of digits (no text)."""
    if not data.data.isdecimal():
        raise ValidationError("Un numero di telefono non può contenere caratteri testuali.")

class NewUpdateUserForm(FlaskForm):
    subtype = SelectMultipleField("Tipologia volontario*", description="È possibile selezionare più tipologie di volontariato.", validators=[InputRequired()], coerce=int)
    firstname = StringField("Nome*", validators=[InputRequired()])
    lastname = StringField("Cognome*", validators=[InputRequired()])
    gender = SelectField("Genere")
    born_on = DateField("Nato il", validators=[Optional()])
    born_in = StringField("Nato a")
    zip = StringField("CAP", validators=[Optional(), only_numbers])
    city = StringField("Città")
    address = StringField("Indirizzo")
    email1 = EmailField("Indirizzo email*", validators=[InputRequired()])
    email2 = EmailField("Indirizzo email secondario")
    tel1 = TelField("Numero di telefono", validators=[Optional(), only_numbers])
    tel2 = TelField("Numero di telefono secondario", validators=[Optional(), only_numbers])
    notes = TextAreaField("Note", filters=[lambda x: x or None])
    submit = SubmitField("OK")

    def validate_email1(form, email1):
        """Check if already exists a user with the same primary email."""
        if User.query.filter_by(email1=email1.data).first():
            raise ValidationError("Esiste già un utente con questo indirizzo email primario.")

class ConfirmUserDeletionForm(FlaskForm):
    subtype = SelectMultipleField("Da quali gruppi si desidera rimuovere il volontario?", description="È possibile selezionare più gruppi. Selezionandoli tutti il volontario verrà rimosso dal sistema.", validators=[InputRequired()], coerce=int)
    submit = SubmitField('OK')
