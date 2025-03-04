from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


# Function to send emails using SMTP
def send_email(subject: str, email_to: list, html_template: str, context: dict):
    html_content = get_template(html_template).render(context)
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=html_content,  
        from_email="noreply@yourdomain.com",
        to=email_to
    )
    
    msg.attach_alternative(html_content, "text/html") 
    msg.send(fail_silently=False)