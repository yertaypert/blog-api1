from unittest.mock import patch

# Django modules
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

# Django Rest Framework modules
from rest_framework import status
from rest_framework.test import APIClient


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class UserLoggingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            first_name='Test',
            last_name='User',
            password='strong-pass-123',
        )

    def test_login_success_is_logged(self):
        with self.assertLogs('users', level='INFO') as logs:
            response = self.client.post(
                '/api/auth/token/',
                {'email': 'user@example.com', 'password': 'strong-pass-123'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any('Login attempt for email: user@example.com' in message for message in logs.output))
        self.assertTrue(any('Login succeeded for email: user@example.com' in message for message in logs.output))

    def test_login_failure_is_logged(self):
        with self.assertLogs('users', level='WARNING') as logs:
            response = self.client.post(
                '/api/auth/token/',
                {'email': 'user@example.com', 'password': 'wrong-pass'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(any('Login failed for email: user@example.com' in message for message in logs.output))

    def test_registration_validation_failure_is_logged(self):
        with self.assertLogs('users', level='WARNING') as logs:
            response = self.client.post(
                '/api/auth/register/',
                {
                    'email': 'new@example.com',
                    'first_name': 'New',
                    'last_name': 'User',
                    'password': 'strong-pass-123',
                    'password2': 'different-pass-123',
                },
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(any('Registration failed for email: new@example.com' in message for message in logs.output))

    def test_registration_unexpected_error_uses_exception_logging(self):
        payload = {
            'email': 'boom@example.com',
            'first_name': 'Boom',
            'last_name': 'User',
            'password': 'strong-pass-123',
            'password2': 'strong-pass-123',
        }

        with patch('apps.users.views.RegisterSerializer.save', side_effect=RuntimeError('boom')):
            with self.assertLogs('users', level='ERROR') as logs:
                with self.assertRaises(RuntimeError):
                    self.client.post('/api/auth/register/', payload, format='json')

        self.assertTrue(any('Unexpected registration error for email: boom@example.com' in message for message in logs.output))

    def test_debug_request_logger_receives_incoming_requests(self):
        with self.assertLogs('debug_requests', level='DEBUG') as logs:
            self.client.get('/api/posts/')

        self.assertTrue(any('Incoming request: GET /api/posts/' in message for message in logs.output))
