"""Public interface for the Beneficiaries module (§3.1, §3.4).

Other modules must import ONLY from this file.
"""

from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    RecordServiceDeliveryInput,
    RecordServiceDeliveryResult,
)
from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    execute as record_service_delivery,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    RegisterBeneficiaryInput,
    RegisterBeneficiaryResult,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    execute as register_beneficiary,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    UpdateBeneficiaryInput,
    UpdateBeneficiaryResult,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    execute as update_beneficiary,
)
from abren_one.modules.beneficiaries.application.exceptions import (
    BeneficiaryError,
    BeneficiaryNotFoundError,
    InactiveBeneficiaryError,
    InvalidBeneficiaryTransitionError,
    InvalidDeliveryTransitionError,
    ServiceDeliveryNotFoundError,
)
from abren_one.modules.beneficiaries.application.queries.get_beneficiary import (
    GetBeneficiaryResult,
)
from abren_one.modules.beneficiaries.application.queries.get_beneficiary import (
    execute as get_beneficiary,
)
from abren_one.modules.beneficiaries.application.queries.get_service_delivery import (
    GetServiceDeliveryResult,
)
from abren_one.modules.beneficiaries.application.queries.get_service_delivery import (
    execute as get_service_delivery,
)
from abren_one.modules.beneficiaries.application.queries.list_beneficiaries import (
    BeneficiarySummaryResult,
)
from abren_one.modules.beneficiaries.application.queries.list_beneficiaries import (
    execute as list_beneficiaries,
)
from abren_one.modules.beneficiaries.application.queries.list_service_deliveries import (
    ServiceDeliverySummaryResult,
)
from abren_one.modules.beneficiaries.application.queries.list_service_deliveries import (
    execute as list_service_deliveries,
)

__all__ = [
    "BeneficiaryError",
    "BeneficiaryNotFoundError",
    "BeneficiarySummaryResult",
    "GetBeneficiaryResult",
    "GetServiceDeliveryResult",
    "InactiveBeneficiaryError",
    "InvalidBeneficiaryTransitionError",
    "InvalidDeliveryTransitionError",
    "RecordServiceDeliveryInput",
    "RecordServiceDeliveryResult",
    "RegisterBeneficiaryInput",
    "RegisterBeneficiaryResult",
    "ServiceDeliveryNotFoundError",
    "ServiceDeliverySummaryResult",
    "UpdateBeneficiaryInput",
    "UpdateBeneficiaryResult",
    "get_beneficiary",
    "get_service_delivery",
    "list_beneficiaries",
    "list_service_deliveries",
    "record_service_delivery",
    "register_beneficiary",
    "update_beneficiary",
]
