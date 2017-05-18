"""
    Author: Mark Kelly
    Author: Danielle Gorman
"""

from flask import abort, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_
import random

from . import home
from .. import db
from ..models import User, ProbAnswer

from forms import *

"""
    Homepage route
"""
@home.route('/')
def homepage():
    return render_template('home/index.html', title="Welcome")


"""
    This route is for the patient dashboard
"""
@home.route('/dashboard')
@login_required
def dashboard():
    # prevent doctors from accessing the page
    if current_user.is_doctor:
        abort(403)
    #  Get a random quote
    quote = get_quote()
    return render_template('home/dashboard.html',
                            quote=quote,
                            title="Dashboard")

"""
    This route is for the Doctor dashboard
"""
@home.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    # prevent non-doctors from accessing the page
    if not current_user.is_doctor:
        abort(403)
    # Get all the stats for the dashboard
    total_patients = User.query.filter_by(doctor_id=current_user.id).count()
    total_yes = ProbAnswer.query.filter(and_(ProbAnswer.doctor_id==current_user.id, ProbAnswer.ans==0)).count()
    total_no = ProbAnswer.query.filter(and_(ProbAnswer.doctor_id==current_user.id, ProbAnswer.ans==1)).count()
    total_recovering = User.query.filter(and_(User.doctor_id==current_user.id, User.status=='Recovering')).count()
    total_at_risk = User.query.filter(and_(User.doctor_id==current_user.id, User.status=='At Risk')).count()
    total_alerts = User.query.filter(and_(User.doctor_id==current_user.id, User.status=='Alert')).count()
    return render_template('home/doctor_dashboard.html',
                            total_patients=total_patients,
                            total_yes=total_yes,
                            total_no=total_no,
                            total_recovering=total_recovering,
                            total_at_risk=total_at_risk,
                            total_alerts=total_alerts,
                            title="Dashboard")


"""
    This route is for users profile page
"""
@home.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    #  Get the current users's details
    user = User.query.get_or_404(current_user.id)
    #  Create all the forms for updating the details
    form = UpdateDetailsForm()
    emailForm = UpdateEmailForm()
    usernameForm = UpdateUsernameForm()
    firstnameForm = UpdateFirstnameForm()
    lastnameForm = UpdateLastnameForm()
    updatePasswordForm = UpdatePasswordForm()
    #  If the form is validated and submitted
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

    #  Populate the forms with data from the database
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


"""
    This function is reads in a file of quotes and returns a random one
"""
def get_quote():
    quotes = []
    with open('/home/recover/recover-2/app/quotes.txt') as quote_file:
        for line in quote_file:
            quote = line.strip()
            quotes.append(quote)
    return random.choice(quotes)
