# Recipe: Add an API Endpoint

## Steps

### 1. Create or update the files in `interfaces/api/v1/`

**serializers.py** — input validation and output formatting:

```python
from rest_framework import serializers


class CreateProgramSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="")


class ProgramResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    is_active = serializers.BooleanField()
```

**views.py** — delegate to application layer:

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.platform.common.context import ExecutionContext, ActorType
from abren_one.modules.programs.application.commands import create_program


class CreateProgramView(APIView):
    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def post(self, request):
        serializer = CreateProgramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=request.user.id,
            organization_id=request.org_context.organization_id,
            correlation_id=request.correlation_id,
        )

        result = create_program.execute(
            create_program.CreateProgramInput(
                context=context,
                **serializer.validated_data,
            )
        )

        return Response(
            ProgramResponseSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )
```

**urls.py** — routing:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.CreateProgramView.as_view(), name="create-program"),
]
```

### 2. Include in root URL conf

```python
# config/urls.py
(path("api/v1/programs/", include("abren_one.modules.programs.interfaces.api.v1.urls")),)
```

### 3. Write API tests

```python
# modules/<module>/tests/api/test_create_program.py
```

## Rules
- Views do NOT contain business logic
- Serializers validate transport data only
- `ExecutionContext` constructed at the API boundary
- No direct ORM queries in views
