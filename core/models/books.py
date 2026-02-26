from django.db import models
from django.utils.translation import gettext_lazy as _

from config import settings


class Book(models.Model):
    title = models.CharField(_('Тақырыбы'), max_length=255)
    description = models.TextField(_('Сипаттамасы'), blank=True, default="")
    poster = models.ImageField(_('Мұқабасы'), upload_to="books/posters/", blank=True, null=True)
    file = models.FileField(_('Файл'), upload_to="books/pdf/")  # pdf

    is_active = models.BooleanField(_('Жарияланған'), default=True)
    order = models.PositiveIntegerField(_('Реті'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Кітап')
        verbose_name_plural = _('Кітаптар')
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title


class UserBook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="user_books", verbose_name=_('Қолданушы')
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name="user_books", verbose_name=_('Кітап')
    )
    is_saved = models.BooleanField(_('Сақталды'), default=True)
    last_page = models.PositiveIntegerField(_('Соңғы оқылған бет'), default=1)
    progress = models.PositiveSmallIntegerField(_('Прогресс'), default=0)

    saved_at = models.DateTimeField(_('Сақталған уақыты'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Өзгертілген уақыты'), auto_now=True)

    class Meta:
        verbose_name = _('Қолданушы кітабы')
        verbose_name_plural = _('Қолданушы кітаптары')
        unique_together = ("user", "book")
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"{self.user_id} -> {self.book_id}"
