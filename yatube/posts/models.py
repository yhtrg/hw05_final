from django.contrib.auth import get_user_model
from django.db import models

from yatube.settings import QUANTITY_TEXT

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Текст поста')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    group = models.ForeignKey(
        Group,
        help_text='Группа, к которой относится пост',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:QUANTITY_TEXT]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(
        "Текст комментария",
        help_text="Введите текст комментария"
    )
    created = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.text[:QUANTITY_TEXT]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['-author']
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unnique_follow')
        ]

    def __str__(self) -> str:
        return self.user.username
