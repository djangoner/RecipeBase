from rest_framework import serializers

from tasks.models import Task, TaskCategory


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        serializer.parent = None
        return serializer.data


class TaskNestedSerializer(serializers.ModelSerializer):
    childrens = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Task
        exclude = ()


class TaskSerializer(serializers.ModelSerializer):
    childrens = TaskNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        exclude = ()
        read_only_fields = ("author",)


class TaskCategorySerializer(serializers.ModelSerializer):
    childrens = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = TaskCategory
        exclude = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["childrens"] = [x for x in representation["childrens"] if not x["parent"]]
        return representation
