from uuid import uuid4

import pytest
from django.utils import timezone


@pytest.fixture
def user(django_user_model):
    def _create():
        user = django_user_model.objects.create_user(
            username=str(uuid4()),
            password='pass',
            email='test@example.com',
            first_name='First',
            last_name='Last',
            last_login=timezone.now(),
        )
        return user

    return _create
