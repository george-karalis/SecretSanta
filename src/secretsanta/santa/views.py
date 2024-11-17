from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
)

from . import forms, models


class GroupListView(LoginRequiredMixin, ListView):
    model = models.Group
    template_name = "santa/group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        return models.Group.objects.filter(members=self.request.user)


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = models.Group
    template_name = "santa/group_from.html"
    form_class = forms.GroupForm
    success_url = reverse_lazy("santa:group_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        models.GroupMember.objects.create(user=self.request.user, group=self.object)
        messages.success(
            self.request,
            gettext_lazy(f"Group {self.object.name} Created successfully!"),
        )
        return response


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = models.Group
    template_name = "santa/group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_member"] = self.object.members.filter(
            id=self.request.user.id
        ).exists()
        context["is_creator"] = self.object.created_by == self.request.user
        if context["is_member"]:
            context["membership"] = models.GroupMember.objects.get(
                user=self.request.user, group=self.object
            )
        return context


@login_required
def join_group(request, group_id):
    group = get_object_or_404(models.Group, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        models.GroupMember.objects.create(user=request.user, group=group)
        messages.success(
            request,
            gettext_lazy(
                f"{request.user.username} had successfully joined {group.name}."
            ),
        )
    return redirect("santa:group_detail", pk=group_id)


@login_required
def update_wishlist(request, group_id):
    membership = get_object_or_404(
        models.GroupMember,
        user=request.user,
        group_id=group_id,
    )
    if request.method == "POST":
        form = forms.WishListForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, gettext_lazy("Wishlist updated successfully!"))
            return redirect("santa:group_detail", pk=group_id)
    else:
        form = forms.WishListForm(instance=membership)

    return render(request, "santa/wishlist_form.html", {"form": form})
