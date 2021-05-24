from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired

class NewUpdateEventForm(FlaskForm):
    gb_category = SelectField('Categoria Libro Verde*', validators=[InputRequired()])
    name = StringField('Nome*', validators=[InputRequired()])
    descr = TextAreaField('Descrizione', filters=[lambda x: x or None])
    submit = SubmitField('OK')
