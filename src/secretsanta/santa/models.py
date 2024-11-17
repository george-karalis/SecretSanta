from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy


class Group(models.Model):
    class Meta:
        db_table = "group"
        ordering = ("event_date", "name")
        verbose_name = gettext_lazy("Group")
        verbose_name_plural = gettext_lazy("Groups")

    name = models.CharField(max_length=100, verbose_name=gettext_lazy("Group Name"))
    description = models.TextField(
        blank=True, null=True, verbose_name=gettext_lazy("Group's Description")
    )
    created_by = models.ForeignKey(
        User, verbose_name=gettext_lazy("Group's Creator"), on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=gettext_lazy("Created at")
    )
    members = models.ManyToManyField(
        User,
        through="GroupMember",
        through_fields=("group", "user"),
        related_name="created_groups",
        verbose_name=gettext_lazy("Group's Members"),
    )
    event_date = models.DateField(verbose_name=gettext_lazy("Event's Date"))
    budget_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=gettext_lazy("Budget Limit"),
    )
    is_matched = models.BooleanField(
        default=False, verbose_name=gettext_lazy("Have the matches been completed?")
    )

    def __str__(self):
        return f"Group: {self.name}"

    @property
    def completed(self):
        """
        Determines if the event has been completed based on the `Group`'s `event_date`

        Returns
        -------
            `True` in case the event has been completed.
            `False` if the event hasn't happened yet.
        """
        dt_now = timezone.make_aware(datetime.now())
        if dt_now >= self.event_date:
            return True
        return False


class GroupMember(models.Model):
    class Meta:
        db_table = "group_member"
        ordering = ("joined_at",)
        unique_together = ("user", "group")
        verbose_name = gettext_lazy("Group Member")
        verbose_name_plural = gettext_lazy("Group Members")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=gettext_lazy("User")
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        help_text=gettext_lazy("Group that this Member is part of"),
        related_name="group_members",
        verbose_name=gettext_lazy("Groups"),
    )
    wishlist = models.TextField(
        blank=True, null=True, verbose_name=gettext_lazy("Member's whishlist")
    )
    recipient = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="santa_for",
        verbose_name=gettext_lazy("Gift Recipient"),
    )
    joined_at = models.DateTimeField(
        auto_now_add=True, verbose_name=gettext_lazy("Joined Datetime")
    )

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
