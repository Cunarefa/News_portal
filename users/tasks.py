import uuid
from smtplib import SMTPException

import jwt
from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from newsPortal.settings import SECRET_KEY as secret

from newsPortal import settings
from users.models import User, InviteToken


def create_acc_activation_email(recipient_email):
    subject = 'Activate your account.'
    recipient = User.objects.get(email=recipient_email)
    payload = {"user_id": recipient.id}
    token = jwt.encode(payload, secret, algorithm='HS256')

    message = render_to_string('acc_activate_email.html', {
        'user': recipient,
        'domain': 'http://127.0.0.1:8000',
        'token': token
    })

    send_email_task.delay(subject, message, recipient)


def create_reset_password_email(recipient_email, password):
    subject = 'Reset password.'
    recipient = User.objects.get(email=recipient_email)
    payload = {"user_id": recipient.id, "password": password}
    token = jwt.encode(payload, secret, algorithm='HS256')

    message = render_to_string('reset_password.html', {
        'user': recipient,
        'domain': 'http://127.0.0.1:8000',
        'token': token
    })

    send_email_task.delay(subject, message, recipient)


@shared_task
def send_email_task(subject, message, recipient):
    from_email = settings.EMAIL_HOST_USER
    try:
        email = EmailMessage(subject, message, from_email, [recipient])
        email.send()
        return status.HTTP_200_OK
    except SMTPException as err:
        return Response(err, status.HTTP_400_BAD_REQUEST)


@shared_task
def send_invites_task(emails_list):
    try:
        subject = 'Invitation to cooperation.'
        for email in emails_list:
            user = User.objects.filter(email=email).first()
            token = InviteToken.objects.create(user=user, value=uuid.uuid4())
            message = render_to_string('invite_email.html', {
                'user': user,
                'domain': 'http://127.0.0.1:8000',
                'token': token.value
            })

            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return status.HTTP_200_OK
    except SMTPException as err:
        return Response(err, status.HTTP_400_BAD_REQUEST)
