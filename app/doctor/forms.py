from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from flask.ext.wtf.html5 import NumberInput

from ..models import User


# Questionnaire forms

class CreateQuestionnaireForm(FlaskForm):

    #  Form to create questionnaire

    title = StringField('Title', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit details and add questions')


class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
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

class UpdateAlertsForm(FlaskForm):

    #  Form to update patient alerts

    allow_alerts = BooleanField()
    days_before_alert = IntegerField(validators=[DataRequired()], widget=NumberInput())
    #  IntegerField('Telephone', [validators.NumberRange(min=0, max=10)])


    #  days_before_alert = IntegerField(validators=[DataRequired(), NumberRange(min=0, max=10)])


    submit = SubmitField('Update Alerts')

