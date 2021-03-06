from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField, \
    HiddenField, BooleanField
from wtforms.fields.html5 import EmailField, TelField, DateField
from wtforms.validators import InputRequired, Optional, ValidationError

from app.models import User


def only_numbers(form, data):
    """Validate if a string is made of digits (no text)."""
    if not data.data.isdecimal():
        raise ValidationError("Un numero di telefono non può contenere caratteri testuali.")

class NewUserForm(FlaskForm):
    subtype = SelectMultipleField("Tipologia volontario*", description="È possibile selezionare più tipologie di volontariato.", validators=[InputRequired()], coerce=int)
    firstname = StringField("Nome*", validators=[InputRequired()])
    lastname = StringField("Cognome*", validators=[InputRequired()])
    gender = SelectField("Genere*", validators=[InputRequired()])
    born_on = DateField("Nato il", validators=[Optional()])
    region = SelectField("Regione*", validators=[InputRequired()])
    province = SelectField("Provincia*", validators=[InputRequired()])
    town = SelectField("Comune*", validators=[InputRequired()])
    address = StringField("Indirizzo", validators=[Optional()])
    email = EmailField("Indirizzo email*", validators=[InputRequired()])
    tel = TelField("Numero di telefono", validators=[Optional(), only_numbers])
    notes = TextAreaField("Note", filters=[lambda x: x or None])
    admin = BooleanField("Amministratore")
    password = PasswordField("Password", render_kw={"placeholder": "Imposta/modifica password"})
    submit = SubmitField("OK")

    def validate_email(form, email):
        """Check if already exists a user with the same primary email."""
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Esiste già un utente con questo indirizzo email primario.")

    def validate_password(form, password):
        """Check if the given password is empty, only if the user doesn't have already a password and if the admin checkbox is flagged."""
        if (form.admin.data is True) and (not password.data) and (not User.query.filter_by(email=form.email.data).first().password):
            raise ValidationError("Password non specificata.")

class UpdateUserForm(NewUserForm):
    id = HiddenField()
    def validate_email(form, email):
        """Check if already exists a user with the same primary email."""
        searched_by_email = User.query.filter_by(email=email.data).first()
        if searched_by_email and searched_by_email.id != int(form.id.data):
            raise ValidationError("Esiste già un utente con questo indirizzo email primario.")

class ConfirmUserDeletionForm(FlaskForm):
    subtype = SelectMultipleField("Da quali gruppi si desidera rimuovere il volontario?", description="È possibile selezionare più gruppi. Selezionandoli tutti il volontario verrà rimosso dal sistema.", validators=[InputRequired()], coerce=int)
    submit = SubmitField('OK')
