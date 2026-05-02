import factory
from faker import Faker
from .models import Workspace, WorkspaceMember
from users.factories import UserFactory

faker = Faker()


class WorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workspace

    name = factory.LazyFunction(faker.company)
    slug = factory.LazyFunction(faker.slug)
    owner = factory.SubFactory(UserFactory)


class WorkspaceMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkspaceMember

    workspace = factory.SubFactory(WorkspaceFactory)
    user = factory.SubFactory(UserFactory)
    role = WorkspaceMember.Role.MEMBER