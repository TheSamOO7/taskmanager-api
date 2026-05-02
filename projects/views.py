from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from workspaces.models import Workspace, WorkspaceMember
from .models import Project, Task, Comment, ActivityLog
from .serializers import (
    ProjectSerializer, TaskSerializer,
    CommentSerializer, ActivityLogSerializer
)


def is_workspace_member(user, workspace):
    return WorkspaceMember.objects.filter(
        user=user, workspace=workspace
    ).exists()


# ── Projects ──────────────────────────────────────────────

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_workspace(self):
        return get_object_or_404(Workspace, pk=self.kwargs['workspace_pk'])

    def get_queryset(self):
        workspace = self.get_workspace()
        if not is_workspace_member(self.request.user, workspace):
            return Project.objects.none()
        return Project.objects.filter(workspace=workspace)

    def perform_create(self, serializer):
        workspace = self.get_workspace()
        if not is_workspace_member(self.request.user, workspace):
            raise PermissionError("You are not a member of this workspace.")
        serializer.save(workspace=workspace, created_by=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workspace = get_object_or_404(Workspace, pk=self.kwargs['workspace_pk'])
        return Project.objects.filter(workspace=workspace)


# ── Tasks ─────────────────────────────────────────────────

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

    def get_queryset(self):
        project = self.get_project()
        queryset = Task.objects.filter(project=project)

        # filtering
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        assignee_id = self.request.query_params.get('assignee_id')
        due_date = self.request.query_params.get('due_date')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        if due_date:
            queryset = queryset.filter(due_date=due_date)

        return queryset

    def perform_create(self, serializer):
        project = self.get_project()
        task = serializer.save(
            project=project,
            created_by=self.request.user
        )
        # log activity
        ActivityLog.objects.create(
            task=task,
            actor=self.request.user,
            action='Task created',
            new_value=task.title
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project_id=self.kwargs['project_pk'])

    def perform_update(self, serializer):
        task = self.get_object()
        old_status = task.status
        old_assignee = str(task.assignee) if task.assignee else 'None'

        updated_task = serializer.save()

        # log status change
        if old_status != updated_task.status:
            ActivityLog.objects.create(
                task=updated_task,
                actor=self.request.user,
                action='Status changed',
                old_value=old_status,
                new_value=updated_task.status
            )

        # log assignee change
        new_assignee = str(updated_task.assignee) if updated_task.assignee else 'None'
        if old_assignee != new_assignee:
            ActivityLog.objects.create(
                task=updated_task,
                actor=self.request.user,
                action='Assignee changed',
                old_value=old_assignee,
                new_value=new_assignee
            )


# ── Comments ──────────────────────────────────────────────

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        serializer.save(task=task, author=self.request.user)


# ── Activity Log ──────────────────────────────────────────

class ActivityLogListView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(
            task_id=self.kwargs['task_pk']
        ).order_by('-timestamp')