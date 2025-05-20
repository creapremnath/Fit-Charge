import os
import smtplib
import ssl
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from config import settings


# Set up Jinja2 environment
templates_dir = os.path.join(os.getcwd(), "mail_templates")
env = Environment(loader=FileSystemLoader(templates_dir))

class MailEngine:
    def __init__(self, sender_email, sender_password):
        self.email_sender = sender_email
        self.email_password = sender_password

    def send_email(self, receiver_email, subject, html_content):
        # Create the email message
        em = EmailMessage()
        em['From'] = self.email_sender
        em['To'] = receiver_email
        em['Subject'] = subject
        em.set_content(html_content, subtype='html')

        # Set up the SSL context
        context = ssl.create_default_context()

        # Send the email using Gmail's SMTP server
        with smtplib.SMTP_SSL(settings.email_host,settings.email_port, context=context) as smtp:
            smtp.login(self.email_sender, self.email_password)
            smtp.sendmail(self.email_sender, receiver_email, em.as_string())

    def send_otp_email(self, receiver_email, otp):
        subject = 'Your OTP Verification Code'
        template = env.get_template("otp_template.html")
        html_content = template.render(otp=otp)
        self.send_email(receiver_email, subject, html_content)

    def send_welcome_email(self, receiver_email, user_name):
        subject = 'Welcome to Our Service'
        template = env.get_template("welcome_template.html")
        html_content = template.render(user_name=user_name)
        self.send_email(receiver_email, subject, html_content)

    def send_verification_success_email(self, receiver_email):
        subject = 'Verification Successful'
        template = env.get_template("verification_template.html")
        html_content = template.render()
        self.send_email(receiver_email, subject, html_content)
    def send_org_creation_success_mail(self, receiver_email,org_name,user_name):
        subject = 'Organization Created Successful'
        template = env.get_template("org_creation_success.html")
        html_content = template.render(org_name=org_name, user_name=user_name)
        self.send_email(receiver_email, subject, html_content)

    def reset_password_mail(self, receiver_email,user_name,reset_url):
        subject = 'Your qtools password has been reset.'
        template = env.get_template("reset_password_link.html")
        html_content = template.render(user_name=user_name,reset_url=reset_url)
        self.send_email(receiver_email, subject, html_content)


mail_engine = MailEngine(settings.email_user, settings.email_password)
