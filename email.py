
import sendgrid
import os
from sendgrid.helpers.mail import *

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
