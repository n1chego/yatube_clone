import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow, User
from posts.utils import MAX_POSTS_DISPLAYED


NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR = 12

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()
        # Создаем пользователя
        cls.first_user = User.objects.create_user(username='Auth')
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.first_user)
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Создаем записи в БД.
        cls.first_group = Group.objects.create(
            title='Тест названия группы',
            slug='unique_slug',
            description='Тест описания группы'
        )
        cls.posts_total_count = 0
        for i in range(NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR):
            cls.post = Post.objects.create(
                author=cls.first_user,
                group=cls.first_group,
                text='Тестовый текст поста',
                image=SimpleUploadedFile(
                    name=f'small_{ i }.gif',
                    content=cls.small_gif,
                    content_type='image/gif'
                )
            )
            cls.posts_total_count += 1
        cls.post_of_another_author_and_group = Post.objects.create(
            author=User.objects.create_user(username='author'),
            group=Group.objects.create(
                title='Новая группа',
                slug='unique_slug_2',
                description='Тест описания группы'
            ),
            text='Тестовый текст поста',
            image=cls.uploaded
        )
        cls.posts_total_count += 1

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.post
        group = self.first_group
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{ group.slug }'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{ post.author.username }'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{ post.id }'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{ post.id }'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(post_group_0, 'Новая группа')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertIsInstance(first_object, Post)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            MAX_POSTS_DISPLAYED
        )

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должны быть остальные посты.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_total_count - MAX_POSTS_DISPLAYED)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = self.first_group
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{ group.slug }'})
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(post_group_0, 'Тест названия группы')
        self.assertEqual(post_author_0, 'Auth')
        self.assertEqual(
            post_image_0,
            f'posts/small_{ NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1 }.gif'
        )
        self.assertIsInstance(first_object, Post)

    def test_group_list_first_page_contains_ten_records(self):
        group = self.first_group
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{ group.slug }'}
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            MAX_POSTS_DISPLAYED
        )

    def test_group_list_second_page_contains_two_records(self):
        # Проверка: на второй странице остальные посты.
        group = self.first_group
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{ group.slug }'}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR - MAX_POSTS_DISPLAYED
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{ post.author.username }'}
            )
        )
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(post_group_0, 'Тест названия группы')
        self.assertEqual(
            post_image_0,
            f'posts/small_{ NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1 }.gif'
        )
        for post in response.context['page_obj']:
            self.assertEqual(
                post.author.username,
                'Auth',
                'Посты не отсортированы по Автору'
            )
        self.assertIsInstance(first_object, Post)
        self.assertEqual(
            response.context['posts_count'],
            NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR
        )

    def test_profile_first_page_contains_ten_records(self):
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{ post.author.username }'}
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']),
            MAX_POSTS_DISPLAYED
        )

    def test_profile_second_page_contains_two_records(self):
        # Проверка: на второй странице остальные посты.
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{ post.author.username }'}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR - MAX_POSTS_DISPLAYED
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post detail сформирован с правильным контекстом."""
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{ post.id }'}
            )
        )
        choosen_post = response.context['post']
        self.assertIsInstance(
            choosen_post,
            Post,
            msg='Post_detail не возвращает объект класса Post'
        )
        self.assertEqual(
            choosen_post.id,
            post.id,
            msg='Post_detail не возвращает выбранный по post_id объект'
        )
        self.assertEqual(
            response.context['author_posts_count'],
            NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR,
            msg=(
                'author_posts_count неверно считает количество постов автора'
            )
        )
        self.assertEqual(
            choosen_post.image,
            f'posts/small_{ NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR-1 }.gif'
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit передает форму с правильным контекстом."""
        post = self.post
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{ post.id }'}
            )
        )
        choosen_post = response.context['post']
        self.assertEqual(
            choosen_post.id,
            post.id,
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
        response = self.authorized_client.get(
            reverse(
                'posts:post_create'
            )
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

    def test_post_created_with_group_in_index_profile_group_list(self):
        new_post_with_group = self.post_of_another_author_and_group
        response = self.authorized_client.get(reverse('posts:index'))  # ????
        context_object = response.context['page_obj']
        self.assertIn(new_post_with_group, context_object)
        templates_pages_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{ new_post_with_group.group.slug }'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{ new_post_with_group.author.username }'}
            ),
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
        # Подписываемся на автора
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{author.username}'}
            ))
        # Дважды пытаемся подписаться на одного автора
        response = self.authorized_client.get(reverse('posts:follow_index'))
        response = self.authorized_client.get(reverse('posts:follow_index'))
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
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{author.username}'}
            ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
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
