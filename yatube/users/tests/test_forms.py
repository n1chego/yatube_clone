from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


FIRST_USER_USERNAME = 'Auth'
USER_USERNAME = 'auth'


class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        # Создаем пользователя
        cls.first_user = User.objects.create_user(
            username=FIRST_USER_USERNAME
        )
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.user = User.objects.create_user(username=USER_USERNAME)

    def test_create_user(self):
        """Валидная форма создает запись в User."""
        # Подсчитаем количество записей в Post
        users_count = User.objects.count()

        form_data = {
            'username': 'Some_user',
            'email': 'some_user@yandex.ru',
            'password1': '1357Password',
            'password2': '1357Password'
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        print(self.user.email)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(User.objects.count(), users_count + 1)
        # Проверяем, что создалась запись с заданными параметрами
        self.assertTrue(
            User.objects.filter(
                username='Some_user',
                email='some_user@yandex.ru'
            ).exists()
        )
