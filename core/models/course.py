from __future__ import annotations
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.generics import TimeStampedModel, PublishModel


# ----------------------------------------------------------------------------------------------------------------------
# Course
# ----------------------------------------------------------------------------------------------------------------------

# Category
class Category(TimeStampedModel, PublishModel):
    title = models.CharField(_('Атауы'), max_length=255)
    slug = models.SlugField(_('Кілттік сөз'), max_length=255, unique=True)
    description = models.TextField(_('Сипаттамасы'), blank=True)
    order = models.PositiveIntegerField(_('Реті'), default=0)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категориялар')
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return self.title


# Course
class Course(TimeStampedModel, PublishModel):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Бастапқы')
        INTERMEDIATE = 'intermediate', _('Орта')
        ADVANCED = 'advanced', _('Жоғары')

    category = models.ForeignKey(
        Category, verbose_name=_('Категория'),
        on_delete=models.PROTECT, related_name='courses',
    )
    title = models.CharField(_('Курс атауы'), max_length=255)
    slug = models.SlugField(_('Кілттік сөз'), max_length=255, unique=True)
    thumbnail = models.ImageField(_('Сурет'), upload_to='courses/thumbnails/', blank=True, null=True)
    description = models.TextField(_('Сипаттамасы'), blank=True)
    level = models.CharField(_('Деңгейі'), max_length=20, choices=Level.choices, default=Level.BEGINNER)
    order = models.PositiveIntegerField(_('Реті'), default=0)

    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курстар')
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return self.title


# Module
class Module(TimeStampedModel, PublishModel):
    course = models.ForeignKey(
        Course, verbose_name=_('Курс'),
        on_delete=models.CASCADE, related_name='modules',
    )
    title = models.CharField(_('Модуль атауы'), max_length=255)
    description = models.TextField(_('Сипаттамасы'), blank=True)
    order = models.PositiveIntegerField(_('Реті'), default=0)

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модульдер')
        ordering = ['course_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['course', 'order'], name='uniq_module_order_in_course'),
        ]
        indexes = [
            models.Index(fields=['course', 'order']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return f"{self.course.title} — {self.title}"


# Lesson
class Lesson(TimeStampedModel, PublishModel):
    module = models.ForeignKey(
        Module, verbose_name=_('Модуль'),
        on_delete=models.CASCADE, related_name='lessons',
    )
    title = models.CharField(_('Сабақ атауы'), max_length=255)
    description = models.TextField(_('Сипаттамасы'), blank=True)
    order = models.PositiveIntegerField(_('Реті'), default=0)
    duration = models.PositiveIntegerField(_('Ұзақтығы (мин)'), default=0)

    class Meta:
        verbose_name = _('Сабақ')
        verbose_name_plural = _('Сабақтар')
        ordering = ['module_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['module', 'order'], name='uniq_lesson_order_in_module'),
        ]
        indexes = [
            models.Index(fields=['module', 'order']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return f"{self.module.title} — {self.title}"
