from django.contrib import admin

from abren_one.modules.programs.models import Activity, Program, Project


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "start_date", "end_date", "created_at")
    list_filter = ("status", "organization")
    search_fields = ("name", "organization__name")
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "program", "status", "budget_currency", "created_at")
    list_filter = ("status", "program__organization")
    search_fields = ("name", "program__name")
    ordering = ("name",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "due_date", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "project__name")
    ordering = ("-created_at",)
