from drf_spectacular.openapi import AutoSchema
from rest_flex_fields import FlexFieldsModelSerializer
from drf_spectacular.contrib.django_filters import DjangoFilterExtension


class DRFFlexFieldsSchema(DjangoFilterExtension):
    priority = 10
    # target_class = "rest_flex_fields.serializers.FlexFieldsModelSerializer"
    target_class = "django_filters.rest_framework.DjangoFilterBackend"
    match_subclasses = True

    static_fields = [
        {
            "in": "query",
            "name": "fields",
            "schema": {"type": "string"},
            "description": "Which fields should be returned",
        },
        {
            "in": "query",
            "name": "omit",
            "schema": {"type": "string"},
            "description": "Which fields should be excluded from results",
        },
        {
            "in": "query",
            "name": "expand",
            "schema": {"type": "string"},
            "description": "Which field should be expanded, comma separated",
        },
    ]
    # static_field = {
    #     "fields": {"type": "string", "title": "field"}
    # }

    def get_schema_operation_parameters(self, auto_schema: "AutoSchema", *args, **kwargs) -> list[dict]:
        serializer = auto_schema.get_request_serializer()
        res = super().get_schema_operation_parameters(auto_schema, *args, **kwargs)

        # Extend if flex serializer subclassed
        if issubclass(serializer.__class__, FlexFieldsModelSerializer):
            res.extend(self.static_fields)

        return res
