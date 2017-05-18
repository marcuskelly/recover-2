"""
    Author: Mark Kelly
    Author: Danielle Gorman
"""

import sys
import sendgrid
from sendgrid.helpers.mail import *
import MySQLdb

path = '/home/recover/recover-2'
if path not in sys.path:
    sys.path.append(path)

#  Email settings
sg = sendgrid.SendGridAPIClient(apikey='secret')
from_email = Email("addictionhelp365@gmail.com")

#  Connect to the database
db = MySQLdb.connect(host="recover.mysql.pythonanywhere-services.com",
                     user="recover",
                     passwd="secret",
                     db="recover$recover_db")


cur = db.cursor() #  This cursor is for the patient details
cur2 = db.cursor() #  This cursor is for the Doctor details

#  Get all users, for a Doctor id, that have "Allow Email" on, where the number of days since a questionnare is greater than the allowed days.
cur.execute("select users.email, users.first_name, users.last_name, users.doctor_id, users.days_before_email, datediff(now(),max(ques_answers.date)), max(ques_answers.date), datediff(now(),users.confirmed_at) from users left join ques_answers on users.id=ques_answers.user_id where not users.is_doctor and users.allow_email group by users.email;")

for row in cur.fetchall():
    email = row[0]
    first_name = row[1]
    last_name = row[2]
    doctor_id = row[3]
    days_before_email = row[4]
    days_since_questionnaire = row[5]
    date = row[6]
    confirmed_at = row[7]

    #  Get the Doctor's contact details
    cur2.execute("select email, first_name from users where id =" + str(doctor_id) + "")
    for row2 in cur2.fetchall():
        doctor_email = row2[0]
        doctor_first_name = row2[1]

    # Check how many days before a new patient answers their first questionnaire
    if days_since_questionnaire is None and confirmed_at >= days_before_email:
        #  Email the patient
        to_email = Email(email)
        subject = "Questionnaire"
        content = Content("text/plain", "Dear " + first_name + ",\r\n\r\nYou have not answered a questionnaire yet. Please visit http://recover.pythonanywhere.com\r\n\r\n\r\nRegards,\r\n\r\nRecover Team." )
        mail = Mail(from_email, subject, to_email, content)
        sg.client.mail.send.post(request_body=mail.get())

        #  Email the doctor
        to_email = Email(doctor_email)
        subject = "Patient Notification - " + first_name + " " + last_name + "."
        content = Content("text/plain", "Dear " + doctor_first_name + ",\r\n\r\n" + first_name + " has been a patient for " + str(confirmed_at) + " days and has not yet answered a questionnaire.\r\n\r\n\r\nRegards,\r\n\r\nRecover Team." )
        mail = Mail(from_email, subject, to_email, content)
        sg.client.mail.send.post(request_body=mail.get())

    #  Check if the number of days since a questionnaire was answered
    #  is greater than or equal to the days allowed
    elif days_since_questionnaire >= days_before_email:
        #  Email the patient
        to_email = Email(email)
        subject = "Questionnaire"
        content = Content("text/plain", "Dear " + first_name + ",\r\n\r\nIt's been " + str(days_since_questionnaire) + " days since your last questionnaire. Please visit http://recover.pythonanywhere.com\r\n\r\n\r\nRegards,\r\n\r\nRecover Team." )
        mail = Mail(from_email, subject, to_email, content)
        sg.client.mail.send.post(request_body=mail.get())

        #  Email the Doctor
        to_email = Email(doctor_email)
        subject = "Patient Notification - " + first_name + " " + last_name + "."
        content = Content("text/plain", "Dear " + doctor_first_name + ",\r\n\r\nIt's been " + str(days_since_questionnaire) + " days since " + first_name + "'s last questionnaire.\r\n\r\n\r\nRegards,\r\n\r\nRecover Team." )
        mail = Mail(from_email, subject, to_email, content)
        sg.client.mail.send.post(request_body=mail.get())

db.close()
