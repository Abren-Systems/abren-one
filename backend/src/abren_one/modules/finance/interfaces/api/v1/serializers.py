from decimal import Decimal

from rest_framework import serializers


class CreateAccountRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    account_type = serializers.ChoiceField(
        choices=["asset", "liability", "equity", "revenue", "expense"],
        default="asset",
    )
    currency = serializers.CharField(max_length=3, default="USD")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    parent_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class AccountSummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    currency = serializers.CharField()
    is_active = serializers.BooleanField()


class AccountDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    currency = serializers.CharField()
    is_active = serializers.BooleanField()
    description = serializers.CharField()
    parent_id = serializers.UUIDField(allow_null=True)


class JournalLineInputSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    debit = serializers.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    credit = serializers.DecimalField(max_digits=16, decimal_places=2, default=Decimal("0.00"))
    memo = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")


class CreateJournalEntryRequestSerializer(serializers.Serializer):
    entry_date = serializers.DateField()
    memo = serializers.CharField()
    currency = serializers.CharField(max_length=3, default="USD")
    lines = JournalLineInputSerializer(many=True)
    entry_number = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    source_document = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    program_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    grant_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    donation_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    post_immediately = serializers.BooleanField(default=False)


class JournalLineDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    account_id = serializers.UUIDField()
    account_code = serializers.CharField()
    account_name = serializers.CharField()
    debit = serializers.DecimalField(max_digits=16, decimal_places=2)
    credit = serializers.DecimalField(max_digits=16, decimal_places=2)
    memo = serializers.CharField()


class JournalEntrySummaryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    entry_number = serializers.CharField()
    entry_date = serializers.DateField()
    memo = serializers.CharField()
    currency = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    reversal_of_id = serializers.UUIDField(allow_null=True)


class JournalEntryDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    entry_number = serializers.CharField()
    entry_date = serializers.DateField()
    memo = serializers.CharField()
    currency = serializers.CharField()
    status = serializers.CharField()
    posted_at = serializers.DateTimeField(allow_null=True)
    posted_by = serializers.UUIDField(allow_null=True)
    source_document = serializers.CharField()
    reversal_of_id = serializers.UUIDField(allow_null=True)
    program_id = serializers.UUIDField(allow_null=True)
    grant_id = serializers.UUIDField(allow_null=True)
    donation_id = serializers.UUIDField(allow_null=True)
    lines = JournalLineDetailSerializer(many=True)
    total_debits = serializers.DecimalField(max_digits=16, decimal_places=2)
    total_credits = serializers.DecimalField(max_digits=16, decimal_places=2)


class ReverseJournalEntryRequestSerializer(serializers.Serializer):
    reason = serializers.CharField()


class TrialBalanceItemSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    normal_balance = serializers.CharField()
    total_debit = serializers.DecimalField(max_digits=16, decimal_places=2)
    total_credit = serializers.DecimalField(max_digits=16, decimal_places=2)
    balance_debit = serializers.DecimalField(max_digits=16, decimal_places=2)
    balance_credit = serializers.DecimalField(max_digits=16, decimal_places=2)


class TrialBalanceResponseSerializer(serializers.Serializer):
    items = TrialBalanceItemSerializer(many=True)
    total_debits = serializers.DecimalField(max_digits=16, decimal_places=2)
    total_credits = serializers.DecimalField(max_digits=16, decimal_places=2)
    is_balanced = serializers.BooleanField()
    currency = serializers.CharField()
