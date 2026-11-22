import uuid
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestFinanceAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username="finance_officer", password="secretpassword")
        self.client.force_authenticate(user=self.user)

        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.user.id,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        self.org_result = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Horn Relief Finance",
                slug=f"horn-relief-{uuid.uuid4().hex[:6]}",
            )
        )
        self.org_id = self.org_result.organization_id

    def test_account_creation_and_listing(self) -> None:
        # Create cash account
        resp = self.client.post(
            "/api/v1/finance/accounts/",
            {
                "code": "1010",
                "name": "Operating Cash",
                "account_type": "asset",
                "currency": "USD",
                "description": "Primary checking account",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert resp.status_code == status.HTTP_201_CREATED
        acc_id = resp.data["account_id"]

        # Detail query
        detail_resp = self.client.get(
            f"/api/v1/finance/accounts/{acc_id}/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.data["code"] == "1010"

        # List query
        list_resp = self.client.get(
            "/api/v1/finance/accounts/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert list_resp.status_code == status.HTTP_200_OK
        assert len(list_resp.data) == 1

    def test_journal_entry_post_and_trial_balance_api(self) -> None:
        # Create accounts
        cash_resp = self.client.post(
            "/api/v1/finance/accounts/",
            {"code": "1010", "name": "Cash", "account_type": "asset", "currency": "USD"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        rev_resp = self.client.post(
            "/api/v1/finance/accounts/",
            {"code": "4010", "name": "Grant Revenue", "account_type": "revenue", "currency": "USD"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )

        cash_id = cash_resp.data["account_id"]
        rev_id = rev_resp.data["account_id"]

        # Create draft journal entry
        je_resp = self.client.post(
            "/api/v1/finance/journal-entries/",
            {
                "entry_date": "2026-11-22",
                "memo": "Received UNICEF emergency grant",
                "currency": "USD",
                "lines": [
                    {"account_id": cash_id, "debit": "75000.00", "credit": "0.00"},
                    {"account_id": rev_id, "debit": "0.00", "credit": "75000.00"},
                ],
                "post_immediately": False,
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert je_resp.status_code == status.HTTP_201_CREATED
        entry_id = je_resp.data["journal_entry_id"]
        assert je_resp.data["status"] == "draft"

        # Post the entry
        post_resp = self.client.post(
            f"/api/v1/finance/journal-entries/{entry_id}/post/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert post_resp.status_code == status.HTTP_200_OK
        assert post_resp.data["status"] == "posted"

        # Query Trial Balance
        tb_resp = self.client.get(
            "/api/v1/finance/trial-balance/",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert tb_resp.status_code == status.HTTP_200_OK
        assert tb_resp.data["is_balanced"] is True
        assert Decimal(tb_resp.data["total_debits"]) == Decimal("75000.00")
        assert Decimal(tb_resp.data["total_credits"]) == Decimal("75000.00")

        # Reverse the journal entry
        rev_resp = self.client.post(
            f"/api/v1/finance/journal-entries/{entry_id}/reverse/",
            {"reason": "Incorrect allocation category"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.org_id),
        )
        assert rev_resp.status_code == status.HTTP_200_OK
        assert rev_resp.data["reversal_entry_number"].startswith("REV-")

    def test_unauthorized_without_organization_context(self) -> None:
        resp = self.client.get("/api/v1/finance/accounts/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
