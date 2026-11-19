from rest_framework import serializers


class CreateProgramRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True, default=None)
    end_date = serializers.DateField(required=False, allow_null=True, default=None)


class UpdateProgramRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["planning", "active", "completed", "archived"],
        required=False,
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)


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


# --- Projects ---


class CreateProjectRequestSerializer(serializers.Serializer):
    program_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    budget_currency = serializers.CharField(max_length=3, required=False, default="USD")


class UpdateProjectRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["planning", "in_progress", "completed", "on_hold"],
        required=False,
    )
    budget_currency = serializers.CharField(max_length=3, required=False)


class ProjectSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    program_id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    budget_currency = serializers.CharField()


class ProjectDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    program_id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    budget_currency = serializers.CharField()


# --- Activities ---


class CreateActivityRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True, default=None)


class UpdateActivityRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "completed", "blocked"],
        required=False,
    )
    due_date = serializers.DateField(required=False, allow_null=True)


class ActivitySummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    due_date = serializers.DateField(allow_null=True, required=False)


class ActivityDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    due_date = serializers.DateField(allow_null=True, required=False)
