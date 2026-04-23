from django.urls import path
from .views import (
    WorkspaceListCreateView,
    WorkspaceDetailView,
    InviteMemberView,
    WorkspaceMemberListView
)

urlpatterns = [
    path('', WorkspaceListCreateView.as_view(), name='workspace-list-create'),
    path('<int:pk>/', WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('<int:pk>/invite/', InviteMemberView.as_view(), name='workspace-invite'),
    path('<int:pk>/members/', WorkspaceMemberListView.as_view(), name='workspace-members'),
]