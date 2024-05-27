import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.text import MIMEText

from dotenv import load_dotenv

from BACKEND.models.config import PATH

load_dotenv()


class SMTP:

    def __init__(self, send_gmail):
        self.msg = MIMEMultipart("alternative")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.sender = os.getenv("EMAIL")
        self.receiver = send_gmail
        self.msg['From'] = formataddr(['no-reply', os.getenv("EMAIL")])
        self.msg['To'] = send_gmail

    def send_email_for_password(self, url, token):
        try:
            self.msg['Subject'] = "Восстановление данных"
            with open(f"{PATH}/BACKEND/html/forgot_password.html", encoding="UTF-8") as f:
                email_content = f.read()
            email_content = email_content.replace("SESSION_TOKEN", token).replace("URL_FOR_SERVER", url)
            email_content = MIMEText(email_content, "html", "utf-8")
            self.msg.attach(email_content)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.mail.ru", 465, context=context) as server:
                server.login(self.sender, self.password)
                server.sendmail(
                    self.msg['From'], self.msg['To'], self.msg.as_string()
                )
            return True
        except Exception as e:
            print("Cбой (send_email_for_password)" + '\n' + str(e))
            return False
