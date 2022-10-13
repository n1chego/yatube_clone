from django.test import TestCase

from posts.models import SYMBOLS_LIMIT_FOR_STR_METHOD, Post, Group, User


def cycle_for_class_verbose_name_tests(tested_class, field_verboses, self):
    for field, expected_value in field_verboses.items():
        with self.subTest(field=field):
            self.assertEqual(
                tested_class._meta.get_field(field).verbose_name,
                expected_value
            )


def cycle_for_class_help_text_tests(tested_class, field_help_text, self):
    for field, expected_value in field_help_text.items():
        with self.subTest(field=field):
            self.assertEqual(
                tested_class._meta.get_field(field).help_text,
                expected_value
            )


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тест названия группы',
            slug='Тест уникального идентификатора группы',
            description='Тест описания группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст поста'
        )

    def test_models_have_correct_object_names(self):
        post = self.post
        expected_object_name = post.text[:SYMBOLS_LIMIT_FOR_STR_METHOD]
        self.assertEqual(
            expected_object_name,
            str(post),
            'Ошибка при обращении с строковому методу класса Post'
        )
        group = self.group
        expected_object_name = group.title
        self.assertEqual(
            expected_object_name,
            str(group),
            'Ошибка при обращении с строковому методу класса Group'
        )

    def test_verbose_name(self):
        tested_class = self.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
            'created': 'Дата создания',
        }
        cycle_for_class_verbose_name_tests(tested_class, field_verboses, self)
        tested_class = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный идентификатор группы',
            'description': 'Описание',
        }
        cycle_for_class_verbose_name_tests(tested_class, field_verboses, self)

    def test_help_text(self):
        tested_class = self.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        cycle_for_class_help_text_tests(tested_class, field_help_text, self)
        tested_class = self.group
        field_help_text = {
            'title': 'Придумайте название группы',
            'slug': (
                'Придумайте уникальный идентификатор для группы'
                'Используйте только латиницу, '
                + 'цифры, дефисы и знаки подчёркивания'
            ),
            'description': 'Краткое описание группы',
        }
        cycle_for_class_help_text_tests(tested_class, field_help_text, self)
