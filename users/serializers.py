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

    class Meta:
        model = User
        exclude = ["groups", "user_permissions", "is_superuser", "password"]
        read_only_fields = ["last_login", "date_joined", "is_staff"]
        depth = 1

class ShortUserSerializer(UserSerializer):
    profile = None
