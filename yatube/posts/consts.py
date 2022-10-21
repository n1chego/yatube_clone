import tempfile

from django.conf import settings
'''from django.urls import reverse'''


# Решил засунуть все константы приложения и тестов в один файл,
# но была мысль раскидать константы по разным файлам отдельно
# для приложения и отдельно для тестов
COMMENT_TEXT = 'Текст комментария'
FIRST_USER_USERNAME = 'Auth'
GROUP_DESCRIPTION = 'Тест описания группы'
GROUP_SLUG = 'unique_slug'
GROUP_TITLE = 'Тест названия группы'
# Название тестового изображения
IMAGE_NAME = 'small.gif'
# Количество отображаемых на странице постов
MAX_POSTS_DISPLAYED = 10
NEW_GROUP_SLUG = 'unique_slug_2'
NEW_GROUP_TITLE = 'Новая группа'
NUMBER_OF_POSTS_OF_ONE_GROUP_AND_AUTHOR = 12
POST_TEXT = 'Тестовый текст поста'
# Тестовое изображение
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
# Количество символов возвращаемое при обращении к стоковому методу класса
SYMBOLS_LIMIT_FOR_STR_METHOD = 15
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
USER_USERNAME = 'auth'
# Есть ли смысл этот словарь выносить сюда как константу?
# Прийдется тогда усложнить структуру и сделать в каждом
# файле отдельный словарь со списком kwargs для подстановки
'''PAGE_URL_DICT = {
    'index': reverse(
        'posts:index'
    ),
    'group': reverse(
        'posts:group_list',
        kwargs={'slug': f'{cls.group.slug}'}
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
}'''
