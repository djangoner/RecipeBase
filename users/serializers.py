from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ()


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    permissions = serializers.SerializerMethodField()

    _show_permissions = False

    def __init__(self, instance=None, *args, show_permissions: bool = False, **kwargs):
        super().__init__(instance, *args, **kwargs)
        self._show_permissions = show_permissions

    class Meta:
        model = User
        exclude = ["groups", "user_permissions", "is_superuser", "password"]
        read_only_fields = ["last_login", "date_joined", "is_staff"]
        depth = 1

    def get_permissions(self, obj) -> list[str]:
        if self._show_permissions:
            return sorted(obj.get_all_permissions())
        return []


class ShortUserSerializer(UserSerializer):
    profile = None  # type: ignore
