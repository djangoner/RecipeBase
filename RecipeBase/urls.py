"""RecipeBase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from recipes.urls import router as router_recipes
from rest_framework import routers
from users.urls import router as router_users
from tasks.urls import router as router_tasks
from users.views import CustomObtainAuthToken
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

router = routers.DefaultRouter()
router_include = [router_recipes, router_users, router_tasks]

for sub_router in router_include:
    router.registry.extend(sub_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),
    #
    path("api/v1/", include(router.urls)),
    # Custom
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/auth/token/", CustomObtainAuthToken.as_view()),
    # url('', include('rest_framework.urls'), name="recipes"),
]

if getattr(settings, "TELEGRAM_BOT_ENABLE"):
    urlpatterns.append(path("", include("telegram_bot.urls")))

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {
                "document_root": settings.MEDIA_ROOT,
            },
        ),
    ]
if settings.DEBUGBAR:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
