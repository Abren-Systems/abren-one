from django.contrib import admin

from abren_one.modules.finance.models.account import Account
from abren_one.modules.finance.models.journal_entry import JournalEntry
from abren_one.modules.finance.models.journal_line import JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 2
    fields = ("account", "debit", "credit", "memo")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "currency", "is_active", "organization")
    list_filter = ("account_type", "is_active", "currency")
    search_fields = ("code", "name")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_number", "entry_date", "status", "currency", "memo", "organization")
    list_filter = ("status", "entry_date", "currency")
    search_fields = ("entry_number", "memo", "source_document")
    inlines = [JournalLineInline]
