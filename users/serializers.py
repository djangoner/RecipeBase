from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ["groups", "user_permissions", "is_superuser", "password"]
        read_only_fields = ["last_login", "date_joined", "is_staff"]
        depth = 1
