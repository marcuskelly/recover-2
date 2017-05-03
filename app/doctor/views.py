from flask import g, request, abort, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_required
from datetime import datetime

import sendgrid
import os
from sendgrid.helpers.mail import *

from . import doctor
from .. import db
from ..models import User, Questionnaire, QuesAnswer, ProbAnswer, Release
from forms import CreateQuestionnaireForm, RegistrationForm
import pickle


def check_doctor():
    # prevent non-doctors from accessing the page
    if not current_user.is_doctor:
        abort(403)


# Patient Views

@doctor.route('/patients', methods=['GET', 'POST'])
@login_required
def list_patients():

    check_doctor()

    """
    List all patients for the current doctor
    """
    patients = User.query.filter_by(doctor_id=current_user.id)

    form = RegistrationForm()
    if form.validate_on_submit():
        patient = User(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data,
                            is_doctor=False,
                            doctor_id=current_user.id)

        # add patient to the database
        db.session.add(patient)
        db.session.commit()
        flash('You have successfully added a patient.', 'success')

        # redirect to the login page
        return redirect(url_for('doctor.list_patients'))

    return render_template('doctor/patients/patients.html',
                            patients=patients,
                            form=form,
                            title='Patients')


@doctor.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():

    check_doctor()

    #  patients = User.query.filter_by(doctor_id=current_user.id)

    form = RegistrationForm()
    if form.validate_on_submit():
        patient = User(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data,
                            is_doctor=False,
                            doctor_id=current_user.id)

        # add patient to the database
        db.session.add(patient)
        db.session.commit()
        flash('You have successfully added a patient.', 'success')

        # redirect to the list patients page
        return redirect(url_for('doctor.list_patients'))


    return render_template('doctor/patients/patient_add.html',
                            form=form,
                            title='Add Patient')



@doctor.route('/patients/<int:p_id>/remove', methods=['GET', 'POST'])
@login_required
def remove_patient(p_id):

    check_doctor()

    patient = User.query.get_or_404(p_id)
    db.session.delete(patient)
    db.session.commit()

    flash('You have successfully removed a patient.', 'success')

    return redirect(url_for('doctor.list_patients'))



@doctor.route('/patients/<int:p_id>/profile', methods=['GET', 'POST'])
@login_required
def patient_profile(p_id):

    check_doctor()

    patient = User.query.get(p_id)

    return render_template('doctor/patients/patient_profile.html',
                            patient=patient,
                            title='Patient Profile')



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


#  Questionnaire views

@doctor.route('/questionnaires')
@login_required
def list_questionnaires():

    check_doctor()

    questionnaires = Questionnaire.query.all()
    return render_template('doctor/questionnaire/questionnaire.html',
                            questionnaires=questionnaires,
                            title='Questionnaires')


@doctor.route('/questionnaires/create', methods = ['GET', 'POST'])
@login_required
def create_questionnaire():

    check_doctor()

    form = CreateQuestionnaireForm()

    if form.validate_on_submit():
        q = Questionnaire(title=form.title.data,
                    subject=form.subject.data,
                    description=form.description.data)

        # add questionnaire to the database
        db.session.add(q)
        db.session.commit()
        flash('Please add the questions.', 'info')

        # redirect
        return redirect(url_for('doctor.create_question',q_id=q.id))


    #  users = User.query.all()
    return render_template('doctor/questionnaire/questionnaire_create.html',
                            form=form,
                            title='Questionnaires')


@doctor.route('/questionnaires/<int:q_id>/create_question', methods=['GET', 'POST'])
@login_required
def create_question(q_id):

    check_doctor()

    def get_questions():
        questions = []
        current_index = 0
        while True:
            ques_form = 'ques_' + str(current_index)  #  example: ques_1
            if ques_form+'.type' in request.form:
                current_question = {
                                    "type": request.form[ques_form + '.type'],  # example:ques_7.type
                                    "description": request.form[ques_form + '.description'],    # example:ques_9.description
                                    "options": get_options(ques_form)
                                   }
                questions.append(current_question)
                current_index += 1
            else: break
        return questions

    def get_options(ques_form):
        options = []
        option_index = 0
        while True:
            option = ques_form + '.option_' + str(option_index)  #example: ques_3.option_3 'C.wow'
            if option in request.form:
                options.append(request.form[option])
                option_index += 1
            else: break
        return options

    q = Questionnaire.query.get(q_id)
    if not q:
        return "ERROR!"
    if request.method == 'POST':
        questions = get_questions()
        dumped_questions = pickle.dumps(questions, protocol = 2)
        q.schema = dumped_questions
        q.create_time = datetime.now()
        q.author_id = current_user.id

        db.session.add(q)
        db.session.commit()

        def get_security():
            def to_int(string):
                try: return int(string)
                except ValueError: return None

            security = {}

            is_allow_anonymous = False
            limit_num_participants = None
            limit_num_ip = None
            special_participants = None

            security['anonymous'] = is_allow_anonymous
            security['limit_per_user'] = limit_num_participants
            security['limit_per_ip'] = limit_num_ip
            security['limit_participants'] = special_participants

            return security

        security = get_security()
        dumped_security = pickle.dumps(security, protocol = 2)
        release = Release(ques_id = q_id,
            start_time =datetime.now(),
            security = dumped_security,
            is_closed = False)
        db.session.add(release)
        db.session.commit()
        flash('You have successfully created the questionnaire.', 'success')

        return redirect(url_for('doctor.list_questionnaires'))

    return render_template('doctor/questionnaire/questionnaire_create_question.html',
                            title='Create question')


@doctor.route('/questionnaire/<int:q_id>/preview')
@login_required
def preview(q_id):
    q = Questionnaire.query.get_or_404(q_id)

    if q.get_status() == 'Banned':
        return render_template('message.html',
                message = 'Sorry, the questionnaire is banned')

    schema = pickle.loads(q.schema)
    return render_template('doctor/questionnaire/questionnaire_preview.html',
            g = g,
            id = q.id,
            schema = schema,
            title = q.title,
            subject = q.subject,
            description = q.description)



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
