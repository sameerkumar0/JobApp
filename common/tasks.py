from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_email(subject:str,email_to: list[str],html_templete,context):
    msg=EmailMultiAlternatives(
        subject=subject,from_email="noreply@talentb.com"
    )