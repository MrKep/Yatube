import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
max_posts = 10


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test')
        cls.user_two = User.objects.create_user(username='test_two')
        cls.user_tree = User.objects.create_user(username='test_tree')

        cls.group = Group.objects.create(

            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.group_test = Group.objects.create(

            title='Тестовая группа 2',
            slug='slug2',
            description='Тестовое описание',
        )
        for i in range(1, 15):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
            )
            time.sleep(0.01)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTest.user)

    def test_uses_correct_template(self):
        """Проверяем, что во view используюся правильные html шаблоны """
        template_pages_name = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test'}):
            'posts/profile.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
            'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
            'posts/post_detail.html',
        }
        for reverse_name, template in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_index(self):
        """Проверяем context и паджинатор для index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_test = {
            self.post.author: first_object.author,
            self.post.text: first_object.text,
            self.post.group.slug: first_object.group.slug,
            self.post.image: first_object.image
        }
        for value, expected in context_test.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

        self.assertEqual(len(response.context['page_obj']), max_posts)

    def test_context_group_list(self):
        """Проверяем context и паджинатор для group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'}))
        first_object = response.context['page_obj'][0]
        context_test = {
            self.post.author: first_object.author,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.image: first_object.image
        }
        for value, expected in context_test.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

        self.assertEqual(len(response.context['page_obj']), max_posts)

    def test_context_profile(self):
        """Проверяем context и паджинатор для profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test'}))
        first_object = response.context['page_obj'][0]
        context_test = {
            self.post.author: first_object.author,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.image: first_object.image
        }
        for value, expected in context_test.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

        self.assertEqual(len(response.context['page_obj']), max_posts)

    def test_correct_context_post_detail(self):
        """Проверяем context для post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 14}))
        post = response.context['post']
        context_test = {
            self.post: post.id,
            self.post.image: post.image
        }
        for value, expected in context_test.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_correct_post_create(self):
        """Проверяем context для post_create"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_post_edit(self):
        """Проверяем context для post_edit"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_two_group(self):
        """Проверяем что пост не во второй группе"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug2'}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:profile_follow', kwargs={'username': self.user_two}
            ))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        first_follow = Follow.objects.filter(
            user=self.user, author=self.user_two).count()
        two_follow = Follow.objects.filter(
            user=self.user, author=self.user_tree).count()
        self.assertEqual(first_follow, follow_count + 1)
        self.assertEqual(two_follow, follow_count)
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow', kwargs={'username': self.user_two}
            ))
        first_follow = Follow.objects.filter(
            user=self.user, author=self.user_two).count()
        self.assertEqual(first_follow, follow_count)
