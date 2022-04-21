from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


# Проверка кеша в test_forms функция test_caching или нужно еще?
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_correct_urls(self):
        response_urls = {
            '/': HTTPStatus.OK,
            '/group/slug/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/profile/test/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND

        }

        for address, stat_code in response_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, stat_code)

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_templates(self):
        template_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/test/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }

        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
