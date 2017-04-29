from flask import abort, render_template
from flask_login import current_user, login_required

from . import home

from ..models import User

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
    return render_template('home/dashboard.html', title="Dashboard")


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



