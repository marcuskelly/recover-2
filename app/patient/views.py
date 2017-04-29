from flask import g, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from datetime import datetime


from . import patient
from .. import db
from ..models import User, Questionnaire, QuesAnswer, ProbAnswer, Release
import pickle


def check_doctor():
    # prevent doctors from accessing the page
    if current_user.is_doctor:
        abort(403)


# Patient Views

@patient.route('/questionnaires')
@login_required
def list_questionnaires():

    check_doctor()

    #  users = User.query.all()
    return render_template('questionnaire.html', title='Questionnaire')


@patient.route('/questionnaires/<int:q_id>/fill',methods = ['GET','POST'])
def fill(q_id):
    q = Questionnaire.query.get(q_id)
    if not q:
        flash('No questionnaires have been added', 'info')
        return redirect(url_for('home.dashboard'))

    #begin access control
    if q.get_status() == 'Banned':
        return render_template('message.html',
                message = 'Sorry, the questionnaire is banned')
    if q.get_status() == 'Closed':
        return render_template('message.html',
                message = 'Sorry, the questionnaire is closed')
    if q.get_status() == 'In creating':
        return render_template('message.html',
                message = 'Sorry, the questionnaire is not ready yet')

    release = q.get_last_release()

    #end access control

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
        ans = QuesAnswer(
                         ques_id = q.id,
                         user_id = current_user.id,
                         ip = request.remote_addr,
                         date = datetime.now()
                         )
        db.session.add(ans)
        db.session.commit()
        for prob_id in range(len(questions)):
            if questions[prob_id]['type'] in ['0','2','3']:
                #single-selection, true/false ,or essay question
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
                                        ans = request.form['ques_' + str(prob_id) + '.ans'],  #example: ques_3.ans 2(that is, C)
                                        )
                    db.session.add(p_ans)
            elif questions[prob_id]['type'] == '1':
                #multi-selection
                for choice_id in range(len(questions[prob_id]["options"])):
                    if 'ques_' + str(prob_id) + '.ans_' + str(choice_id) in request.form: #example: ques_4.ans_7 which is a checkbox
                        p_ans = ProbAnswer(ques_ans_id = ans.id,
                                           prob_id = prob_id,
                                           ans = str(choice_id),
                                          )
                        db.session.add(p_ans)
        db.session.commit()
        flash('Thank you.', 'success')
        return redirect(url_for('home.dashboard'))


