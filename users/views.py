from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import render
from drf_spectacular.utils import (OpenApiResponse, extend_schema,
                                   inline_serializer)
from rest_framework import (decorators, permissions, response, serializers,
                            viewsets)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from users.serializers import UserSerializer

User = get_user_model()


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "is_admin": user.is_staff})


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by(F("profile__num").asc(nulls_last=True))
    permission_classes = [
        permissions.IsAdminUser | permissions.IsAuthenticatedOrReadOnly
    ]

    search_fields = ["fio", "username", "phone"]
    ordering_fields = ["username", "fio", "birthdate", "employment_date", "hour_rate", "profile__num"]
    filter_fields = ["is_active"]
    http_method_names = ["get", "post", "put", "patch"]

    # def get_queryset(self):
    #     return super().get_queryset().exclude(id=self.request.user.id)

    @extend_schema(
        request=None,
        responses={200: UserSerializer},
    )
    @decorators.action(
        ["GET"], detail=False, permission_classes=[permissions.IsAuthenticated]
    )
    def current_user_info(self, request):
        user = request.user

        return response.Response(UserSerializer(user).data)
