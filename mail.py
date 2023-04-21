import os
import smtplib as smtp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tokens import Tokens

root_folder = os.path.dirname(os.path.realpath(__file__))
with open("{}/psswrd.txt".format(root_folder), 'r') as f:
    db_password, email_password = f.readlines()
    db_password = db_password.rstrip()

tokens = Tokens()


class Mail:
    @staticmethod
    def recovery(email):
        server = smtp.SMTP_SSL('smtp.yandex.com')
        server.set_debuglevel(1)
        email_from = "schoolmathsite@yandex.ru"
        server.set_debuglevel(1)
        server.ehlo(email_from)
        server.login(email_from, email_password)
        server.auth_plain()
        msg = MIMEMultipart()
        token_forget_password = tokens.create(email, salt='forgetpassword')

        html = """\
                <html>
                  <head></head>
                  <body>
                    <p>Здравствуйте!<br>
                     <br>
                       Ваша ссылка для восстановления доступа к сайту: <a href="http://192.168.1.3:5000/new_password/{}">ссылка</a><br>
        
                       <br>Письмо сформировано автоматически и не требует ответа.</br>
                    </p>
                  </body>
                </html>
                """.format(str(token_forget_password))

        msg.attach(MIMEText(html, 'html'))
        to = email

        msg['Subject'] = "Математический сайт. Восстановление пароля."
        msg['From'] = email_from
        msg['To'] = to

        server.sendmail(email_from, to, msg.as_string())

        server.quit()

    @staticmethod
    def register(email):
        server = smtp.SMTP_SSL('smtp.yandex.com')
        server.set_debuglevel(1)
        email_from = "schoolmathsite@yandex.ru"
        server.set_debuglevel(1)
        server.ehlo(email_from)
        server.login(email_from, email_password)
        server.auth_plain()
        msg = MIMEMultipart()
        token = tokens.create(email, salt='email-confirm')

        html = """\
                                            <html>
                                              <head></head>
                                              <body>
                                                <p>Здравствуйте!<br>
                                                 <br>
                                                   Ваша ссылка для подтверждения e-mail: <a href="http://192.168.1.3:5000/confirm_email/{}">ссылка</a><br>

                                                   <br>Письмо сформировано автоматически и не требует ответа.</br>
                                                </p>
                                              </body>
                                            </html>
                                            """.format(str(token))

        msg.attach(MIMEText(html, 'html'))
        to = email

        msg['Subject'] = "Математический сайт. Подтверждение e-mail"
        msg['From'] = email_from
        msg['To'] = to

        server.sendmail(email_from, to, msg.as_string())

        server.quit()
