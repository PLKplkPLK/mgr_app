from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

def send_activation_email(request, user):
    """
    Send account activation email to user
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(reverse('account:activate', kwargs={'uidb64': uid, 'token': token}))

    subject = 'Potwierdzenie maila - zwierzątka'
    message = f'Hej, aktywacja konta:\n{activation_link}'

    send_mail(subject, message, from_email=None, recipient_list=[user.email])
