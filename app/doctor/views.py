from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
#  from flask_mail import Message
#  from app.__init__ import mail

import sendgrid
import os
from sendgrid.helpers.mail import *

from . import doctor
#  from forms import DepartmentForm, EmployeeAssignForm, RoleForm
from .. import db
#  from ..models import Department, Employee, Role
from ..models import User

def check_admin():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)


def check_doctor():
    # prevent non-doctors from accessing the page
    if not current_user.is_doctor:
        abort(403)


# Patient Views

@doctor.route('/patients')
@login_required
def list_patients():
    """
    List all patients
    """
    check_doctor()

    #  users = User.query.all()
    return render_template('doctor/patients/patients.html', title='Patients')


# Notification Views

@doctor.route('/notifications')
@login_required
def list_notifications():
    """
    List all notifications
    """
    check_doctor()

    return render_template('doctor/notifications/notifications.html',
                            title='Notifications')




# Mail send test

@doctor.route("/mail")
@login_required
def send_mail():

    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("addictionhelp365@gmail.com")
    to_email = Email("c00198041@itcarlow.ie")
    subject = "Test subject"
    content = Content("text/plain", "If you are reading this.. It worked!!!!")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

    """
    msg = Message("Hello",
                  recipients=["kelly.mark.76@gmail.com"])

    mail.send(msg)
    """
    return "sent"


"""
# Department Views


@doctor.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments():

    #  List all departments

    check_admin()

    departments = Department.query.all()

    return render_template('doctor/departments/departments.html',
                           departments=departments, title="Departments")


@doctor.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():

    #  Add a department to the database

    check_admin()

    add_department = True

    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            flash('You have successfully added a new department.')
        except:
            # in case department name already exists
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('doctor.list_departments'))

    # load department template
    return render_template('doctor/departments/department.html', action="Add",
                           add_department=add_department, form=form,
                           title="Add Department")


@doctor.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):

    #  Edit a department

    check_admin()

    add_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the department.')

        # redirect to the departments page
        return redirect(url_for('doctor.list_departments'))

    form.description.data = department.description
    form.name.data = department.name
    return render_template('doctor/departments/department.html', action="Edit",
                           add_department=add_department, form=form,
                           department=department, title="Edit Department")


@doctor.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):

    #  Delete a department from the database

    check_admin()

    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('You have successfully deleted the department.')

    # redirect to the departments page
    return redirect(url_for('doctor.list_departments'))

    return render_template(title="Delete Department")


# Role Views


@doctor.route('/roles')
@login_required
def list_roles():
    check_admin()

    #  List all roles

    roles = Role.query.all()
    return render_template('doctor/roles/roles.html',
                           roles=roles, title='Roles')


@doctor.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():

    # Add a role to the database

    check_admin()

    add_role = True

    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)

        try:
            # add role to the database
            db.session.add(role)
            db.session.commit()
            flash('You have successfully added a new role.')
        except:
            # in case role name already exists
            flash('Error: role name already exists.')

        # redirect to the roles page
        return redirect(url_for('doctor.list_roles'))

    # load role template
    return render_template('doctor/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')


@doctor.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):

    #  Edit a role

    check_admin()

    add_role = False

    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()
        flash('You have successfully edited the role.')

        # redirect to the roles page
        return redirect(url_for('doctor.list_roles'))

    form.description.data = role.description
    form.name.data = role.name
    return render_template('doctor/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")


@doctor.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):

    #  Delete a role from the database

    check_admin()

    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('You have successfully deleted the role.')

    # redirect to the roles page
    return redirect(url_for('doctor.list_roles'))

    return render_template(title="Delete Role")


# Employee Views

@doctor.route('/employees')
@login_required
def list_employees():

    #  List all employees

    check_admin()

    employees = Employee.query.all()
    return render_template('doctor/employees/employees.html',
                           employees=employees, title='Employees')


@doctor.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_employee(id):

    #  Assign a department and a role to an employee

    check_admin()

    employee = Employee.query.get_or_404(id)

    # prevent admin from being assigned a department or role
    if employee.is_admin:
        abort(403)

    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department = form.department.data
        employee.role = form.role.data
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully assigned a department and role.')

        # redirect to the roles page
        return redirect(url_for('doctor.list_employees'))

    return render_template('doctor/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

"""
