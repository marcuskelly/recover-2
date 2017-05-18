"""
    Author: Mark Kelly
    Author: Danielle Gorman
"""

import os
from flask import g, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from datetime import datetime
import pickle
from sqlalchemy import and_
import sendgrid
from sendgrid.helpers.mail import *

from . import patient
from .. import db
from ..models import User, Questionnaire, QuesAnswer, ProbAnswer


def check_doctor():
    # prevent doctors from accessing the page
    if current_user.is_doctor:
        abort(403)


"""
    This route is for the patient to fill a questionnare.
    Takes the questionnaire id as a parameter
"""
@patient.route('/questionnaires/<int:q_id>/fill',methods = ['GET','POST'])
@login_required
def fill(q_id):

    check_doctor()

    q = Questionnaire.query.get(q_id)
    if not q:
        flash('No questionnaires have been added', 'info')
        return redirect(url_for('home.dashboard'))
    if request.method == 'GET':
        schema = pickle.loads(q.schema)
        return render_template('questionnaire_fill.html',
            g = g,
            schema = schema,
            title = q.title,
            subject = q.subject,
            description = q.description)
    elif request.method == 'POST':
        questions = pickle.loads(q.schema)
        ans = QuesAnswer(ques_id = q.id,
                         user_id = current_user.id,
                         date = datetime.now())
        db.session.add(ans)
        db.session.commit()
        #  Fetch the answers from the form
        for prob_id in range(len(questions)):
            if ('ques_' + str(prob_id) + '.ans') not in request.form:
                flash('Please answer all questions', 'error')
                return render_template('questionnaire_fill.html',
                    g = g,
                    schema = questions,
                    title = q.title,
                    subject = q.subject,
                    description = q.description)
            else:
                p_ans = ProbAnswer(ques_ans_id = ans.id,
                                    prob_id = prob_id,
                                    doctor_id = current_user.doctor_id,
                                    ans = request.form['ques_' + str(prob_id) + '.ans'])
                db.session.add(p_ans)
        db.session.commit()
        #  get Doctor and patient details
        patient = User.query.get_or_404(current_user.id)
        doctor = User.query.filter_by(id=patient.doctor_id).first()
        #  Check the patients answers
        yes_count = ProbAnswer.query.filter(and_(ProbAnswer.ques_ans_id==ans.id, ProbAnswer.ans==0)).count()
        #  If too many negative answers, Email the Doctor and update patient status
        if yes_count > 7:
            patient.status = 'Alert'
            sg = sendgrid.SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
            from_email = Email("addictionhelp365@gmail.com")
            to_email = Email(doctor.email)
            subject = "Patient Status Changed - " + patient.first_name + " " + patient.last_name + "."
            content = Content("text/plain", "Dear " + doctor.first_name + ",\r\n\r\n" + patient.first_name + "'s status has changed to " + patient.status + ".\r\n\r\n\r\nRegards,\r\n\r\nRecover Team.")
            mail = Mail(from_email, subject, to_email, content)
            sg.client.mail.send.post(request_body=mail.get())
        elif yes_count > 3:
            patient.status = 'At Risk'
        else:
            patient.status = 'Recovering'
        db.session.add(patient)
        db.session.commit()
        flash('Thank you.', 'success')
        return redirect(url_for('home.dashboard'))
