## --------------------------------------------------------------------
## boiler controller
##
## Authors   : Yaron Weinsberg and Meir Tsvi
## License   : GPL Version 3
## --------------------------------------------------------------------
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## --------------------------------------------------------------------

import smtplib
import logging
import os
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from config import GMAIL_USER, GMAIL_PASSWORD

def send_email(recipient, subject, body, files=None):
    import smtplib

    FROM = GMAIL_USER
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = MIMEMultipart()
    message['From'] = FROM
    message['To'] = COMMASPACE.join(TO)
    #message['Date'] = formatdate(localtime=True)
    message['Subject'] = SUBJECT

    message.attach(MIMEText(TEXT))
    
    try:
        for f in files or []:
            with open(f, "rb") as fil:
       	       part = MIMEApplication(fil.read(), Name=basename(f))
    	       part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
    	       message.attach(part)

        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(GMAIL_USER, GMAIL_PASSWORD)
        smtpserver.sendmail(FROM, TO, message.as_string())
        smtpserver.close()
	logging.getLogger('BoilerLogger').debug('successfully sent the mail')
    except Exception as e:
        logging.getLogger('BoilerLogger').debug('failed to send mail:' + str(e))
