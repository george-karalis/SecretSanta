from django.urls import path

from . import views

app_name = "santa"

urlpatterns = [
    # Group views
    path("", views.GroupListView.as_view(), name="group_list"),
    path("group/create/", views.GroupCreateView.as_view(), name="group_create"),
    path("group/<int:pk>/", views.GroupDetailView.as_view(), name="group_detail"),
    # Member management
    path("group/<int:group_id>/join/", views.join_group, name="join_group"),
    path(
        "group/<int:group_id>/wishlist/", views.update_wishlist, name="update_wishlist"
    ),
    # Matching
]
