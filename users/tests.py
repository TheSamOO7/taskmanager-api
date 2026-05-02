import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.factories import UserFactory


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
class TestRegister:
    def test_register_success(self, api_client):
        response = api_client.post(reverse('register'), {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'pass1234'
        })
        assert response.status_code == 201
        assert response.data['email'] == 'newuser@example.com'

    def test_register_duplicate_email(self, api_client):
        UserFactory(email='existing@example.com')
        response = api_client.post(reverse('register'), {
            'email': 'existing@example.com',
            'full_name': 'Test',
            'password': 'pass1234'
        })
        assert response.status_code == 400

    def test_register_missing_password(self, api_client):
        response = api_client.post(reverse('register'), {
            'email': 'test@example.com',
            'full_name': 'Test'
        })
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client):
        user = UserFactory(email='login@example.com')
        response = api_client.post(reverse('login'), {
            'email': 'login@example.com',
            'password': 'testpass123'
        })
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, api_client):
        UserFactory(email='login2@example.com')
        response = api_client.post(reverse('login'), {
            'email': 'login2@example.com',
            'password': 'wrongpass'
        })
        assert response.status_code == 401

    def test_me_endpoint_authenticated(self, auth_client):
        response = auth_client.get(reverse('me'))
        assert response.status_code == 200
        assert response.data['email'] == auth_client.user.email

    def test_me_endpoint_unauthenticated(self, api_client):
        response = api_client.get(reverse('me'))
        assert response.status_code == 401