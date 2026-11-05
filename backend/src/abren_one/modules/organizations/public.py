"""Public interface for the Organizations module (§3.1, §3.4).

Other modules must import ONLY from this file.
Cross-module ForeignKeys use string references ("organizations.Organization"),
not direct model imports.
"""

from abren_one.modules.organizations.application.commands.create_organization import (
    CreateOrganizationInput,
    CreateOrganizationResult,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    execute as create_organization,
)
from abren_one.modules.organizations.application.queries.get_membership import (
    MembershipResult,
)
from abren_one.modules.organizations.application.queries.get_membership import (
    execute as get_user_membership,
)
from abren_one.modules.organizations.application.queries.get_organization import (
    GetOrganizationResult,
)
from abren_one.modules.organizations.application.queries.get_organization import (
    execute as get_organization,
)
from abren_one.modules.organizations.application.queries.list_branches import (
    BranchSummaryResult,
)
from abren_one.modules.organizations.application.queries.list_branches import (
    execute as list_branches,
)
from abren_one.modules.organizations.application.queries.list_members import (
    MemberSummaryResult,
)
from abren_one.modules.organizations.application.queries.list_members import (
    execute as list_members,
)
from abren_one.modules.organizations.domain.exceptions import (
    CannotRevokeLastOwnerError,
    MembershipNotFoundError,
    OrganizationError,
    OrganizationNotFoundError,
)

__all__ = [
    "BranchSummaryResult",
    "CannotRevokeLastOwnerError",
    "CreateOrganizationInput",
    "CreateOrganizationResult",
    "GetOrganizationResult",
    "MemberSummaryResult",
    "MembershipNotFoundError",
    "MembershipResult",
    "OrganizationError",
    "OrganizationNotFoundError",
    "create_organization",
    "get_organization",
    "get_user_membership",
    "list_branches",
    "list_members",
]
