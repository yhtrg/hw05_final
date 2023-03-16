from http import HTTPStatus
 
from django.test import TestCase, Client
from django.urls import reverse
 
from ..models import Group, Post, User
 
 
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(slug='test-slug')
        cls.post = Post.objects.create(author=cls.auth, group=cls.group,)
        cls.INDEX = reverse('posts:posts_index')
        cls.GROUP_POSTS = reverse('posts:group_list',
                                  kwargs={'slug': cls.group.slug})
        cls.PROFILE = reverse('posts:profile',
                              kwargs={'username': cls.user.username})
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})
        cls.POST_CREATE = reverse('posts:post_create')
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id})
        cls.POST_COMMENT = reverse('posts:add_comment',
                                   kwargs={'post_id': cls.post.id})
        cls.LOGIN = reverse('users:login')
        cls.FOLLOW_INDEX = reverse('posts:follow_index')
        cls.PROFILE_FOLLOW = reverse('posts:profile_follow',
                                     kwargs={'username': cls.auth})
        cls.PROFILE_UNFOLLOW = reverse('posts:profile_unfollow',
                                       kwargs={'username': cls.auth})
 
    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
 
    def test_redirect_anonymous(self):
        """перенаправление анонимного пользователя на страницу логина."""
        url_names_redirect = [
            (self.POST_CREATE, f'{self.LOGIN}?next={self.POST_CREATE}'),
            (self.POST_EDIT, f'{self.LOGIN}?next={self.POST_EDIT}'),
            (self.POST_COMMENT, f'{self.LOGIN}?next={self.POST_COMMENT}'),
            (self.FOLLOW_INDEX, f'{self.LOGIN}?next={self.FOLLOW_INDEX}'),
            (self.PROFILE_FOLLOW, f'{self.LOGIN}?next={self.PROFILE_FOLLOW}'),
            (self.PROFILE_UNFOLLOW,
             f'{self.LOGIN}?next={self.PROFILE_UNFOLLOW}'),
        ]
        for adress, redirect in url_names_redirect:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)
 
    def test_post_edit_list_url_redirect_authorized_on_profile(self):
        """Страница по адресу /posts/<int:post_id>/edit/ перенаправит
        авторизированного пользователя на страницу пользователя."""
        response = self.authorized_user.get(self.POST_EDIT, follow=True)
        self.assertRedirects(response, self.PROFILE)
 
    def test_namespace_uses_correct_pages(self):
        """Шаблон использует соответствующий namespace:name."""
        templates_pages_names = [
            ('posts/index.html', self.INDEX),
            ('posts/group_list.html', self.GROUP_POSTS),
            ('posts/profile.html', self.PROFILE),
            ('posts/post_detail.html', self.POST_DETAIL),
            ('posts/post_create.html', self.POST_CREATE),
            ('posts/post_create.html', self.POST_EDIT),
            ('core/404.html', '/unexisting_page/'),
            ('posts/follow.html', self.FOLLOW_INDEX),
        ]
        self.authorized_user.force_login(self.auth)
        for template, address in templates_pages_names:
            with self.subTest(template=template):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)
 
    def test_urls_uses_correct_namespace(self):
        """URL-адрес использует соответствующий namespace:name."""
        templates_url_names = [
            (self.INDEX, '/'),
            (self.GROUP_POSTS, f'/group/{self.group.slug}/'),
            (self.PROFILE, f'/profile/{self.user.username}/'),
            (self.POST_DETAIL, f'/posts/{self.post.id}/'),
            (self.POST_CREATE, '/create/'),
            (self.POST_EDIT, f'/posts/{self.post.id}/edit/'),
            (self.POST_COMMENT, f'/posts/{self.post.id}/comment/'),
            (self.FOLLOW_INDEX, '/follow/'),
            (self.PROFILE_FOLLOW, f'/profile/{self.auth.username}/follow/'),
            (self.PROFILE_UNFOLLOW, f'/profile/{self.auth.username}/unfollow/')
        ]
        for address, urls in templates_url_names:
            with self.subTest(address=address):
                self.assertEqual(address, urls, 'not correct')
 
    def test_exists_at_desired_location(self):
        """Проверка доступности адрессов."""
        names = [
            (self.INDEX, HTTPStatus.OK, True),
            (self.GROUP_POSTS, HTTPStatus.OK, True),
            (self.PROFILE, HTTPStatus.OK, True),
            (self.POST_DETAIL, HTTPStatus.OK, True),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND, True),
            (self.POST_CREATE, HTTPStatus.OK, False),
            (self.POST_EDIT, HTTPStatus.FOUND, False),
            (self.POST_COMMENT, HTTPStatus.FOUND, False),
            (self.FOLLOW_INDEX, HTTPStatus.OK, False),
            (self.PROFILE_FOLLOW, HTTPStatus.FOUND, False),
            (self.PROFILE_UNFOLLOW, HTTPStatus.FOUND, False),
        ]
        for address, status, boolean_item in names:
            with self.subTest(address=address):
                if boolean_item:
                    response = self.guest_client.get(address)
                else:
                    response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, status)