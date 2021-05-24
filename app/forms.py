from flask_wtf import FlaskForm
from wtforms import SubmitField

class ConfirmActionForm(FlaskForm):
    submit = SubmitField('OK')
