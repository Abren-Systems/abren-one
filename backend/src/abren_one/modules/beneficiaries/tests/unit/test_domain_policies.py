from abren_one.modules.beneficiaries.domain.policies import (
    can_transition_beneficiary_status,
    can_transition_delivery_status,
)
from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    DeliveryStatus,
)


class TestBeneficiaryPolicies:
    def test_beneficiary_same_status_allowed(self) -> None:
        assert can_transition_beneficiary_status(BeneficiaryStatus.ACTIVE, BeneficiaryStatus.ACTIVE) is True

    def test_beneficiary_valid_transitions(self) -> None:
        assert can_transition_beneficiary_status(BeneficiaryStatus.ACTIVE, BeneficiaryStatus.SUSPENDED) is True
        assert can_transition_beneficiary_status(BeneficiaryStatus.ACTIVE, BeneficiaryStatus.GRADUATED) is True
        assert can_transition_beneficiary_status(BeneficiaryStatus.ACTIVE, BeneficiaryStatus.ARCHIVED) is True
        assert can_transition_beneficiary_status(BeneficiaryStatus.SUSPENDED, BeneficiaryStatus.ACTIVE) is True
        assert can_transition_beneficiary_status(BeneficiaryStatus.GRADUATED, BeneficiaryStatus.ACTIVE) is True

    def test_beneficiary_invalid_transitions(self) -> None:
        assert can_transition_beneficiary_status(BeneficiaryStatus.ARCHIVED, BeneficiaryStatus.ACTIVE) is False
        assert can_transition_beneficiary_status(BeneficiaryStatus.ARCHIVED, BeneficiaryStatus.SUSPENDED) is False

    def test_delivery_valid_transitions(self) -> None:
        assert can_transition_delivery_status(DeliveryStatus.PLANNED, DeliveryStatus.DELIVERED) is True
        assert can_transition_delivery_status(DeliveryStatus.PLANNED, DeliveryStatus.CANCELLED) is True

    def test_delivery_invalid_transitions(self) -> None:
        assert can_transition_delivery_status(DeliveryStatus.DELIVERED, DeliveryStatus.PLANNED) is False
        assert can_transition_delivery_status(DeliveryStatus.CANCELLED, DeliveryStatus.PLANNED) is False
