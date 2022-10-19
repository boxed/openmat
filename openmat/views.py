from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.db.models import Count
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.template import Template
from django.utils.safestring import mark_safe
from iommi import (
    Field,
    Form,
    html,
    Page,
)

from openmat.models import (
    LoginToken,
    ScheduleItem,
    Topic,
    User,
)


class IndexPage(Page):
    # language=html
    content = Template('''
<h1>
    Times that work for me
</h1>

<table class="select">
    <thead>
        <tr>
            <th style="border: 0"></th>
            {% for weekday in weekdays %}
                <th>{{ weekday }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for time in times %}
            <tr data-time="{{ time }}">
                <td style="text-align: right; border-left: 0">{{ time }}</td>
                {% for weekday in weekdays %}
                    <td data-weekday="{{ weekday }}" {% selected %}>
                    </td>
                {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>

<h1>
    Overview of times that work for everyone
</h1>

<table class="overview">
    <thead>
        <tr>
            <th style="border: 0"></th>
            {% for weekday in weekdays %}
                <th>{{ weekday }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for time in times %}
            <tr data-time="{{ time }}">
                <th style="text-align: right; border-left: 0">{{ time }}</th>
                {% for weekday in weekdays %}
                    <td data-weekday="{{ weekday }}" {% selected %} onclick="show_people('{{ time }}-{{ weekday }}')">
                        {% count %}
                    </td>
                {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>
    ''')

    def get_context(self):
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

        return dict(
            **super().get_context(),
            times=times,
            weekdays=weekdays,
            selected=set(ScheduleItem.objects.filter(user=self.get_request().user).values_list('slot', flat=True)),
            counts={
                x['slot']: x['user__count']
                for x in ScheduleItem.objects.values('slot').annotate(Count('user'))
            },
        )

    # language=css
    style = html.style(mark_safe('''
        /* body {
            background-color: #383838;
            color: #efefef;
        }*/

        table {
            border-collapse: collapse;
        }
        td, th {
            border: 1px solid #6e6e6e;
            margin: 0;
            padding: 0.1rem;
            min-width: 2.2rem;
            text-align: center;
        }
        th {
            border-top: 0;
        }
        .select .selected {
            background: #41e157;
            color: black;
        }

        .overview .selected {
            border: 2px solid #41e157;
        }
    '''))

    # language=javascript
    script = html.script(mark_safe('''
        document.addEventListener('click', (event) => {
            if (!event.target.matches('td') || !event.target.parentElement.parentElement.parentElement.matches('.select')) {
                return;
            }
            let on;
            if (event.target.classList.contains('selected')) {
                event.target.classList.remove('selected');
                on = false;
            }
            else {
                event.target.classList.add('selected');
                on = true;
            }

            let time = event.target.parentElement.attributes['data-time'].value;
            let weekday = event.target.attributes['data-weekday'].value;

            fetch('/schedule_item/', {method: 'POST', body: `${time}-${weekday}-${on}`})
        });

        function show_people(key) {
            fetch(`/show_people/${key}/`).then((response) => {
                return response.json();
            })
            .then((data) => {
                alert(data.users);
            });
        }
    '''))


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
                message=f'Sign in link: {settings.BASE_URL}/sign_in/?code={token.uuid}',
                from_email='robot@killingar.net',
                recipient_list=[email],
            )
            return Page(parts__message='Check your email for the login link')

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


def show_people(request, slot):
    return JsonResponse(dict(users=[x.user.email for x in ScheduleItem.objects.filter(slot=slot).select_related('user')]))


class Settings(Form):
    class Meta:
        auto__model = User
        auto__include = ['first_name', 'last_name', 'belt', 'topics']
        instance = lambda request, **_: request.user
        # fields__topics__extra__handle_missing = lambda string_value, **_: Topic(name=string_value)


settings_view = Settings.edit().as_view()
