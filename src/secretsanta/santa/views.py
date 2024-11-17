from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from . import forms, models
from .utils import giver_receiver_matching


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


class GroupUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = models.Group
    template_name = "santa/group_from.html"
    form_class = forms.GroupForm

    # 1 TODO: Create group admin permission. Enable GroupMember's to be admins
    # and allow group admins to update the group.
    def test_func(self):
        """
        Allows only the group's creator from editing the group.

        Returns
        -------
            True if the GroupMember is the creator.
        """
        group = self.get_object()
        is_creator = self.request.user == group.created_by
        return is_creator

    def get_success_url(self):
        return reverse_lazy("santa:group_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Prevents updating the Group after the matching is done.
        """
        if self.object.is_matched:
            messages.error(
                self.request,
                gettext_lazy(
                    f"Cannot edit {self.object.name} after the matching is completed"
                ),
            )
            return redirect("santa:group_detail", pk=self.object.pk)
        messages.success(
            self.request,
            gettext_lazy(f"Group {self.object.name} updated successfully."),
        )
        return super().form_valid(form)


class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = models.Group
    template_name = "santa/group_confirm_delete.html"
    success_url = reverse_lazy("santa:group_list")

    # 1 TODO: Create group admin permission. Enable GroupMember's to be admins
    # and allow group admins to delete the group.
    def test_func(self):
        """
        Allows only the group's creator from deleting the group.

        Returns
        -------
            True if the GroupMember is the creator.
        """
        group = self.get_object()
        is_creator = self.request.user == group.created_by
        return is_creator

    def delete(self, request, *args, **kwargs):
        messages.success(
            request, gettext_lazy(f"Group {self.object.name} deleted successfully.")
        )
        return super().delete(request, *args, **kwargs)


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


@login_required
def leave_group(request, group_id):
    if request.method != "POST":
        return redirect("santa:group_detail", pk=group_id)

    group = get_object_or_404(models.Group, id=group_id)

    # 1 TODO: Create group admin permission. Enable GroupMember's to be admins
    # and update this view to not allow the last admin to leave the group.
    if group.created_by == request.user:
        messages.error(request, gettext_lazy("Group's creator cannot leave the group."))
        return redirect("santa:group_detail", pk=group_id)

    # 2 TODO: Allow GroupMembers to leave the group even after matching is done.
    # Sent a notification to the GroupMember that had the removed member as recipient to redraw.
    if group.is_matched:
        messages.error(
            request,
            gettext_lazy("Cannot leave the group after the matching is completed."),
        )
        return redirect("santa:group_detail", pk=group_id)

    member = get_object_or_404(models.GroupMember, user=request.user, group=group)
    member_name = member.user.username
    member.delete()

    messages.success(
        request,
        gettext_lazy(f"{member_name} was successfully removed from {group.name}"),
    )
    return redirect("santa:group_list")


@login_required
def perform_matching(request, group_id):
    group = get_object_or_404(models.Group, id=group_id)

    if group.is_matched:
        member = models.GroupMember.filter(group=group, user=request.user)
        message = (
            f"Matching has already performed for {group.name}. "
            f"Your match is: {member.recipient.username}"
        )
        messages.error(request, gettext_lazy(message))
        return redirect("santa:group_detail", pk=group_id)

    # 1 TODO: Create group admin permission. Enable GroupMember's to be admins
    # and be able to perform matching.
    if group.created_by != request.user:
        messages.error(
            request, gettext_lazy("Only the group creator can perform matching.")
        )
        return redirect("santa:group_detail", pk=group_id)

    if request.method == "POST":
        form = forms.MatchingForm(request.POST)
        if form.is_valid():
            members = list(group.members.all())

            if len(members) < 2:
                message.error(
                    request,
                    gettext_lazy("At least 2 members are required for matching."),
                )
                return redirect("santa:group_detail", pk=group_id)

            try:
                giver_receiver_matching(members=members)

                messages.success(request, gettext_lazy("Matching is complete."))

            except Exception:
                messages.error(
                    request,
                    gettext_lazy(
                        "An error occurred during matching. Please try again."
                    ),
                )
                return redirect("santa:group_detail", pk=group_id)

            return redirect("santa:group_detail", pk=group_id)
    else:
        form = forms.MatchingForm()

    return render(
        request,
        "santa/matching_form.html",
        {"form": form, "group": group},
    )
