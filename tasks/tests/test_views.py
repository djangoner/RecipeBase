from django.test import TestCase
from tasks.tests.factories import TaskCategoryFactory, TaskFactory
from django.contrib.auth.models import User


class ViewsTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(self) -> None:
        self.user = User.objects.create(username="testuser", is_superuser=True)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_task_categories_list(self):
        cat = TaskCategoryFactory()
        TaskFactory(category=cat)
        TaskFactory(category=cat)

        resp = self.client.get("/api/v1/task_category/")
        assert resp.status_code == 200
        resp_json = resp.json()

        assert resp_json["count"] == 1

    def test_task_categories_create(self):
        resp = self.client.post("/api/v1/task_category/", {"title": "test task category"})
        assert resp.status_code == 201
        resp_json = resp.json()

        assert resp_json["title"] == "test task category"

    def test_task_list(self):
        TaskFactory()

        resp = self.client.get("/api/v1/task/")
        assert resp.status_code == 200
        resp_json = resp.json()

        assert resp_json["count"] == 1

    def test_task_create(self):
        cat = TaskCategoryFactory()
        resp = self.client.post("/api/v1/task/", {"title": "test task", "category": cat.id})
        assert resp.status_code == 201
        resp_json = resp.json()

        assert resp_json["title"] == "test task"

    def test_task_nested_create(self):
        cat = TaskCategoryFactory()
        parent_task = TaskFactory(category=cat)

        resp = self.client.post("/api/v1/task/", {"title": "test task2", "category": cat.id, "parent": parent_task.id})
        assert resp.status_code == 201
        resp_json = resp.json()

        assert resp_json["title"] == "test task2"
        assert resp_json["parent"] == parent_task.id
        created_id = resp_json["id"]

        # Check parent task

        resp = self.client.get(f"/api/v1/task/{parent_task.id}/")
        assert resp.status_code == 200
        resp_json = resp.json()

        assert resp_json["childrens"][0]["id"] == created_id
