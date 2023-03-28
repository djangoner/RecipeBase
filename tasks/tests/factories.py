import factory

from factory.django import DjangoModelFactory

from tasks.models import TaskCategory, Task


class TaskCategoryFactory(DjangoModelFactory):
    class Meta:
        model = TaskCategory

    title = factory.Faker("sentence")
    description = factory.Faker("text")


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence")
    description = factory.Faker("text")
    category = factory.SubFactory(TaskCategoryFactory)
