import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.factories import UserFactory
from workspaces.factories import WorkspaceFactory, WorkspaceMemberFactory
from projects.factories import ProjectFactory, TaskFactory
from projects.models import ActivityLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = UserFactory()
    response = api_client.post(reverse('login'), {
        'email': user.email,
        'password': 'testpass123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    api_client.user = user
    return api_client


@pytest.fixture
def workspace_with_member(auth_client):
    workspace = WorkspaceFactory()
    WorkspaceMemberFactory(workspace=workspace, user=auth_client.user)
    return workspace


@pytest.mark.django_db
class TestProject:
    def test_create_project(self, auth_client, workspace_with_member):
        url = reverse('project-list-create', kwargs={
            'workspace_pk': workspace_with_member.id
        })
        response = auth_client.post(url, {
            'name': 'New Project',
            'description': 'Test description'
        })
        assert response.status_code == 201
        assert response.data['name'] == 'New Project'

    def test_non_member_cannot_create_project(self, auth_client):
        # workspace user does NOT belong to
        workspace = WorkspaceFactory()
        url = reverse('project-list-create', kwargs={
            'workspace_pk': workspace.id
        })
        response = auth_client.post(url, {'name': 'Sneaky Project'})
        assert response.status_code == 403


@pytest.mark.django_db
class TestTask:
    def test_create_task(self, auth_client, workspace_with_member):
        project = ProjectFactory(workspace=workspace_with_member)
        url = reverse('task-list-create', kwargs={
            'workspace_pk': workspace_with_member.id,
            'project_pk': project.id
        })
        response = auth_client.post(url, {
            'title': 'New Task',
            'status': 'todo',
            'priority': 'high'
        })
        assert response.status_code == 201
        assert response.data['title'] == 'New Task'

    def test_activity_log_created_on_task_create(self, auth_client, workspace_with_member):
        project = ProjectFactory(workspace=workspace_with_member)
        url = reverse('task-list-create', kwargs={
            'workspace_pk': workspace_with_member.id,
            'project_pk': project.id
        })
        auth_client.post(url, {
            'title': 'Logged Task',
            'status': 'todo',
            'priority': 'medium'
        })
        assert ActivityLog.objects.filter(action='Task created').exists()

    def test_filter_tasks_by_status(self, auth_client, workspace_with_member):
        project = ProjectFactory(workspace=workspace_with_member)
        TaskFactory(project=project, status='todo')
        TaskFactory(project=project, status='done')

        url = reverse('task-list-create', kwargs={
            'workspace_pk': workspace_with_member.id,
            'project_pk': project.id
        })
        response = auth_client.get(f'{url}?status=todo')
        assert response.status_code == 200
        assert all(t['status'] == 'todo' for t in response.data)