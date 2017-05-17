from flask import g, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from datetime import datetime
import pickle
from sqlalchemy import and_

from . import doctor
from .. import db
from ..models import User, Questionnaire, QuesAnswer, ProbAnswer, Release
from forms import CreateQuestionnaireForm, RegistrationForm, UpdateAlertsForm


def check_doctor():
    # prevent non-doctors from accessing the page
    if not current_user.is_doctor:
        abort(403)


"""
    This route is for the Doctor to view patients,
    if the registration form is submitted, a new patient is
    added to the database
"""
@doctor.route('/patients', methods=['GET', 'POST'])
@login_required
def list_patients():

    check_doctor()

    #  List all patients for the current doctor
    patients = User.query.filter_by(doctor_id=current_user.id)

    #  Create a registration form
    form = RegistrationForm()

    #  If the form validates when submitted
    if form.validate_on_submit():
        #  Populate a patient object from the form
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
        # redirect to the patient page
        return redirect(url_for('doctor.list_patients'))
    return render_template('doctor/patients/patients.html',
                            patients=patients,
                            form=form,
                            title='Patients')

"""
    This view is for a Doctor to delete a patient,
    first a check is done to see if the patient has answered
    any questionnaires. The route takes the patient id as a parameter
"""
@doctor.route('/patients/<int:p_id>/remove', methods=['GET', 'POST'])
@login_required
def remove_patient(p_id):

    check_doctor()

    # Get the patient record
    patient = User.query.get_or_404(p_id)

    # Check if patient has answered any questionnaires
    ques_answers = QuesAnswer.query.filter_by(user_id=p_id).first()

    #  If the patient has answered questionnaires
    if ques_answers is not None:

        #  Get the patients answers
        prob_answers = ProbAnswer.query.filter_by(ques_ans_id=ques_answers.id).all()

        #  Delete each answer
        for o in prob_answers:
            db.session.delete(o)

        # Delete the record from the ques_answers table
        db.session.delete(ques_answers)

    # Delete the patient
    db.session.delete(patient)

    db.session.commit()
    flash('You have successfully removed a patient.', 'success')
    return redirect(url_for('doctor.list_patients'))

"""
    This route is for the Doctor to view a patients profile.
    A form allows the Doctor to update email settings.
    The route takes the patient id as a parameter
"""
@doctor.route('/patients/<int:p_id>/profile', methods=['GET', 'POST'])
@login_required
def patient_profile(p_id):

    check_doctor()

    patient = User.query.get(p_id)

    #  Create a form for alert settings
    form = UpdateAlertsForm()

    #  If the form is submitted
    if request.method == 'POST':
        #  Populate the patient object
        patient.allow_email=form.allow_alerts.data
        patient.days_before_email=form.days_before_alert.data
        #  Update the patient email settings
        db.session.add(patient)
        db.session.commit()

        flash('Alerts Updated.', 'info')
        return redirect(url_for('doctor.patient_profile',p_id=patient.id))

    #  Populate the form with data from the database
    form.allow_alerts.data = patient.allow_email
    form.days_before_alert.data = patient.days_before_email

    #  To store the patient's answers
    ques_answered = []
    ques_ans = {}
    #  Loop through the patients answers, and add them to a list
    for qa in patient.quesanswers:
        ques_ans[qa.ques_id] = qa
        ques_answered.append(ques_ans[qa.ques_id])

    #  Reverse the list
    ques_answered_desc = list(reversed(ques_answered))

    return render_template('doctor/patients/patient_profile.html',
                            patient=patient,
                            ques_ans_list = ques_answered,
                            form=form,
                            title='Patient Profile')

"""
    This route allows the Doctor to view the results of a questionnaire.
    The route takes two parameters, the patient id and the questionnaire id
"""
@doctor.route('/patients/<int:p_id>/<int:q_id>/result', methods=['GET', 'POST'])
@login_required
def patient_ques_result(p_id, q_id):

    check_doctor()

    patient = User.query.get(p_id)
    #  Get the questionnaire
    q = Questionnaire.query.first()
    date =  QuesAnswer.query.filter_by(id=q_id).first()
    #  Get the patient's answers
    answers = ProbAnswer.query.filter_by(ques_ans_id=q_id)
    #  Get the questions
    schema = pickle.loads(q.schema)
    
    yes_count = ProbAnswer.query.filter(and_(ProbAnswer.ques_ans_id==q_id, ProbAnswer.ans==0)).count()
    #  total_yes = ProbAnswer.query.filter(and_(ProbAnswer.doctor_id==patient.doctor_id, ProbAnswer.ans==0)).count()
    #  total_no = ProbAnswer.query.filter(and_(ProbAnswer.doctor_id==patient.doctor_id, ProbAnswer.ans==1)).count()
    no_count = ProbAnswer.query.filter(and_(ProbAnswer.ques_ans_id==q_id, ProbAnswer.ans==1)).count()

    return render_template('doctor/patients/patient_result.html',
                            g = g,
                            id = q.id,
                            schema = schema,
                            title = q.title,
                            subject = q.subject,
                            description = q.description,
                            patient = patient,
                            answers = answers,
                            date = date,
                            yes_count = yes_count,
                            no_count = no_count)


"""
    This route is for the Doctor to preview the questionnaire
"""
@doctor.route('/questionnaire/preview')
@login_required
def preview():

    #  Get the questionnaire
    q = Questionnaire.query.first()
    #  Get the questions
    schema = pickle.loads(q.schema)

    return render_template('doctor/questionnaire/questionnaire_preview.html',
            g = g,
            id = q.id,
            schema = schema,
            title = q.title,
            subject = q.subject,
            description = q.description)


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
        release = Release(ques_id = q_id)
        db.session.add(release)
        db.session.commit()
        flash('You have successfully created the questionnaire.', 'success')

        return redirect(url_for('doctor.list_questionnaires'))

    return render_template('doctor/questionnaire/questionnaire_create_question.html',
                            title='Create question')
