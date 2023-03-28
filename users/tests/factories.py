import factory
from factory.django import DjangoModelFactory
from rest_framework.authtoken.models import Token
from recipes.models import User
from users.models import UserProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = "test123"
        if "password" in kwargs:
            password = kwargs.pop("password")

        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)


class TokenFactory(DjangoModelFactory):
    class Meta:
        model = Token
        django_get_or_create = ("user",)
