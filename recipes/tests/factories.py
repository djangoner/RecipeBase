import factory
from factory.django import DjangoModelFactory

from recipes.models import (
    Ingredient,
    IngredientCategory,
    MealTime,
    ProductListItem,
    ProductListWeek,
    Recipe,
    RecipeImage,
    RecipeIngredient,
    RecipePlan,
    RecipePlanWeek,
    RecipeRating,
    RecipeTag,
    RegularIngredient,
    Shop,
    ShopIngredientCategory,
    User,
)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = "username"
    email = factory.Faker("email")


class RecipeFactory(DjangoModelFactory):
    class Meta:
        model = Recipe
        django_get_or_create = ("title",)

    title = factory.Faker("name")


class IngredientFactory(DjangoModelFactory):
    class Meta:
        model = Ingredient

    title = factory.Faker("name")
    description = factory.Faker("text")


class RecipeIngredientFactory(DjangoModelFactory):
    class Meta:
        model = RecipeIngredient

    ingredient = factory.SubFactory(IngredientFactory)
    amount = 0
    amount_type = "g"
    is_main = True


class RegularIngredientFactory(DjangoModelFactory):
    class Meta:
        model = RegularIngredient

    ingredient = factory.SubFactory(IngredientFactory)
    amount = 0
    amount_type = "g"


class RecipeImageFactory(DjangoModelFactory):
    class Meta:
        model = RecipeImage
        django_get_or_create = ("image",)

    recipe = factory.SubFactory(RecipeFactory)
    image = factory.django.ImageField()
    title = factory.Faker("name")


class RecipeTagFactory(DjangoModelFactory):
    class Meta:
        model = RecipeTag
        django_get_or_create = ("title",)

    title = factory.Faker("name")


class RecipeRatingFactory(DjangoModelFactory):
    class Meta:
        model = RecipeRating
        django_get_or_create = ("recipe", "user")

    user = factory.SubFactory(UserFactory)
    recipe = factory.SubFactory(RecipeFactory)
    rating = factory.Faker("pyint", min_value=1, max_value=5)


class MealTimeFactory(DjangoModelFactory):
    class Meta:
        model = MealTime
        django_get_or_create = ("title",)

    title = "Test meal"
    is_primary = True


class RecipePlanFactory(DjangoModelFactory):
    class Meta:
        model = RecipePlan
        django_get_or_create = ("week", "day")

    day = factory.Faker("pyint", min_value=1, max_value=7)
    meal_time = factory.SubFactory(MealTimeFactory)
    recipe = factory.SubFactory(RecipeFactory)


class ProductListItemFactory(DjangoModelFactory):
    class Meta:
        model = ProductListItem

    day = factory.Faker("pyint", min_value=1, max_value=7)
    ingredient = factory.SubFactory(IngredientFactory)
    description = factory.Faker("text")
    is_auto = True
    is_deleted = False
    is_completed = False


class RecipePlanWeekFactory(DjangoModelFactory):
    class Meta:
        model = RecipePlanWeek
        django_get_or_create = ("year", "week")

    year = factory.Faker("pyint", min_value=2000, max_value=2022)
    week = factory.Faker("pyint", min_value=1, max_value=53)

    # plans = factory.SubFactory(RecipePlanFactory)

    @factory.post_generation
    def plans(self, create, extracted):
        if not create:
            return
        if extracted:
            for plan in extracted:
                self.plans.add(plan)
        else:
            for i in range(7):
                self.plans.add(RecipePlanFactory(week=self, day=i + 1))


class ProductListWeekFactory(DjangoModelFactory):
    class Meta:
        model = ProductListWeek
        django_get_or_create = ("year", "week")

    year = factory.Faker("pyint", min_value=2000, max_value=2022)
    week = factory.Faker("pyint", min_value=1, max_value=53)

    @factory.post_generation
    def items(self, create, extracted):
        if not create:
            return
        if not extracted:
            return
        for plan in extracted:
            self.items.add(plan)


class ShopFactory(DjangoModelFactory):
    class Meta:
        model = Shop
        django_get_or_create = ("title",)

    title = factory.Faker("name")


class IngredientCategoryFactory(DjangoModelFactory):
    class Meta:
        model = IngredientCategory
        django_get_or_create = ("title",)

    title = factory.Faker("name")


class ShopIngredientCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ShopIngredientCategory
        django_get_or_create = ("shop", "category")

    shop = factory.SubFactory(ShopFactory)
    category = factory.SubFactory(IngredientCategoryFactory)
    num = factory.Faker("pyint", min_value=0, max_value=1000)
