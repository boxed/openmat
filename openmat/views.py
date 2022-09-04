from django.contrib.auth import login
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from iommi import (
    Field,
    Form,
    Page,
)

from openmat.models import (
    LoginToken,
    User,
)


def index(request):
    times = []
    for i in range(6, 21):
        times.append(f'{i}:00')
        times.append(f'{i}:30')

    return render(
        request,
        template_name='index.html',
        context=dict(
            times=times,
        ),
    )


class Login(Form):
    class Meta:
        title = 'Login'

        @staticmethod
        def actions__submit__post_handler(form, **_):
            email = form.fields.email.value
            token = LoginToken.objects.create(email=email)
            send_mail(
                subject='Sign in to openmat',
                message=f'Sign in link: http://127.0.0.1:8004/sign_in/?code={token.uuid}',
                from_email='robot@killingar.net',
                recipient_list=[email],
            )
            return Page('Check your email for the login link')

    explanation = 'Write your email to sign up/login'
    email = Field.email()


def sign_in(request):
    token = LoginToken.objects.get(uuid=request.GET['code'])
    user, _ = User.objects.get_or_create(email=token.email)
    login(request, user)
    return HttpResponseRedirect('/')
