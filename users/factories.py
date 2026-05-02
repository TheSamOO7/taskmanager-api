import factory
from faker import Faker
from django.contrib.auth import get_user_model

faker = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(faker.unique.email)
    full_name = factory.LazyFunction(faker.name)
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True