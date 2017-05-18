"""
    Author: Mark Kelly
    Author: Danielle Gorman
"""

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import auth
from forms import LoginForm, RegistrationForm
from .. import db
from ..models import User

"""
    This route is for users to register
"""
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data)

        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.', 'success')
        # redirect to the login page
        return redirect(url_for('auth.login'))
    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


"""
    This route is for users to login
"""
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if employee exists in the database and if
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            # log user in
            login_user(user)
            flash('You have successfully been logged in.', 'success')
            # redirect to the appropriate dashboard page
            if user.is_doctor:
                return redirect(url_for('home.doctor_dashboard'))
            else:
                return redirect(url_for('home.dashboard'))
        # when login details are incorrect
        else:
            flash('Invalid email or password.', 'error')
    # load login template
    return render_template('auth/login.html',
                            form=form,
                            title='Login')

"""
    This route is for loging out
"""
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully been logged out.', 'success')
    # redirect to the login page
    return redirect(url_for('auth.login'))
