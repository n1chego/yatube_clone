import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        # Создаем пользователя
        cls.first_user = User.objects.create_user(username='Auth')
        # Создаем второй клиент
        cls.authorized_client = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.first_user)
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
        # Создаем запись в базе данных для проверки сушествующего slug
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тест названия группы',
            slug='unique_slug',
            description='Тест описания группы'
        )
        cls.post = Post.objects.create(
            author=cls.first_user,
            group=cls.group,
            text='Тестовый текст поста',
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_second.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{ self.first_user.username }'}
        ))
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
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный текст',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'post_id': f'{self.post.id}'
            }
        ))
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
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.id}'}
        ))
        # Проверяем, увеличилось ли число rjvvtynfhbtd
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Проверяем, что создалась запись с заданными параметрами
        comment = Comment.objects.first()
        self.assertEqual(
            comment.text,
            form_data['text'],
            msg='Add_post неверно передает атрибут text'
        )
