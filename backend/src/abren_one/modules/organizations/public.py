"""Public interface for the Organizations module (§3.1, §3.4).

Other modules must import ONLY from this file.
Cross-module ForeignKeys use string references ("organizations.Organization"),
not direct model imports.
"""

from abren_one.modules.organizations.application.commands.create_branch import (
    CreateBranchInput,
    CreateBranchResult,
)
from abren_one.modules.organizations.application.commands.create_branch import (
    execute as create_branch,
)
from abren_one.modules.organizations.application.commands.create_department import (
    CreateDepartmentInput,
    CreateDepartmentResult,
)
from abren_one.modules.organizations.application.commands.create_department import (
    execute as create_department,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    CreateOrganizationInput,
    CreateOrganizationResult,
)
from abren_one.modules.organizations.application.commands.create_organization import (
    execute as create_organization,
)
from abren_one.modules.organizations.application.queries.get_department import (
    GetDepartmentResult,
)
from abren_one.modules.organizations.application.queries.get_department import (
    execute as get_department,
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
from abren_one.modules.organizations.application.queries.list_departments import (
    DepartmentSummaryResult,
)
from abren_one.modules.organizations.application.queries.list_departments import (
    execute as list_departments,
)
from abren_one.modules.organizations.application.queries.list_members import (
    MemberSummaryResult,
)
from abren_one.modules.organizations.application.queries.list_members import (
    execute as list_members,
)
from abren_one.modules.organizations.domain.exceptions import (
    BranchNotFoundError,
    CannotRevokeLastOwnerError,
    DepartmentNotFoundError,
    MembershipNotFoundError,
    OrganizationError,
    OrganizationNotFoundError,
)

__all__ = [
    "BranchNotFoundError",
    "BranchSummaryResult",
    "CannotRevokeLastOwnerError",
    "CreateBranchInput",
    "CreateBranchResult",
    "CreateDepartmentInput",
    "CreateDepartmentResult",
    "CreateOrganizationInput",
    "CreateOrganizationResult",
    "DepartmentNotFoundError",
    "DepartmentSummaryResult",
    "GetDepartmentResult",
    "GetOrganizationResult",
    "MemberSummaryResult",
    "MembershipNotFoundError",
    "MembershipResult",
    "OrganizationError",
    "OrganizationNotFoundError",
    "create_branch",
    "create_department",
    "create_organization",
    "get_department",
    "get_organization",
    "get_user_membership",
    "list_branches",
    "list_departments",
    "list_members",
]
