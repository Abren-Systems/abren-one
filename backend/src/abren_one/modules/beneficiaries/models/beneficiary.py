import uuid

from django.db import models

from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    BeneficiaryType,
    Gender,
    VulnerabilityLevel,
)
from abren_one.platform.common.models import OrgOwnedMixin, TimestampMixin


class Beneficiary(OrgOwnedMixin, TimestampMixin, models.Model):
    """An individual, household, or community receiving services (§4.1, §4.4)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beneficiary_type = models.CharField(
        max_length=50,
        choices=[(t.value, t.name) for t in BeneficiaryType],
        default=BeneficiaryType.INDIVIDUAL.value,
    )
    identification_number = models.CharField(max_length=100, blank=True, default="")
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    household_name = models.CharField(max_length=255, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[(g.value, g.name) for g in Gender],
        default=Gender.UNSPECIFIED.value,
    )
    status = models.CharField(
        max_length=50,
        choices=[(s.value, s.name) for s in BeneficiaryStatus],
        default=BeneficiaryStatus.ACTIVE.value,
        db_index=True,
    )
    vulnerability_level = models.CharField(
        max_length=50,
        choices=[(v.value, v.name) for v in VulnerabilityLevel],
        default=VulnerabilityLevel.MEDIUM.value,
    )
    contact_phone = models.CharField(max_length=50, blank=True, default="")
    contact_address = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "beneficiaries_beneficiary"
        ordering = ["last_name", "first_name", "household_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "identification_number"],
                condition=~models.Q(identification_number=""),
                name="unique_organization_beneficiary_id_number",
            )
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.beneficiary_type})"

    @property
    def display_name(self) -> str:
        if self.beneficiary_type == BeneficiaryType.HOUSEHOLD.value and self.household_name:
            return str(self.household_name)
        parts = [str(p) for p in (self.first_name, self.last_name) if p]
        return " ".join(parts) if parts else (str(self.household_name) or "Unnamed Beneficiary")

    @property
    def is_active(self) -> bool:
        return self.status == BeneficiaryStatus.ACTIVE.value
