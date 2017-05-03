from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import User


class UpdateDetailsForm(FlaskForm):
    """
    Form for users to update details
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Save Changes')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError


class UpdateEmailForm(FlaskForm):
    """
    Form for users to update details
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    email_submit = SubmitField('Update Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')


class UpdateUsernameForm(FlaskForm):

    username = StringField('User Name', validators=[DataRequired()])
    username_submit = SubmitField('Update User Name')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')


class UpdateFirstnameForm(FlaskForm):

    first_name = StringField('First Name', validators=[DataRequired()])
    first_name_submit = SubmitField('Update First Name')


class UpdateLastnameForm(FlaskForm):

    last_name = StringField('Last Name', validators=[DataRequired()])
    last_name_submit = SubmitField('Update Last Name')


class UpdatePasswordForm(FlaskForm):

    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    update_password_submit = SubmitField('Update Password')
