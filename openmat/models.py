from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    UUIDField,
)


class User(AbstractUser):
    pass


class LoginToken(Model):
    email = EmailField()
    uuid = UUIDField(default=uuid4, db_index=True)


class ScheduleItem(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    slot = CharField(max_length=10)

    def __repr__(self):
        return f'{self.user}/{self.slot}'
