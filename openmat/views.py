from django.contrib.auth import login
from django.core.mail import send_mail
from django.db.models import Count
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render
from iommi import (
    Field,
    Form,
    Page,
)

from openmat.models import (
    LoginToken,
    ScheduleItem,
    User,
)


def index(request):
    times = []
    for i in range(6, 21):
        times.append(f'{i}:00')
        times.append(f'{i}:30')

    weekdays = [
        'Mon',
        'Tus',
        'Wed',
        'Thu',
        'Fri',
        'Sat',
    ]

    return render(
        request,
        template_name='index.html',
        context=dict(
            times=times,
            weekdays=weekdays,
            selected=set(ScheduleItem.objects.filter(user=request.user).values_list('slot', flat=True)),
            counts={
                x['slot']: x['user__count']
                for x in ScheduleItem.objects.values('slot').annotate(Count('user'))
            },
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


def schedule_item(request):
    slot, _, on = request.body.decode().rpartition('-')
    if on == 'true':
        ScheduleItem.objects.get_or_create(user=request.user, slot=slot)
    else:
        ScheduleItem.objects.filter(user=request.user, slot=slot).delete()
    return HttpResponse('ok')
