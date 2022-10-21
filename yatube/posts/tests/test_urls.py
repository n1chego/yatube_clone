import shutil

from http import HTTPStatus
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts import consts
from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=consts.TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(
            username=consts.FIRST_USER_USERNAME
        )
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=consts.GROUP_TITLE,
            slug=consts.GROUP_SLUG,
            description=consts.GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=consts.POST_TEXT
        )
        cls.post_of_another_author = Post.objects.create(
            author=User.objects.create_user(username=consts.USER_USERNAME),
            group=cls.group,
            text=consts.POST_TEXT
        )
        cls.page_url_dict = {
            'index': reverse(
                'posts:index'
            ),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.group.slug}'}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{cls.post.author.username}'}
            ),
            'detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'create': reverse(
                'posts:post_create'
            ),
            'edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'comment': reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'follow': reverse(
                'posts:follow_index'
            ),
            'profile_follow': reverse(
                'posts:profile_follow',
                kwargs={'username': f'{cls.post.author.username}'}
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{cls.post.author.username}'}
            ),
            'login_redirect': '/auth/login/?next=',
        }
        cls.url_key_access_right_dict = {
            cls.page_url_dict['index']: 'all',
            cls.page_url_dict['group']: 'all',
            cls.page_url_dict['profile']: 'all',
            cls.page_url_dict['detail']: 'all',
            cls.page_url_dict['create']: 'authorized_only',
            cls.page_url_dict['edit']: 'authorized_author_only',
            cls.page_url_dict['follow']: 'authorized_only',
        }
        cls.url_to_template_dict = {
            cls.page_url_dict['index']: 'posts/index.html',
            cls.page_url_dict['group']: 'posts/group_list.html',
            cls.page_url_dict['profile']: 'posts/profile.html',
            cls.page_url_dict['detail']: 'posts/post_detail.html',
            cls.page_url_dict['create']: 'posts/create_post.html',
            cls.page_url_dict['edit']: 'posts/create_post.html',
            cls.page_url_dict['follow']: 'posts/follow.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(consts.TEMP_MEDIA_ROOT, ignore_errors=True)

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
        test_dict = self.page_url_dict
        url_redirect_dict = {
            test_dict['create']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["create"]}'
            ),
            test_dict['edit']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["edit"]}'
            ),
            f'/posts/{another_author_post.id}/edit/':
            f'/posts/{another_author_post.id}/',
            test_dict['comment']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["comment"]}'
            ),
            test_dict['follow']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["follow"]}'
            ),
            test_dict['profile_follow']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["profile_follow"]}'
            ),
            test_dict['profile_unfollow']: (
                f'{test_dict["login_redirect"]}'
                f'{test_dict["profile_unfollow"]}'
            ),
        }
        for url, redirect_url in url_redirect_dict.items():
            with self.subTest(url=url):
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
