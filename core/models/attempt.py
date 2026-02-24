from __future__ import annotations
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import Task, Question
from core.models.course import Lesson
from core.models.generics import TimeStampedModel


# ----------------------------------------------------------------------------------------------------------------------
# Progress
# ----------------------------------------------------------------------------------------------------------------------
# UserCourse
class UserCourse(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Оқып жатыр')
        COMPLETED = 'completed', _('Аяқталған')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Қолданушы'),
        on_delete=models.CASCADE, related_name='user_courses',
    )
    course = models.ForeignKey(
        'Course', verbose_name=_('Курс'),
        on_delete=models.CASCADE, related_name='user_courses',
    )
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percent = models.DecimalField(_('Прогресс (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    percentage = models.DecimalField(_('Пайыз (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    score = models.DecimalField(_('Жиынтық балл'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    started_at = models.DateTimeField(_('Басталған уақыты'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Аяқталған уақыты'), blank=True, null=True)

    last_lesson = models.ForeignKey(
        'Lesson', verbose_name=_('Соңғы сабақ'),
        on_delete=models.SET_NULL, blank=True, null=True, related_name='+',
    )

    class Meta:
        verbose_name = _('Қолданушы курсы')
        verbose_name_plural = _('Қолданушы курстары')
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='uniq_user_course'),
        ]

    def __str__(self):
        return f'{self.user} — {self.course.title}'


# UserModule
class UserModule(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Оқып жатыр')
        COMPLETED = 'completed', _('Аяқталған')

    module = models.ForeignKey(
        'Module', verbose_name=_('Модуль'),
        on_delete=models.CASCADE, related_name='user_modules',
    )
    user_course = models.ForeignKey(
        UserCourse, verbose_name=_('Қолданушы курсы'),
        on_delete=models.CASCADE, related_name='user_modules',
    )
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percent = models.DecimalField(_('Прогресс (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    percentage = models.DecimalField(_('Пайыз (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    score = models.DecimalField(_('Жиынтық балл'), max_digits=10, decimal_places=2, default=Decimal('0.00'))

    last_lesson = models.ForeignKey(
        'Lesson', verbose_name=_('Соңғы сабақ'),
        on_delete=models.SET_NULL, blank=True, null=True, related_name='+',
    )

    class Meta:
        verbose_name = _('Қолданушы модулі')
        verbose_name_plural = _('Қолданушы модульдері')
        constraints = [
            models.UniqueConstraint(fields=['user_course', 'module'], name='uniq_user_module'),
        ]

    def __str__(self):
        return f'{self.user_course.user} — {self.module.title}'


# UserLesson
class UserLesson(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Оқып жатыр')
        COMPLETED = 'completed', _('Аяқталған')

    user_module = models.ForeignKey(
        UserModule, verbose_name=_('Қолданушы модулі'),
        on_delete=models.CASCADE, related_name='lessons',
    )
    lesson = models.ForeignKey(
        Lesson, verbose_name=_('Сабақ'),
        on_delete=models.CASCADE, related_name='user_lessons',
    )
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    time_spent_sec = models.PositiveIntegerField(_('Жұмсалған уақыт (сек)'), default=0)
    score = models.DecimalField(_('Жиынтық балл'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    percentage = models.DecimalField(_('Пайыз (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    progress_percent = models.DecimalField(_('Прогресс (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = _('Қолданушы сабағы')
        verbose_name_plural = _('Қолданушы сабақтары')
        constraints = [
            models.UniqueConstraint(fields=['user_module', 'lesson'], name='uniq_user_lesson'),
        ]

    def __str__(self):
        return f'{self.user_module.user_course.user} — {self.lesson.title}'


# UserTask
class UserTask(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Орындап жатыр')
        SUBMITTED = 'submitted', _('Жіберілген')
        GRADED = 'graded', _('Бағаланған')
        COMPLETED = 'completed', _('Аяқталған')

    user_lesson = models.ForeignKey(
        UserLesson, verbose_name=_('Қолданушы сабағы'),
        on_delete=models.CASCADE, related_name='user_tasks',
    )
    task = models.ForeignKey(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='user_tasks',
    )
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    started_at = models.DateTimeField(_('Басталған уақыты'), blank=True, null=True)
    submitted_at = models.DateTimeField(_('Жіберілген уақыты'), blank=True, null=True)
    graded_at = models.DateTimeField(_('Бағаланған уақыты'), blank=True, null=True)

    attempts_count = models.PositiveIntegerField(_('Тапсыру саны'), default=0)
    score = models.DecimalField(_('Жинаған балл'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    teacher_feedback = models.TextField(_('Оқытушы пікірі'), blank=True)

    class Meta:
        verbose_name = _('Қолданушы тапсырмасы')
        verbose_name_plural = _('Қолданушы тапсырмалары')
        constraints = [
            models.UniqueConstraint(fields=['user_lesson', 'task'], name='uniq_user_task'),
        ]

    def __str__(self) -> str:
        return f"{self.user_lesson.user_module.user_course.user} — {self.task.title}"


# ----------------------------------------------------------------------------------------------------------------------
# Attempts + Answers (full results storage)
# ----------------------------------------------------------------------------------------------------------------------
class TaskAttempt(TimeStampedModel):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('Орындап жатыр')
        SUBMITTED = 'submitted', _('Жіберілген')
        CANCELLED = 'cancelled', _('Болдырылмады')

    user_task = models.ForeignKey(
        UserTask, verbose_name=_('Қолданушы тапсырмасы'),
        on_delete=models.CASCADE, related_name='attempts',
    )
    attempt_no = models.PositiveIntegerField(_('Нәтиже нөмірі'), default=1)
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)

    started_at = models.DateTimeField(_('Басталған уақыты'), blank=True, null=True)
    submitted_at = models.DateTimeField(_('Жіберілген уақыты'), blank=True, null=True)

    score = models.DecimalField(_('Әрекет бойынша балл'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    meta = models.JSONField(_('Қосымша мәлімет'), blank=True, default=dict)

    class Meta:
        verbose_name = _('Тапсыру әрекеті')
        verbose_name_plural = _('Тапсыру әрекеттері')
        ordering = ['user_task_id', 'attempt_no']
        constraints = [
            models.UniqueConstraint(fields=['user_task', 'attempt_no'], name='uniq_attempt_no_per_user_task'),
        ]
        indexes = [
            models.Index(fields=['user_task', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.user_task} — #{self.attempt_no}"


class VideoProgress(TimeStampedModel):
    user_task = models.OneToOneField(
        UserTask, verbose_name=_('Қолданушы тапсырмасы'),
        on_delete=models.CASCADE, related_name='video_progress',
    )
    watched_sec = models.PositiveIntegerField(_('Қараған уақыты (сек)'), default=0)
    last_position_sec = models.PositiveIntegerField(_('Соңғы позиция (сек)'), default=0)
    is_completed = models.BooleanField(_('Аяқталды ма'), default=False)

    class Meta:
        verbose_name = _('Видео прогресс')
        verbose_name_plural = _('Видео прогрестер')

    def __str__(self) -> str:
        return f"{self.user_task} — видео прогресс"


class QuestionAttempt(TimeStampedModel):
    attempt = models.ForeignKey(
        TaskAttempt, verbose_name=_('Әрекет'),
        on_delete=models.CASCADE, related_name='question_attempts',
    )
    question = models.ForeignKey(
        Question, verbose_name=_('Сұрақ'),
        on_delete=models.CASCADE, related_name='+',
    )

    selected_option_ids = models.JSONField(_('Таңдалған нұсқалар'), blank=True, default=list)
    option_order = models.JSONField(_('Нұсқалар реті (freeze)'), blank=True, default=list)
    is_correct = models.BooleanField(_('Дұрыс па'), default=False)
    score = models.DecimalField(_('Ұпай'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    answered_at = models.DateTimeField(_('Жауап берілген уақыты'), blank=True, null=True)

    class Meta:
        verbose_name = _('Сұрақ нәтижесі')
        verbose_name_plural = _('Сұрақ нәтижелері')
        indexes = [
            models.Index(fields=['attempt', 'question']),
        ]

    def __str__(self) -> str:
        return f"{self.question} — әрекет"


class MatchingAttempt(TimeStampedModel):
    attempt = models.OneToOneField(
        TaskAttempt, verbose_name=_('Әрекет'),
        on_delete=models.CASCADE, related_name='matching_attempt',
    )
    # формат: [{"pair_id": 1, "right_text": "..."}] немесе {"left":"right"} — өзіңе ыңғайлысын бекітесің
    answer = models.JSONField(_('Жауап'), default=dict, blank=True)
    is_correct = models.BooleanField(_('Дұрыс па'), default=False)
    score = models.DecimalField(_('Ұпай'), max_digits=8, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = _('Сәйкестендіру жауабы')
        verbose_name_plural = _('Сәйкестендіру жауаптары')

    def __str__(self) -> str:
        return f"{self.attempt} — сәйкестендіру"
