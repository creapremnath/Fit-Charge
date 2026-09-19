import os
import smtplib
import ssl
import logging
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import certifi
from app.core.config import settings


# Set up Jinja2 environment
# Get the directory of this file (app/services), go up to app/, then to mail_templates
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(base_dir, "mail_templates")
env = Environment(loader=FileSystemLoader(templates_dir))
logger = logging.getLogger(__name__)

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

        # Use certifi CA bundle to avoid platform trust-store issues.
        context = ssl.create_default_context(cafile=certifi.where())

        try:
            if settings.email_port == 587:
                # STARTTLS flow (commonly used on 587).
                with smtplib.SMTP(settings.email_host, settings.email_port) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                    smtp.login(self.email_sender, self.email_password)
                    smtp.sendmail(self.email_sender, receiver_email, em.as_string())
            else:
                # Implicit SSL flow (commonly used on 465).
                with smtplib.SMTP_SSL(settings.email_host, settings.email_port, context=context) as smtp:
                    smtp.login(self.email_sender, self.email_password)
                    smtp.sendmail(self.email_sender, receiver_email, em.as_string())
        except ssl.SSLCertVerificationError:
            # Local/dev fallback for machines with broken root cert setup.
            if not settings.debug:
                raise
            logger.warning("SSL certificate verification failed; retrying with unverified SSL context in debug mode.")
            insecure_context = ssl._create_unverified_context()
            with smtplib.SMTP_SSL(settings.email_host, settings.email_port, context=insecure_context) as smtp:
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
