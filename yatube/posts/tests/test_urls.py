from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='Auth')
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тест названия группы',
            slug='unique_slug',
            description='Тест описания группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст поста'
        )
        cls.post_of_another_author = Post.objects.create(
            author=User.objects.create_user(username='author'),
            group=cls.group,
            text='Тестовый текст поста'
        )
        cls.url_key_access_right_dict = {
            '/': 'all',
            f'/group/{cls.group.slug}/': 'all',
            f'/profile/{cls.post.author.username}/': 'all',
            f'/posts/{cls.post.id}/': 'all',
            '/create/': 'authorized_only',
            f'/posts/{cls.post.id}/edit/': 'authorized_author_only',
            '/follow/': 'authorized_only',
        }
        cls.url_to_template_dict = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.post.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/':
            'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

    def test_posts_urls_exist_and_use_correct_templates(self):
        """Проверка доступности адресов и шаблонов для /posts/<urls>/"""
        for address, access in self.url_key_access_right_dict.items():
            with self.subTest(address=address):
                if access == 'authorized_only':
                    response = self.authorized_client.get(address)
                elif access == 'all':
                    response = self.guest_client.get(address)
                elif access == 'authorized_author_only':
                    response = self.authorized_client.get(address)
                else:
                    raise KeyError(
                        f'Для {address} '
                        'права доступа отсутствуют в словаре'
                        ' cls.url_key_access_right_dict'
                    )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка при запросе к {address}'
                )
                self.assertTemplateUsed(
                    response,
                    self.url_to_template_dict[address],
                    f'Не верный шаблон при вызове {address}'
                )

    def test_posts_urls_redirects_user_with_no_access_rights(self):
        '''Проверка переадресации пользователей
        со страниц, требующих прав доступа.'''
        another_author_post = self.post_of_another_author
        url_redirect_dict = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            f'/posts/{another_author_post.id}/edit/':
            f'/posts/{another_author_post.id}/',
            f'/posts/{self.post.id}/comment/':
            f'/auth/login/?next=/posts/{self.post.id}/comment/',
            '/follow/': '/auth/login/?next=/follow/',
            f'/profile/{self.post.author.username}/follow/': (
                '/auth/login/?next=/profile/'
                f'{self.post.author.username}/follow/'
            ),
            f'/profile/{self.post.author.username}/unfollow/': (
                '/auth/login/?next=/profile/'
                f'{self.post.author.username}/unfollow/'
            )
        }
        for url, redirect_url in url_redirect_dict.items():
            if redirect_url == f'/posts/{another_author_post.id}/':
                response = self.authorized_client.get(url, follow=True)
            else:
                response = self.guest_client.get(url, follow=True)
            self.assertRedirects(
                response,
                redirect_url,
                msg_prefix=f'Ошибка при переадресации от {url}'
            )

    def test_posts_urls_response_404_at_not_exist_page(self):
        '''Проверка ошибки 404 при переходе по не существующему адресу.'''
        response = self.guest_client.get('/not_existing_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Ошибка при переходе по не существующему адресу вместо 404'
        )
