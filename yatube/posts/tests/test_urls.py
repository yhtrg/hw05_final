from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="tester")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )
        cls.templates = [
            reverse('posts:posts_index'),
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.id}/",
        ]
        cls.urls = {
            'group': reverse('posts:group_list',
                             kwargs={'slug': cls.group.slug}),
            'index': reverse('posts:posts_index'),
            'profile': reverse('posts:profile',
                               kwargs={'username': 'tester'}),
            'create': reverse('posts:post_create'),
            'edit': reverse('posts:post_edit',
                            kwargs={'post_id': cls.post.id}),
            'detail': reverse('posts:post_detail',
                              kwargs={'post_id': cls.post.id}),
            'notfound': '/unexisting_page/',
            'login': reverse('users:login'),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_http_status(self):
        """Ответы от сервера правильные"""
        test_data = [
            (self.urls.get('group'),
             HTTPStatus.OK, self.client),
            (self.urls.get('index'),
             HTTPStatus.OK, self.client),
            (self.urls.get('profile'),
             HTTPStatus.OK, self.client),
            (self.urls.get('detail'),
             HTTPStatus.OK, self.client),
            (self.urls.get('notfound'),
             HTTPStatus.NOT_FOUND, self.client)
        ]
        for url, expected_status, client in test_data:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_posts_post_id_edit_url_exists_at_author(self):
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects(self):
        """Редиректы работают правильно"""
        redirects = (
            (
                self.urls.get('create'),
                self.urls.get('login') + '?next=' + self.urls.get('create'),
                self.client,
            ),
        )
        for url, redirect_url, client in redirects:
            with self.subTest():
                response = client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        cache.clear()
        template = (
            (self.urls.get('group'),
             'posts/group_list.html', self.client),
            (self.urls.get('index'),
             'posts/index.html', self.client),
            (self.urls.get('profile'),
             'posts/profile.html', self.client),
            (self.urls.get('create'), 'posts/post_create.html',
             self.authorized_client),
            (self.urls.get('edit'), 'posts/post_create.html',
             self.authorized_client),
            (self.urls.get('detail'),
             'posts/post_detail.html', self.client),
        )
        for url_name, template_name, client in template:
            with self.subTest(url_name=url_name, template_name=template_name):
                response = client.get(url_name)
                self.assertTemplateUsed(response, template_name)
