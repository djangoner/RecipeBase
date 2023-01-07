from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from recipes.models import Recipe
from django.db.models.query import QuerySet
from recipes.admin import RecipeAdmin


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


request = MockRequest()
request.user = MockSuperUser()  # type: ignore


class RecipesAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()

    def test_recipes_queryset(self):
        recipe = Recipe.objects.create()
        ma = RecipeAdmin(Recipe, self.site)

        qs = ma.get_queryset(request)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)
        self.assertIsNone(ma.get_cooked_times(recipe))
