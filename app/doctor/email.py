import sys

path = '/home/recover/recover-2'
if path not in sys.path:
    sys.path.append(path)

import sendgrid
from sendgrid.helpers.mail import *
import MySQLdb


db = MySQLdb.connect(host="",
                     user="",
                     passwd="",
                     db="")

cur = db.cursor()

cur.execute("SELECT * FROM users")

for row in cur.fetchall():
    print row[1]

db.close()

sg = sendgrid.SendGridAPIClient(apikey='')
from_email = Email("addictionhelp365@gmail.com")
to_email = Email("kelly.mark.76@gmail.com")
subject = "Test subject"
content = Content("text/plain", "If you are reading this.. It worked!!!!")
mail = Mail(from_email, subject, to_email, content)
sg.client.mail.send.post(request_body=mail.get())
