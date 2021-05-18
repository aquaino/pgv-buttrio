from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Accedi')

class NewEventForm(FlaskForm):
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')
