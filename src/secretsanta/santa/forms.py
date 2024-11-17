from django import forms
from django.utils.translation import gettext_lazy

from . import models


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ["name", "description", "event_date", "budget_limit"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class WishListForm(forms.ModelForm):
    class Meta:
        model = models.GroupMember
        fields = ["wishlist"]
        widgets = {
            "wishlist": forms.Textarea(
                attrs={"rows": 5, "placeholder": gettext_lazy("My wishlist:")}
            )
        }


class MatchingForm(forms.ModelForm):
    confirm = forms.BooleanField(
        required=True,
        label=gettext_lazy("Confirm Match"),
        help_text=gettext_lazy("This action cannot be undone."),
    )
