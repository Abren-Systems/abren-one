"""Public interface for the Fundraising module (§3.1, §3.4).

Other modules must import ONLY from this file.
Cross-module ForeignKeys use string references ("fundraising.Donor", "fundraising.Grant"),
not direct model imports.
"""

from abren_one.modules.fundraising.application.commands.activate_grant import (
    ActivateGrantInput,
    ActivateGrantResult,
)
from abren_one.modules.fundraising.application.commands.activate_grant import (
    execute as activate_grant,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    AwardGrantInput,
    AwardGrantResult,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    execute as award_grant,
)
from abren_one.modules.fundraising.application.commands.close_grant import (
    CloseGrantInput,
    CloseGrantResult,
)
from abren_one.modules.fundraising.application.commands.close_grant import (
    execute as close_grant,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    CreateDonorInput,
    CreateDonorResult,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    execute as create_donor,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    CreateGrantInput,
    CreateGrantResult,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    execute as create_grant,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    RecordDonationInput,
    RecordDonationResult,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    execute as record_donation,
)
from abren_one.modules.fundraising.application.exceptions import (
    DonationNotFoundError,
    DonorNotFoundError,
    FundraisingError,
    GrantMismatchError,
    GrantNotFoundError,
    InactiveDonorError,
    InvalidDonationAmountError,
    InvalidStateTransitionError,
)
from abren_one.modules.fundraising.application.queries.get_donation import (
    GetDonationResult,
)
from abren_one.modules.fundraising.application.queries.get_donation import (
    execute as get_donation,
)
from abren_one.modules.fundraising.application.queries.get_donor import (
    GetDonorResult,
)
from abren_one.modules.fundraising.application.queries.get_donor import (
    execute as get_donor,
)
from abren_one.modules.fundraising.application.queries.get_grant import (
    GetGrantResult,
)
from abren_one.modules.fundraising.application.queries.get_grant import (
    execute as get_grant,
)
from abren_one.modules.fundraising.application.queries.list_donations import (
    DonationSummaryResult,
)
from abren_one.modules.fundraising.application.queries.list_donations import (
    execute as list_donations,
)
from abren_one.modules.fundraising.application.queries.list_donors import (
    DonorSummaryResult,
)
from abren_one.modules.fundraising.application.queries.list_donors import (
    execute as list_donors,
)
from abren_one.modules.fundraising.application.queries.list_grants import (
    GrantSummaryResult,
)
from abren_one.modules.fundraising.application.queries.list_grants import (
    execute as list_grants,
)

__all__ = [
    "ActivateGrantInput",
    "ActivateGrantResult",
    "AwardGrantInput",
    "AwardGrantResult",
    "CloseGrantInput",
    "CloseGrantResult",
    "CreateDonorInput",
    "CreateDonorResult",
    "CreateGrantInput",
    "CreateGrantResult",
    "DonationNotFoundError",
    "DonationSummaryResult",
    "DonorNotFoundError",
    "DonorSummaryResult",
    "FundraisingError",
    "GetDonationResult",
    "GetDonorResult",
    "GetGrantResult",
    "GrantMismatchError",
    "GrantNotFoundError",
    "GrantSummaryResult",
    "InactiveDonorError",
    "InvalidDonationAmountError",
    "InvalidStateTransitionError",
    "RecordDonationInput",
    "RecordDonationResult",
    "activate_grant",
    "award_grant",
    "close_grant",
    "create_donor",
    "create_grant",
    "get_donation",
    "get_donor",
    "get_grant",
    "list_donations",
    "list_donors",
    "list_grants",
    "record_donation",
]
