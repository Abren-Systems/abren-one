from rest_framework import serializers


class CreateProgramRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)


class ProgramSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    is_active = serializers.BooleanField()


class ProgramDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    is_active = serializers.BooleanField()
