from django.contrib.auth.forms import UserCreationForm
from django.test import Client, TestCase
from django.urls import reverse


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон signup передает форму с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'users:signup'
            )
        )
        form_field = response.context.get('form')
        self.assertIsInstance(
            form_field,
            UserCreationForm,
            msg='Проверьте что signup передает в шаблон объект формы User'
        )
