from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    name = "abren_one.modules.organizations"
    label = "organizations"
    verbose_name = "Organizations"

    def ready(self) -> None:
        from uuid import UUID

        from abren_one.platform.tenancy.verifier import (
            MembershipInfo,
            register_membership_verifier,
        )

        class OrganizationMembershipVerifier:
            def get_membership(self, *, user_id: UUID, organization_id: UUID) -> MembershipInfo | None:
                from abren_one.modules.organizations.application.queries.get_membership import (
                    execute,
                )

                result = execute(organization_id=organization_id, user_id=user_id)
                if result is None:
                    return None
                return MembershipInfo(
                    organization_id=result.organization_id,
                    user_id=result.user_id,
                    role=result.role,
                    status=result.status,
                    is_active=result.is_active,
                )

        register_membership_verifier(OrganizationMembershipVerifier())
