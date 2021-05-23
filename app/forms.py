from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Accedi')

class NewUpdateEventForm(FlaskForm):
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')

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
    email1 = StringField('Indirizzo email*', validators=[InputRequired()])
    email2 = StringField('Indirizzo email secondario')
    tel1 = StringField('Numero di telefono')
    tel2 = StringField('Numero di telefono secondario')
    notes = TextAreaField('Note', filters=[lambda x: x or None])
    submit = SubmitField('OK')

class ConfirmActionForm(FlaskForm):
    submit = SubmitField('OK')
