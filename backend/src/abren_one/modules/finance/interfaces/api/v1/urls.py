from django.urls import path

from abren_one.modules.finance.interfaces.api.v1.views import (
    AccountDetailView,
    AccountListCreateView,
    JournalEntryDetailView,
    JournalEntryListCreateView,
    JournalEntryPostView,
    JournalEntryReverseView,
    TrialBalanceView,
)

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<uuid:account_id>/", AccountDetailView.as_view(), name="account-detail"),
    path("journal-entries/", JournalEntryListCreateView.as_view(), name="journal-entry-list-create"),
    path("journal-entries/<uuid:journal_entry_id>/", JournalEntryDetailView.as_view(), name="journal-entry-detail"),
    path("journal-entries/<uuid:journal_entry_id>/post/", JournalEntryPostView.as_view(), name="journal-entry-post"),
    path(
        "journal-entries/<uuid:journal_entry_id>/reverse/",
        JournalEntryReverseView.as_view(),
        name="journal-entry-reverse",
    ),
    path("trial-balance/", TrialBalanceView.as_view(), name="trial-balance"),
]
