from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_email(template,context,subject,to_email):
    """
    Function to send emails
    """

    #render html template to string to pass it in email message
    html_message = render_to_string(template, context)

    #create object of email message
    message = EmailMessage(subject=subject, body=html_message, from_email=settings.EMAIL_HOST_USER, to=[to_email])

    #pass in the subtype as html so that html tags rendered when user open email
    message.content_subtype = 'html'

    # send email
    message.send()