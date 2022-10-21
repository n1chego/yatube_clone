import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts import consts
from posts.models import Comment, Group, Post, User


@override_settings(MEDIA_ROOT=consts.TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        # Создаем пользователя
        cls.first_user = User.objects.create_user(
            username=consts.FIRST_USER_USERNAME
        )
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.first_user)
        cls.uploaded = SimpleUploadedFile(
            name=consts.IMAGE_NAME,
            content=consts.SMALL_GIF,
            content_type='image/gif'
        )
        # Создаем запись в базе данных для проверки сушествующего slug
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.user = User.objects.create_user(username=consts.USER_USERNAME)
        cls.group = Group.objects.create(
            title=consts.GROUP_TITLE,
            slug=consts.GROUP_SLUG,
            description=consts.GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.first_user,
            group=cls.group,
            text=consts.POST_TEXT,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.first_user,
            text=consts.COMMENT_TEXT
        )
        cls.page_url_dict = {
            'index': reverse('posts:index'),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{ cls.first_user.username }'}
            ),
            'detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'create': reverse('posts:post_create'),
            'edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'comment': reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{cls.post.id}'}
            ),
            'login_redirect': '/auth/login/?next=',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(consts.TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_second.gif',
            content=consts.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.page_url_dict['create'],
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.page_url_dict['profile'])
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданными параметрами
        post = Post.objects.first()
        self.assertEqual(
            post.text,
            form_data['text'],
            msg='Post_create неверно передает атрибут text'
        )
        self.assertEqual(
            post.group.id,
            form_data['group'],
            msg='Post_create неверно передает атрибут group'
        )
        self.assertEqual(
            post.image.name,
            f'posts/{form_data["image"]}',
            msg='Post_create неверно передает атрибут image'
        )
        # Пытался сделать цикл, image не сравнивается нормально
        # Может есть простые варианты как это сделать?
        '''for value, expected in form_data.items():
            with self.subTest(value=value):
                form_field = getattr(post, value)
                self.assertEqual(
                    form_field,
                    expected,
                    msg='Post_edit не возвращает выбранный по post_id объект'
                )'''

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_third.gif',
            content=consts.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный текст',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.page_url_dict['edit'],
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.page_url_dict['detail'])
        # Проверяем, что число постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись с заданными параметрами
        self.assertEqual(
            response.context['post'].text,
            form_data['text'],
            msg='Post_edit неверно передает атрибут text'
        )
        self.assertEqual(
            response.context['post'].group,
            None,
            msg='Post_edit неверно передает атрибут group'
        )
        self.assertEqual(
            response.context['post'].image,
            f'posts/{form_data["image"]}',
            msg='Post_edit неверно передает атрибут image'
        )

    def test_add_comment(self):
        """Валидная форма создает комментарий к посту."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.page_url_dict['comment'],
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.page_url_dict['detail'])
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Проверяем, что создалась запись с заданными параметрами
        comment = Comment.objects.first()
        self.assertEqual(
            comment.text,
            form_data['text'],
            msg='Add_post неверно передает атрибут text'
        )

    def test_not_auth_client_unable_to_create_edit_post_or_comment(self):
        '''Неавторизованный пользователь не может создать или отредактировать
        пост или комментарий'''
        address_objects_dict = {
            self.page_url_dict['comment']: Comment.objects,
            self.page_url_dict['create']: Post.objects,
            self.page_url_dict['edit']: Post.objects,
        }
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        for address, tested_objects in address_objects_dict.items():
            with self.subTest(address=address):
                objects_pre_count = tested_objects.count()
                response = self.guest_client.post(
                    address,
                    data=form_data,
                    follow=True
                )
                # Перенаправляет на страницу авторизации
                self.assertRedirects(
                    response,
                    f'{self.page_url_dict["login_redirect"]}{address}',
                    msg_prefix=f'Ошибка при переадресации от {address}'
                )
                # Не создались посты
                self.assertEqual(tested_objects.count(), objects_pre_count)
                # Не изменилось содержание
                self.assertNotEqual(
                    tested_objects.first().text,
                    form_data['text'],
                    msg='Add_post неверно передает атрибут text'
                )
