from flask import g, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from datetime import datetime
import pickle

from . import patient
from .. import db
from ..models import User, Questionnaire, QuesAnswer, ProbAnswer, Release


def check_doctor():
    # prevent doctors from accessing the page
    if current_user.is_doctor:
        abort(403)


@patient.route('/questionnaires')
@login_required
def list_questionnaires():

    check_doctor()

    return render_template('questionnaire.html', title='Questionnaire')


@patient.route('/questionnaires/<int:q_id>/fill',methods = ['GET','POST'])
def fill(q_id):
    q = Questionnaire.query.get(q_id)
    if not q:
        flash('No questionnaires have been added', 'info')
        return redirect(url_for('home.dashboard'))

    release = q.get_last_release()
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
                                    ans = request.form['ques_' + str(prob_id) + '.ans'])
                db.session.add(p_ans)
        db.session.commit()
        flash('Thank you.', 'success')
        return redirect(url_for('home.dashboard'))
