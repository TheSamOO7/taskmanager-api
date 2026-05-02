import factory
from faker import Faker
from .models import Project, Task
from users.factories import UserFactory
from workspaces.factories import WorkspaceFactory

faker = Faker()


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    workspace = factory.SubFactory(WorkspaceFactory)
    name = factory.LazyFunction(faker.bs)
    description = factory.LazyFunction(faker.text)
    created_by = factory.SubFactory(UserFactory)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    project = factory.SubFactory(ProjectFactory)
    title = factory.LazyFunction(faker.sentence)
    description = factory.LazyFunction(faker.text)
    status = Task.Status.TODO
    priority = Task.Priority.MEDIUM
    created_by = factory.SubFactory(UserFactory)