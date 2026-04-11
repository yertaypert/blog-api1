# Python modules
from unittest.mock import patch

# Django modules
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

# Django Rest Framework modules
from rest_framework import status
from rest_framework.test import APIClient


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class UserLoggingTests(TestCase):
    def setUp(self):
        cache.clear()
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

    def test_registration_uses_default_preference_values(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'email': 'defaults@example.com',
                'first_name': 'Default',
                'last_name': 'Prefs',
                'password': 'strong-pass-123',
                'password2': 'strong-pass-123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email='defaults@example.com')
        self.assertEqual(user.preferred_language, 'en')
        self.assertEqual(user.preferred_timezone, 'UTC')

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

    def test_register_is_rate_limited_per_ip(self):
        for index in range(5):
            response = self.client.post(
                '/api/auth/register/',
                {
                    'email': f'user{index}@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'strong-pass-123',
                    'password2': 'strong-pass-123',
                },
                format='json',
                REMOTE_ADDR='203.0.113.10',
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            '/api/auth/register/',
            {
                'email': 'user6@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'strong-pass-123',
                'password2': 'strong-pass-123',
            },
            format='json',
            REMOTE_ADDR='203.0.113.10',
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.json(), {'detail': 'Too many requests. Try again later.'})

    def test_login_is_rate_limited_per_ip(self):
        for _ in range(10):
            response = self.client.post(
                '/api/auth/token/',
                {'email': 'user@example.com', 'password': 'strong-pass-123'},
                format='json',
                REMOTE_ADDR='203.0.113.20',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            '/api/auth/token/',
            {'email': 'user@example.com', 'password': 'strong-pass-123'},
            format='json',
            REMOTE_ADDR='203.0.113.20',
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.json(), {'detail': 'Too many requests. Try again later.'})

    def test_register_rate_limit_does_not_clear_unrelated_cache_entries(self):
        cache.set('sentinel', 'value', timeout=60)

        for index in range(5):
            self.client.post(
                '/api/auth/register/',
                {
                    'email': f'cache-user{index}@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'password': 'strong-pass-123',
                    'password2': 'strong-pass-123',
                },
                format='json',
                REMOTE_ADDR='203.0.113.30',
            )

        self.assertEqual(cache.get('sentinel'), 'value')
