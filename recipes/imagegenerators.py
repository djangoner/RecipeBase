from imagekit import ImageSpec, register
from imagekit.processors import ResizeToCover


class BaseThumbnail(ImageSpec):
    processors = [ResizeToCover(width=200, height=200)]
    format = "JPEG"
    options = {"quality": 70}


class BaseWebpThumbnail(ImageSpec):
    processors = [ResizeToCover(width=200, height=200)]
    format = "WEBP"
    options = {"quality": 70}


class RecipeThumbnail(BaseThumbnail):
    pass


class RecipeWebpThumbnail(BaseWebpThumbnail):
    pass


class IngredientThumbnail(BaseThumbnail):
    pass


class IngredientWebpThumbnail(BaseWebpThumbnail):
    pass


register.generator("recipes:recipe:image_thumbnail", RecipeThumbnail)
register.generator("recipes:recipe:image_thumbnail_webp", RecipeWebpThumbnail)
register.generator("recipes:ingredient:image_thumbnail", IngredientThumbnail)
register.generator("recipes:ingredient:image_thumbnail_webp", IngredientWebpThumbnail)
