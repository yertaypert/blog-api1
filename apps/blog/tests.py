from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Comment, Post


TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'blog-tests',
    }
}


@override_settings(CACHES=TEST_CACHES)
class BlogViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user('author@example.com')
        self.other_user = self.create_user('other@example.com')
        self.published_post = Post.objects.create(
            author=self.user,
            title='Published Post',
            slug='published-post',
            body='Visible body',
            status=Post.Status.PUBLISHED,
        )
        self.draft_post = Post.objects.create(
            author=self.user,
            title='Draft Post',
            slug='draft-post',
            body='Hidden body',
            status=Post.Status.DRAFT,
        )
        self.comment = Comment.objects.create(
            post=self.published_post,
            author=self.user,
            body='Original comment',
        )

    def create_user(self, email):
        return get_user_model().objects.create_user(
            email=email,
            first_name='Test',
            last_name='User',
            password='strong-pass-123',
        )

    def test_posts_list_only_returns_published_posts(self):
        response = self.client.get(reverse('post-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['slug'], self.published_post.slug)

    def test_posts_comments_route_is_nested_under_slug(self):
        response = self.client.get(reverse('post-comments', kwargs={'slug': self.published_post.slug}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['body'], self.comment.body)

    def test_draft_post_is_not_available_through_public_routes(self):
        post_response = self.client.get(reverse('post-detail', kwargs={'slug': self.draft_post.slug}))
        comments_response = self.client.get(reverse('post-comments', kwargs={'slug': self.draft_post.slug}))

        self.assertEqual(post_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(comments_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_create_comment_for_published_post(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.post(
            reverse('post-comments', kwargs={'slug': self.published_post.slug}),
            {'body': 'New nested comment'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author_email'], self.other_user.email)
        self.assertTrue(
            Comment.objects.filter(post=self.published_post, author=self.other_user, body='New nested comment').exists()
        )

    def test_post_owner_can_patch_post_but_other_user_cannot(self):
        own_client = APIClient()
        own_client.force_authenticate(self.user)
        own_response = own_client.patch(
            reverse('post-detail', kwargs={'slug': self.published_post.slug}),
            {'title': 'Updated title'},
            format='json',
        )

        other_client = APIClient()
        other_client.force_authenticate(self.other_user)
        other_response = other_client.patch(
            reverse('post-detail', kwargs={'slug': self.published_post.slug}),
            {'title': 'Forbidden title'},
            format='json',
        )

        self.assertEqual(own_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_response.status_code, status.HTTP_403_FORBIDDEN)
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.title, 'Updated title')

    def test_only_comment_owner_can_update_comment(self):
        owner_client = APIClient()
        owner_client.force_authenticate(self.user)
        owner_response = owner_client.patch(
            reverse('comment-detail', kwargs={'pk': self.comment.pk}),
            {'body': 'Edited by owner'},
            format='json',
        )

        other_client = APIClient()
        other_client.force_authenticate(self.other_user)
        other_response = other_client.patch(
            reverse('comment-detail', kwargs={'pk': self.comment.pk}),
            {'body': 'Edited by stranger'},
            format='json',
        )

        self.assertEqual(owner_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, 'Edited by owner')
