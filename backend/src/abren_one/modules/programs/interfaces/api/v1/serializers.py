from rest_framework import serializers


class CreateProgramRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True, default=None)
    end_date = serializers.DateField(required=False, allow_null=True, default=None)


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
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
