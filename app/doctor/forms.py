"""
    Author: Mark Kelly
    Author: Danielle Gorman
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.html5 import NumberInput

from ..models import User


"""
    Form for DOctors to register new patient
"""
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')

"""
    Form to allow Doctors to set patient Email settings
"""
class UpdateAlertsForm(FlaskForm):
    allow_alerts = BooleanField()
    days_before_alert = IntegerField(validators=[DataRequired()], widget=NumberInput())
    submit = SubmitField('Update Alerts')
