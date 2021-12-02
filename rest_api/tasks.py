from celery import shared_task
from django.core.mail import send_mail

from newsPortal import settings


@shared_task
def send_email_task(email):
    message = 'To confirm your email follow the link bellow.'
    subject = 'Account activation.'
    send_mail(subject=subject,
              message=message,
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email]
              )
    return 'Email has ben sent!'
