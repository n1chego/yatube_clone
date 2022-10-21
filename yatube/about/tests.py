from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        # Создаем экземпляр клиента
        self.guest_client = Client()

    def test_about_author_url_exists_and_uses_correct_template(self):
        """Проверка доступности адреса и шаблона для /about/<urls>/"""
        url_template_dict = {
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html'
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


class AboutPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем экземпляр клиента
        cls.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('about:tech'): 'about/tech.html',
            reverse('about:author'): 'about/author.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
