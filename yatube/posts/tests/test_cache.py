from django.test import Client, TestCase
from django.urls import reverse

from posts import consts
from posts.models import Post, User


class PostCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.first_user = User.objects.create_user(
            username=consts.FIRST_USER_USERNAME
        )

    def test_index_page_cache(self):
        # Ожидаемый текст поста
        expected_post_text = 'test_text'
        # Создаем новый пост с ожидаемым текстом
        post = Post.objects.create(
            author=self.first_user,
            text=expected_post_text
        )
        # Проверяем что запись создана с нужным текстом
        self.assertEqual(expected_post_text, post.text)
        # Запрашиваем ответ от главной страницы
        response = self.guest_client.get(reverse('posts:index'))
        # Считаем количество постов,переданное в контекст
        posts_count_with_added_post = len(response.context['page_obj'])
        # Убеждаемся что пост добавлен в бд
        self.assertEqual(
            1,
            posts_count_with_added_post,
            'Пост не добавлен в бд для проверки кеширования'
        )
        # Удаляем все посты из бд
        post.delete()
        # Сеова запрашиваем ответ от главной страницы
        response = self.guest_client.get(reverse('posts:index'))
        # Считаем количество постов,переданное в контекст
        post_count_after_deletion = len(response.context['page_obj'])
        # Убеждаемся что пост удален из бд
        self.assertEqual(
            0,
            post_count_after_deletion,
            'Пост не удален из бд для проверки кеширования'
        )
        # Проверяем что в новый ответ от главной страницы этот пост добавлен
        # так как выводятся кешированные данные
        self.assertIn(
            post.text,
            str(response.content),
            'Функция кеширования не работает для постов на странице index'
        )
