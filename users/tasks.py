from smtplib import SMTPException

import jwt
from celery import shared_task
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from newsPortal.settings import SECRET_KEY as secret


from newsPortal import settings
from users.models import User


# def create_email_content(request, serializer, subject, template, password=None):
#     current_site = get_current_site(request)
#     message = render_to_string(template, {
#         'user': serializer,
#         'domain': current_site.domain,
#         'uid': urlsafe_base64_encode(force_bytes(serializer.data['id'])),
#         'password': urlsafe_base64_encode(force_bytes(password)),
#     })
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = serializer.data['email']
#     send_email_task.delay(subject, message, from_email, recipient_list)


@shared_task
def send_reset_password_email_task(recipient_email, password):
    recipient = User.objects.get(email=recipient_email)
    subject = 'Reset password.'
    payload = {"user_id": recipient.id, "password": password}
    token = jwt.encode(payload, secret, algorithm='HS256')
    message = render_to_string('reset_password.html', {
        'user': recipient,
        'domain': 'http://127.0.0.1:8000',
        'token': token
    })
    from_email = settings.EMAIL_HOST_USER

    try:
        email = EmailMessage(subject, message, from_email, [recipient_email])
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
            payload = {'user_id': user.id}
            token = jwt.encode(payload, secret, algorithm='HS256')
            message = render_to_string('invite_email.html', {
                'user': user,
                'domain': 'http://127.0.0.1:8000',
                'token': token
            })

            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return status.HTTP_200_OK
    except SMTPException as err:
        return Response(err, status.HTTP_400_BAD_REQUEST)


