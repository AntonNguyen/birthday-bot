from common import get_email_content
from email.message import Message
from smtplib import SMTP
import datetime
import os

if __name__ == '__main__':
    content = get_email_content()

    if len(content) > 0:
        msg = Message()
        msg['Subject'] = 'Birthdays and Freshiversaries for ' + datetime.date.today().strftime('%B %-d, %Y') + ' [Preview]'
        msg['From'] = 'TimBot <timbot@freshbooks.com>'
        msg['To'] = 'clough@freshbooks.com'
        msg.add_header('Content-Type','text/html')
        msg.set_payload(content)

        smtp = SMTP('smtp.office365.com', 587)
        smtp.starttls()
        smtp.login('timbot@freshbooks.com', os.environ['TIMBOT_EMAIL_PASSWORD'])
        smtp.sendmail('timbot@freshbooks.com', [msg['To']], msg.as_string())
        smtp.quit()
