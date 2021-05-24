from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

class NewUpdateUserForm(FlaskForm):
    subtype = SelectField('Tipologia utente*', validators=[InputRequired()])
    firstname = StringField('Nome*', validators=[InputRequired()])
    lastname = StringField('Cognome*', validators=[InputRequired()])
    gender = SelectField('Genere')
    born_on = StringField('Nato il')
    born_in = StringField('Nato a')
    zip = StringField('CAP')
    city = StringField('Città')
    address = StringField('Indirizzo')
    email1 = EmailField('Indirizzo email*', validators=[InputRequired()])
    email2 = EmailField('Indirizzo email secondario')
    tel1 = StringField('Numero di telefono')
    tel2 = StringField('Numero di telefono secondario')
    notes = TextAreaField('Note', filters=[lambda x: x or None])
    submit = SubmitField('OK')
