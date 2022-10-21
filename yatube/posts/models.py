from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q

from core.models import CreatedModel
from .consts import SYMBOLS_LIMIT_FOR_STR_METHOD


User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа',
        blank=True,
        on_delete=models.SET_NULL,
        related_name='group_name',
        null=True,
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:SYMBOLS_LIMIT_FOR_STR_METHOD]


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text='Придумайте название группы'
    )
    slug = models.SlugField(
        verbose_name='Уникальный идентификатор группы',
        max_length=200,
        unique=True,
        help_text=(
            'Придумайте уникальный идентификатор для группы'
            'Используйте только латиницу, цифры, дефисы и знаки подчёркивания'
        )
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Краткое описание группы'
    )

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Пост, к которому будет относиться комментарий'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:SYMBOLS_LIMIT_FOR_STR_METHOD]


class Follow(models.Model):
    # все пользователи, кто подписан User.follower.all()
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    # все авторы, на кого подписан пользователь User.following.all()
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.CheckConstraint(
                name='not_same',
                check=~Q(author=F('user')),
            ),
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_pair',
            )
        )
