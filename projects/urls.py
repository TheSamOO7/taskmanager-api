from django.urls import path
from .views import (
    ProjectListCreateView, ProjectDetailView,
    TaskListCreateView, TaskDetailView,
    CommentListCreateView, ActivityLogListView
)

urlpatterns = [
    # Projects
    path(
        '',
        ProjectListCreateView.as_view(),
        name='project-list-create'
    ),
    path(
        '<int:project_pk>/',
        ProjectDetailView.as_view(),
        name='project-detail'
    ),

    # Tasks
    path(
        '<int:project_pk>/tasks/',
        TaskListCreateView.as_view(),
        name='task-list-create'
    ),
    path(
        '<int:project_pk>/tasks/<int:pk>/',
        TaskDetailView.as_view(),
        name='task-detail'
    ),

    # Comments
    path(
        '<int:project_pk>/tasks/<int:task_pk>/comments/',
        CommentListCreateView.as_view(),
        name='comment-list-create'
    ),

    # Activity log
    path(
        '<int:project_pk>/tasks/<int:task_pk>/activity/',
        ActivityLogListView.as_view(),
        name='activity-log'
    ),
]