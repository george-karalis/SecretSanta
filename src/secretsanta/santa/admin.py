from django.conf import settings
from django.contrib import admin
from django.utils import formats
from django.utils.html import format_html

from . import models


def _format_datetime(template, function, description):
    def output(self, obj):
        value = function(obj)
        if value is None:
            return ""
        value = formats.date_format(value, template)
        return format_html('<span style="white-space: nowrap;">{0}</span>', value)

    output.short_description = description
    return output


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Details",
            {
                "classes": ("wide"),
                "fields": ("name", "description", "_event_date", "budget_limit"),
            },
        ),
        (
            "Members",
            {
                "classes": ("wide"),
                "fields": ("members__username",),
            },
        ),
        (
            "Creation Data",
            {
                "classes": ("wide"),
                "fields": ("created_by__username", "created_at"),
            },
        ),
        (
            "Mode",
            {
                "classes": ("wide"),
                "fields": ("is_matched", "completed"),
            },
        ),
    ]
    list_display = ("name", "created_by", "_event_date", "is_matched", "completed")
    date_hierarchy = "event_date"
    list_filter = ("is_matched",)
    readonly_fields = ("created_by", "created_at")
    ordering = ("name", "event_date", "created_at")
    search_fields = ("name", "created_by__username")

    @admin.display(description="Match Completed?", boolean=True, ordering="is_matched")
    def _is_matched(self, obj):
        return obj.is_matched

    @admin.display(description="Is Completed?", boolean=True, ordering="completed")
    def _completed(self, obj):
        return obj.completed

    _event_date = _format_datetime(
        settings.DATETIME_FORMAT,
        lambda obj: obj.event_date,
        description="Event Date & Time",
    )


@admin.register(models.GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Members's Details",
            {
                "classes": ("wide"),
                "fields": ("user__username", "wishlist", "joined_at"),
            },
        ),
        (
            "Groups",
            {
                "classes": ("wide"),
                "fields": ("group",),
            },
        ),
    ]

    list_display = ("user", "group", "_joined_at")
    list_filter = ("group",)
    search_fields = ("user__username", "group__name")
    readonly_fields = ("joined_at",)

    _joined_at = _format_datetime(
        settings.DATETIME_FORMAT,
        lambda obj: obj.joined_at,
        description="Joined at Date & Time",
    )
