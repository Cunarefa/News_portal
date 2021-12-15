from smtplib import SMTPException

from celery import shared_task
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    try:
        email = EmailMessage(subject, message, from_email, [recipient_list])
        email.send()
        return status.HTTP_200_OK
    except SMTPException as err:
        return Response(err, status.HTTP_400_BAD_REQUEST)
