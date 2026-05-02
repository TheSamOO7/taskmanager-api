import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.factories import UserFactory
from workspaces.factories import WorkspaceFactory, WorkspaceMemberFactory
from workspaces.models import WorkspaceMember


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


@pytest.mark.django_db
class TestWorkspace:
    def test_create_workspace(self, auth_client):
        response = auth_client.post(reverse('workspace-list-create'), {
            'name': 'Test Workspace'
        })
        assert response.status_code == 201
        assert response.data['name'] == 'Test Workspace'

    def test_creator_becomes_admin(self, auth_client):
        auth_client.post(reverse('workspace-list-create'), {
            'name': 'Test Workspace'
        })
        membership = WorkspaceMember.objects.get(user=auth_client.user)
        assert membership.role == WorkspaceMember.Role.ADMIN

    def test_list_only_own_workspaces(self, auth_client):
        # workspace the user belongs to
        workspace = WorkspaceFactory()
        WorkspaceMemberFactory(
            workspace=workspace,
            user=auth_client.user
        )
        # workspace the user does NOT belong to
        WorkspaceFactory()

        response = auth_client.get(reverse('workspace-list-create'))
        assert response.status_code == 200
        # user should only see workspaces they belong to
        workspace_ids = [w['id'] for w in response.data]
        assert workspace.id in workspace_ids

    def test_invite_member_as_admin(self, auth_client):
        # create workspace where auth_client.user is admin
        workspace_response = auth_client.post(
            reverse('workspace-list-create'),
            {'name': 'Invite Test'}
        )
        workspace_id = workspace_response.data['id']

        new_user = UserFactory()
        response = auth_client.post(
            reverse('workspace-invite', kwargs={'pk': workspace_id}),
            {'email': new_user.email, 'role': 'member'}
        )
        assert response.status_code == 201

    def test_invite_member_as_non_admin(self, auth_client):
        # workspace where auth_client.user is just a member
        workspace = WorkspaceFactory()
        WorkspaceMemberFactory(
            workspace=workspace,
            user=auth_client.user,
            role=WorkspaceMember.Role.MEMBER
        )
        new_user = UserFactory()
        response = auth_client.post(
            reverse('workspace-invite', kwargs={'pk': workspace.id}),
            {'email': new_user.email, 'role': 'member'}
        )
        assert response.status_code == 403