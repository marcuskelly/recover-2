from flask import abort, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
import random

from . import home
from .. import db
from ..models import User

from forms import *

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")


@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    quote = get_quote()

    return render_template('home/dashboard.html',
                            quote=quote,
                            title="Dashboard")


@home.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_doctor:
        abort(403)

    number_of_patients = User.query.filter_by(doctor_id=current_user.id).count()

    return render_template('home/doctor_dashboard.html',
                            number_of_patients=number_of_patients,
                            title="Dashboard")


@home.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = User.query.get_or_404(current_user.id)

    form = UpdateDetailsForm()
    emailForm = UpdateEmailForm()
    usernameForm = UpdateUsernameForm()
    firstnameForm = UpdateFirstnameForm()
    lastnameForm = UpdateLastnameForm()
    updatePasswordForm = UpdatePasswordForm()

    if form.submit.data and form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.first_name=form.first_name.data
        user.last_name=form.last_name.data
        user.password=form.password.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your details.', 'success')

        return redirect(url_for('home.profile'))

    if emailForm.email_submit.data and emailForm.validate_on_submit():
        user.email=form.email.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your email.', 'success')

        return redirect(url_for('home.profile'))

    if usernameForm.username_submit.data and usernameForm.validate_on_submit():
        user.username=form.username.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your User Name.', 'success')

        return redirect(url_for('home.profile'))

    if firstnameForm.first_name_submit.data and firstnameForm.validate_on_submit():
        user.first_name=form.first_name.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your First Name.', 'success')

        return redirect(url_for('home.profile'))

    if lastnameForm.last_name_submit.data and lastnameForm.validate_on_submit():
        user.last_name=form.last_name.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your Last Name.', 'success')

        return redirect(url_for('home.profile'))

    if updatePasswordForm.update_password_submit.data and updatePasswordForm.validate_on_submit():
        user.password=form.password.data
        db.session.add(user)
        db.session.commit()
        flash('You have successfully updated your Password.', 'success')

        return redirect(url_for('home.profile'))

    emailForm.email.data = user.email
    usernameForm.username.data = user.username
    firstnameForm.first_name.data = user.first_name
    lastnameForm.last_name.data = user.last_name

    return render_template('home/profile.html',
                            form=form,
                            emailForm=emailForm,
                            usernameForm=usernameForm,
                            firstnameForm=firstnameForm,
                            lastnameForm=lastnameForm,
                            updatePasswordForm=updatePasswordForm,
                            user=user,
                            title="Profile")


def get_quote():
    quotes = []
    with open('/home/recover/recover-2/app/quotes.txt') as quote_file:
        for line in quote_file:
            quote = line.strip()
            print(quote)
            quotes.append(quote)

    return random.choice(quotes)
