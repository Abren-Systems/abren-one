from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    name = "abren_one.modules.organizations"
    label = "organizations"
    verbose_name = "Organizations"

    def ready(self) -> None:
        from abren_one.modules.organizations.infrastructure.verifier import (
            OrganizationMembershipVerifier,
        )
        from abren_one.platform.tenancy.verifier import register_membership_verifier

        register_membership_verifier(OrganizationMembershipVerifier())
