from django.shortcuts import render
from rest_framework import viewsets, permissions

from tasks.models import Task, TaskCategory
from tasks.serializers import TaskCategorySerializer, TaskSerializer, TaskNestedSerializer


class TaskCategoryViewset(viewsets.ModelViewSet):
    queryset = TaskCategory.objects.prefetch_related("childrens").filter(childrens__parent__isnull=True).distinct()
    serializer_class = TaskCategorySerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TaskViewset(viewsets.ModelViewSet):
    queryset = Task.objects.prefetch_related("childrens").all()
    serializer_class = TaskNestedSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
