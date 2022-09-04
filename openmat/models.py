from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    EmailField,
    Model,
    UUIDField,
)


class User(AbstractUser):
    pass


class LoginToken(Model):
    email = EmailField()
    uuid = UUIDField(default=uuid4, db_index=True)



