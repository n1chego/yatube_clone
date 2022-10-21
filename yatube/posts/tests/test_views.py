import shutil

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts import consts
from posts.models import Follow, Group, Post, User


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=consts.TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()
        # Создаем пользователя
        cls.first_user = User.objects.create_user(
            username=consts.FIRST_USER_USERNAME
        )
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.first_user)
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        cls.uploaded = SimpleUploadedFile(
            name=consts.IMAGE_NAME,
            content=consts.SMALL_GIF,
            content_type='image/gif'
        )
        # Создаем записи в БД.
        cls.first_group = Group.objects.create(
            title=consts.GROUP_TITLE,
            slug=consts.GROUP_SLUG,
            description=consts.GROUP_DESCRIPTION
        )
        cls.posts_total_count = 0
        for i in range(consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR):
            cls.post = Post.objects.create(
                author=cls.first_user,
                group=cls.first_group,
                text=consts.POST_TEXT,
                image=SimpleUploadedFile(
                    name=f'small_{ i }.gif',
                    content=consts.SMALL_GIF,
                    content_type='image/gif'
                )
            )
            cls.posts_total_count += 1
        cls.post_of_another_author_and_group = Post.objects.create(
            author=User.objects.create_user(username=consts.USER_USERNAME),
            group=Group.objects.create(
                title=consts.NEW_GROUP_TITLE,
                slug=consts.NEW_GROUP_SLUG,
                description=consts.GROUP_DESCRIPTION
            ),
            text=consts.POST_TEXT,
            image=cls.uploaded
        )
        cls.posts_total_count += 1
        cls.page_url_dict = {
            'index': reverse(
                'posts:index'
            ),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.first_group.slug}'}
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
            'new_group': reverse(
                'posts:group_list',
                kwargs={
                    'slug':
                    f'{cls.post_of_another_author_and_group.group.slug}'
                }
            ),
            'new_author_profile': reverse(
                'posts:profile',
                kwargs={
                    'username':
                    f'{cls.post_of_another_author_and_group.author.username}'
                }
            ),
            'new_profile_follow': reverse(
                'posts:profile_follow',
                kwargs={
                    'username':
                    f'{cls.post_of_another_author_and_group.author.username}'
                }
            ),
            'new_profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username':
                    f'{cls.post_of_another_author_and_group.author.username}'
                }
            ),
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

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in self.url_to_template_dict.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['index'])
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, consts.POST_TEXT)
        self.assertEqual(post_group_0, consts.NEW_GROUP_TITLE)
        self.assertEqual(post_author_0, consts.USER_USERNAME)
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertIsInstance(first_object, Post)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(self.page_url_dict['index'])
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            consts.MAX_POSTS_DISPLAYED
        )

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должны быть остальные посты.
        response = self.authorized_client.get(
            self.page_url_dict['index'] + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_total_count - consts.MAX_POSTS_DISPLAYED)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['group'])
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, consts.POST_TEXT)
        self.assertEqual(post_group_0, consts.GROUP_TITLE)
        self.assertEqual(post_author_0, consts.FIRST_USER_USERNAME)
        self.assertEqual(
            post_image_0,
            f'posts/small_{consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1}'
            '.gif'
        )
        self.assertIsInstance(first_object, Post)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.authorized_client.get(self.page_url_dict['group'])
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            consts.MAX_POSTS_DISPLAYED
        )

    def test_group_list_second_page_contains_two_records(self):
        # Проверка: на второй странице остальные посты.
        response = self.authorized_client.get(
            self.page_url_dict['group'] + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            (
                consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR
                - consts.MAX_POSTS_DISPLAYED
            )
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['profile'])
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, consts.POST_TEXT)
        self.assertEqual(post_group_0, consts.GROUP_TITLE)
        self.assertEqual(
            post_image_0,
            f'posts/small_{consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1}'
            '.gif'
        )
        for post in response.context['page_obj']:
            self.assertEqual(
                post.author.username,
                consts.FIRST_USER_USERNAME,
                'Посты не отсортированы по Автору'
            )
        self.assertIsInstance(first_object, Post)
        self.assertEqual(
            response.context['posts_count'],
            consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR
        )

    def test_profile_first_page_contains_ten_records(self):
        response = self.authorized_client.get(self.page_url_dict['profile'])
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            consts.MAX_POSTS_DISPLAYED
        )

    def test_profile_second_page_contains_two_records(self):
        # Проверка: на второй странице остальные посты.
        response = self.authorized_client.get(
            self.page_url_dict['profile'] + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            (
                consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR
                - consts.MAX_POSTS_DISPLAYED
            )
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['detail'])
        choosen_post = response.context['post']
        self.assertIsInstance(
            choosen_post,
            Post,
            msg='Post_detail не возвращает объект класса Post'
        )
        self.assertEqual(
            choosen_post.id,
            self.post.id,
            msg='Post_detail не возвращает выбранный по post_id объект'
        )
        self.assertEqual(
            response.context['author_posts_count'],
            consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR,
            msg=(
                'author_posts_count неверно считает количество постов автора'
            )
        )
        self.assertEqual(
            choosen_post.image,
            f'posts/small_{consts.NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1}'
            '.gif'
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit передает форму с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['edit'])
        choosen_post = response.context['post']
        self.assertEqual(
            choosen_post.id,
            self.post.id,
            msg='Post_edit не возвращает выбранный по post_id объект'
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        # Проверяем, что типы полей формы в словаре
        # context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(
                    form_field,
                    expected,
                    msg=(
                        f'Тип данных в форме поля { value } '
                        'не соответствует ожидаемому'
                    )
                )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create передает форму с правильным контекстом."""
        response = self.authorized_client.get(self.page_url_dict['create'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        # Проверяем, что типы полей формы в словаре
        # context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(
                    form_field,
                    expected,
                    msg=(
                        f'Тип данных в форме поля {value} '
                        'не соответствует ожидаемому'
                    )
                )

    def test_post_created_with_group_in_index_profile_group_list(self):
        new_post_with_group = self.post_of_another_author_and_group
        response = self.authorized_client.get(self.page_url_dict['index'])
        context_object = response.context['page_obj']
        self.assertIn(new_post_with_group, context_object)
        templates_pages_names = [
            self.page_url_dict['index'],
            self.page_url_dict['new_group'],
            self.page_url_dict['new_author_profile']
        ]
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                context_object = response.context['page_obj']
                self.assertIn(
                    new_post_with_group,
                    context_object,
                    msg=(
                        'Пост с указанной группой '
                        f'не был добавлен в {reverse_name}'
                    )
                )

    def test_follow_and_unfollow_func_works(self):
        author = self.post_of_another_author_and_group.author
        # Дважды пытаемся подписаться на одного автора
        response = self.authorized_client.get(
            self.page_url_dict['new_profile_follow']
        )
        response = self.authorized_client.get(
            self.page_url_dict['new_profile_follow']
        )
        # Запрашиваем страницу подписок
        response = self.authorized_client.get(
            self.page_url_dict['follow']
        )
        first_object = response.context['page_obj']
        # Проверяем что подписка сработала
        self.assertTrue(
            Follow.objects.filter(
                user=self.first_user,
                author=author
            ).exists()
        )
        # Проверяем что отображаются посты по подписке
        self.assertIn(
            self.post_of_another_author_and_group,
            first_object,
            msg=(
                f'Не работает подписка на автора {author.username}'
            )
        )
        # Проверяем, что подписаться на пользователя можно только один раз
        self.assertEqual(
            self.first_user.follower.count(),
            1,
            'Проверьте что подписаться на пользователя можно только один раз')
        # Отписываемся от автора
        response = self.authorized_client.get(
            self.page_url_dict['new_profile_unfollow']
        )
        response = self.authorized_client.get(self.page_url_dict['follow'])
        first_object = response.context['page_obj']
        # Проверяем что отписка сработала
        self.assertFalse(
            Follow.objects.filter(
                user=self.first_user,
                author=author
            ).exists()
        )
        # Проверяем что перестали отображаться посты по подписке
        self.assertNotIn(
            self.post_of_another_author_and_group,
            first_object,
            msg=(
                f'Не работает отписка от автора {author.username}'
            )
        )
