from django.test import SimpleTestCase
from tasks.tests.factories import TaskCategoryFactory, TaskFactory


class ModelsTestCase(SimpleTestCase):
    def test_task_category(self):
        cat = TaskCategoryFactory.build()
        assert str(cat) == cat.title

    def test_task(self):
        task = TaskFactory.build()
        assert str(task) == task.title
