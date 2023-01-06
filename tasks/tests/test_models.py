from django.test import TestCase
from tasks.tests.factories import TaskCategoryFactory, TaskFactory


class ModelsTestCase(TestCase):
    def test_task_category(self):
        cat = TaskCategoryFactory()
        assert str(cat) == cat.title

    def test_task(self):
        task = TaskFactory()
        assert str(task) == task.title
