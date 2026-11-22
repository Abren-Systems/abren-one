import uuid

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.modules.finance.application.commands.create_account import (
    CreateAccountInput,
)
from abren_one.modules.finance.application.commands.create_account import (
    execute as create_account,
)
from abren_one.modules.finance.application.commands.create_journal_entry import (
    CreateJournalEntryInput,
    JournalLineInput,
)
from abren_one.modules.finance.application.commands.create_journal_entry import (
    execute as create_journal_entry,
)
from abren_one.modules.finance.application.commands.post_journal_entry import (
    PostJournalEntryInput,
)
from abren_one.modules.finance.application.commands.post_journal_entry import (
    execute as post_journal_entry,
)
from abren_one.modules.finance.application.commands.reverse_journal_entry import (
    ReverseJournalEntryInput,
)
from abren_one.modules.finance.application.commands.reverse_journal_entry import (
    execute as reverse_journal_entry,
)
from abren_one.modules.finance.application.exceptions import (
    AccountNotFoundError,
    FinanceDomainError,
    JournalEntryNotFoundError,
)
from abren_one.modules.finance.application.queries.get_account import (
    execute as get_account,
)
from abren_one.modules.finance.application.queries.get_journal_entry import (
    execute as get_journal_entry,
)
from abren_one.modules.finance.application.queries.get_trial_balance import (
    execute as get_trial_balance,
)
from abren_one.modules.finance.application.queries.list_accounts import (
    execute as list_accounts,
)
from abren_one.modules.finance.application.queries.list_journal_entries import (
    execute as list_journal_entries,
)
from abren_one.modules.finance.interfaces.api.v1.serializers import (
    AccountDetailResponseSerializer,
    AccountSummaryResponseSerializer,
    CreateAccountRequestSerializer,
    CreateJournalEntryRequestSerializer,
    JournalEntryDetailResponseSerializer,
    JournalEntrySummaryResponseSerializer,
    ReverseJournalEntryRequestSerializer,
    TrialBalanceResponseSerializer,
)
from abren_one.platform.common.context import build_execution_context
from abren_one.platform.tenancy.permissions import HasOrganizationContext


class AccountListCreateView(APIView):
    """List and create Chart of Accounts (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        account_type = request.query_params.get("account_type")
        is_active_param = request.query_params.get("is_active")
        is_active = None
        if is_active_param is not None:
            is_active = is_active_param.lower() in ("true", "1")

        accounts = list_accounts(
            context=ctx,
            account_type=account_type,
            is_active=is_active,
        )
        serializer = AccountSummaryResponseSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        try:
            result = create_account(
                CreateAccountInput(
                    context=ctx,
                    code=validated["code"],
                    name=validated["name"],
                    account_type=validated.get("account_type", "asset"),
                    currency=validated.get("currency", "USD"),
                    description=validated.get("description", ""),
                    parent_id=validated.get("parent_id"),
                )
            )
            return Response(
                {
                    "account_id": str(result.account_id),
                    "code": result.code,
                    "name": result.name,
                    "account_type": result.account_type,
                    "currency": result.currency,
                },
                status=status.HTTP_201_CREATED,
            )
        except FinanceDomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailView(APIView):
    """Retrieve an account by ID (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request, account_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        try:
            account = get_account(account_id=account_id, context=ctx)
            serializer = AccountDetailResponseSerializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AccountNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)


class JournalEntryListCreateView(APIView):
    """List and create journal entries (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        status_param = request.query_params.get("status")
        entries = list_journal_entries(context=ctx, status=status_param)
        serializer = JournalEntrySummaryResponseSerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = CreateJournalEntryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        ctx = build_execution_context(request)
        line_inputs = [
            JournalLineInput(
                account_id=line["account_id"],
                debit=line["debit"],
                credit=line["credit"],
                memo=line.get("memo", ""),
            )
            for line in validated["lines"]
        ]

        try:
            result = create_journal_entry(
                CreateJournalEntryInput(
                    context=ctx,
                    entry_date=validated["entry_date"],
                    memo=validated["memo"],
                    currency=validated.get("currency", "USD"),
                    lines=line_inputs,
                    entry_number=validated.get("entry_number", ""),
                    source_document=validated.get("source_document", ""),
                    program_id=validated.get("program_id"),
                    grant_id=validated.get("grant_id"),
                    donation_id=validated.get("donation_id"),
                    post_immediately=validated.get("post_immediately", False),
                )
            )
            return Response(
                {
                    "journal_entry_id": str(result.journal_entry_id),
                    "entry_number": result.entry_number,
                    "status": result.status,
                    "total_debits": str(result.total_debits),
                    "total_credits": str(result.total_credits),
                },
                status=status.HTTP_201_CREATED,
            )
        except FinanceDomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class JournalEntryDetailView(APIView):
    """Retrieve full journal entry details with lines (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request, journal_entry_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        try:
            entry = get_journal_entry(journal_entry_id=journal_entry_id, context=ctx)
            serializer = JournalEntryDetailResponseSerializer(entry)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JournalEntryNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)


class JournalEntryPostView(APIView):
    """Post a draft journal entry to the ledger (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def post(self, request: Request, journal_entry_id: uuid.UUID) -> Response:
        ctx = build_execution_context(request)
        try:
            result = post_journal_entry(
                PostJournalEntryInput(
                    context=ctx,
                    journal_entry_id=journal_entry_id,
                )
            )
            return Response(
                {
                    "journal_entry_id": str(result.journal_entry_id),
                    "entry_number": result.entry_number,
                    "status": result.status,
                    "posted_at": result.posted_at,
                },
                status=status.HTTP_200_OK,
            )
        except JournalEntryNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except FinanceDomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class JournalEntryReverseView(APIView):
    """Reverse a posted journal entry with offsetting lines (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def post(self, request: Request, journal_entry_id: uuid.UUID) -> Response:
        serializer = ReverseJournalEntryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data["reason"]

        ctx = build_execution_context(request)
        try:
            result = reverse_journal_entry(
                ReverseJournalEntryInput(
                    context=ctx,
                    journal_entry_id=journal_entry_id,
                    reason=reason,
                )
            )
            return Response(
                {
                    "original_entry_id": str(result.original_entry_id),
                    "original_entry_number": result.original_entry_number,
                    "reversal_entry_id": str(result.reversal_entry_id),
                    "reversal_entry_number": result.reversal_entry_number,
                    "reversed_at": result.reversed_at,
                },
                status=status.HTTP_200_OK,
            )
        except JournalEntryNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except FinanceDomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class TrialBalanceView(APIView):
    """Retrieve the Trial Balance for the active organization (§7.2)."""

    permission_classes = [IsAuthenticated, HasOrganizationContext]

    def get(self, request: Request) -> Response:
        ctx = build_execution_context(request)
        currency = request.query_params.get("currency", "USD")
        tb = get_trial_balance(context=ctx, currency=currency)
        serializer = TrialBalanceResponseSerializer(tb)
        return Response(serializer.data, status=status.HTTP_200_OK)
