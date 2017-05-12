
import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey='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')
from_email = Email("addictionhelp365@gmail.com")
to_email = Email("c00198041@itcarlow.ie")
subject = "Test subject"
content = Content("text/plain", "If you are reading this.. It worked!!!!")
mail = Mail(from_email, subject, to_email, content)
sg.client.mail.send.post(request_body=mail.get())

