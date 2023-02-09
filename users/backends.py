from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from drf_spectacular.authentication import SessionScheme
from rest_framework import pagination
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response

UserModel = get_user_model()


class TotalPagesPageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class CsrfExemptSessionAuthenticationScheme(SessionScheme):
    target_class = "users.backends.CsrfExemptSessionAuthentication"


class CustomAuthorizationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        try:
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
        except UserModel.DoesNotExist:
            pass
        else:
            if password and user.check_password(password) and self.user_can_authenticate(user):
                return user


class CustomTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"
