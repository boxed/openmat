from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    Choices,
    EmailField,
    ForeignKey,
    ManyToManyField,
    Model,
    SET_NULL,
    TextChoices,
    UUIDField,
)


class BeltChoices(TextChoices):
    white = 'white', 'white'
    blue = 'blue', 'blue'
    purple = 'purple', 'purple'
    brown = 'brown', 'brown'
    black = 'black', 'black'


class User(AbstractUser):
    topics = ManyToManyField('Topic')
    belt = CharField(null=True, choices=BeltChoices.choices, max_length=255)


class Topic(Model):
    name = CharField(max_length=255)
    created_by = ForeignKey(User, null=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name


class LoginToken(Model):
    email = EmailField()
    uuid = UUIDField(default=uuid4, db_index=True)


class ScheduleItem(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    slot = CharField(max_length=10)

    def __repr__(self):
        return f'{self.user}/{self.slot}'
