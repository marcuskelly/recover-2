from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import questionnaire
from . import doctor
from .. import db
from ..models import User


def check_doctor():
    # prevent non-doctors from accessing the page
    if not current_user.is_doctor:
        abort(403)


@questionnaire.route('/questionnaire')
@login_required
def list_questionnaire():
    """
    List all patients
    """
    check_doctor()

    #  users = User.query.all()
    return render_template('questionnaire/questionnaire.html', title='Questionnaire')


@questionnaire.route('/questionnaire/create')
@login_required
def create_questionnaire():
    """
    List all patients
    """
    check_doctor()

    #  users = User.query.all()
    return render_template('questionnaire/questionnaire_create.html', title='Questionnaire')

