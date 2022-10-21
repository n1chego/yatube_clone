from http import HTTPStatus
from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        # Создаем экземпляр клиента
        self.guest_client = Client()

    def test_auth_author_url_exists_and_uses_correct_template(self):
        """Проверка доступности адреса и шаблона для /auth/<urls>/"""
        url_template_dict = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in url_template_dict.items():
            response = self.guest_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка при запросе к {url}'
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Не верный шаблон при вызове {url}'
                )
