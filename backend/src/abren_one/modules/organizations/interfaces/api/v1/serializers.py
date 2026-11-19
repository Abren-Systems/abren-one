from rest_framework import serializers


class CreateOrganizationRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=100)


class OrganizationResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()
    is_active = serializers.BooleanField()


class CreateBranchRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    is_headquarters = serializers.BooleanField(default=False)


class BranchResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    is_headquarters = serializers.BooleanField()
    is_active = serializers.BooleanField()


class CreateDepartmentRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    branch_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class DepartmentResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    branch_id = serializers.UUIDField(allow_null=True)
    name = serializers.CharField()
    code = serializers.CharField()
    is_active = serializers.BooleanField()


class AddMemberRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=["owner", "admin", "staff", "member"], default="member")


class MemberResponseSerializer(serializers.Serializer):
    membership_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    email = serializers.CharField()
    role = serializers.CharField()
    status = serializers.CharField()
    is_active = serializers.BooleanField()
