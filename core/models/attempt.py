from __future__ import annotations
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from config import settings
from core.models import Task, Question
from core.models.course import Lesson
from core.models.generics import TimeStampedModel


# ----------------------------------------------------------------------------------------------------------------------
# Progress
# ----------------------------------------------------------------------------------------------------------------------

# UserLesson
class UserLesson(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Оқып жатыр')
        COMPLETED = 'completed', _('Аяқталған')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Қолданушы'),
        on_delete=models.CASCADE, related_name='user_lessons',
    )
    lesson = models.ForeignKey(
        Lesson, verbose_name=_('Сабақ'),
        on_delete=models.CASCADE, related_name='user_lessons',
    )
    status = models.CharField(_('Күйі'), max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    started_at = models.DateTimeField(_('Басталған уақыты'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Аяқталған уақыты'), blank=True, null=True)
    time_spent_sec = models.PositiveIntegerField(_('Жұмсалған уақыт (сек)'), default=0)
    score = models.DecimalField(_('Жиынтық балл'), max_digits=8, decimal_places=2, default=Decimal('0.00'))
    percentage = models.DecimalField(_('Пайыз (%)'), max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = _('Қолданушы сабағы')
        verbose_name_plural = _('Қолданушы сабақтары')
        constraints = [
            models.UniqueConstraint(fields=['user', 'lesson'], name='uniq_user_lesson'),
            models.CheckConstraint(
                name='chk_user_lesson_percent_0_100',
                condition=models.Q(percentage__gte=0) & models.Q(percentage__lte=100)
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['lesson', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.lesson.title}"


# UserTask
class UserTask(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Басталмаған')
        IN_PROGRESS = 'in_progress', _('Орындап жатыр')
        SUBMITTED = 'submitted', _('Жіберілген')
        GRADED = 'graded', _('Бағаланған')
        COMPLETED = 'completed', _('Аяқталған')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Қолданушы'),
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
            models.UniqueConstraint(fields=['user', 'task'], name='uniq_user_task'),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['task', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.task.title}"


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
            models.UniqueConstraint(fields=["user_task", "attempt_no"], name="uniq_attempt_no_per_user_task"),
        ]
        indexes = [
            models.Index(fields=['user_task', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.user_task} — #{self.attempt_no}"


class VideoProgress(TimeStampedModel):
    user_task = models.OneToOneField(
        UserTask,
        verbose_name=_("Қолданушы тапсырмасы"),
        on_delete=models.CASCADE,
        related_name="video_progress",
    )
    watched_sec = models.PositiveIntegerField(_("Қараған уақыты (сек)"), default=0)
    last_position_sec = models.PositiveIntegerField(_("Соңғы позиция (сек)"), default=0)
    is_completed = models.BooleanField(_("Аяқталды ма"), default=False)

    class Meta:
        verbose_name = _("Видео прогресс")
        verbose_name_plural = _("Видео прогрестер")

    def __str__(self) -> str:
        return f"{self.user_task} — видео прогресс"


class QuestionAttempt(TimeStampedModel):
    attempt = models.ForeignKey(
        TaskAttempt,
        verbose_name=_("Әрекет"),
        on_delete=models.CASCADE,
        related_name="question_attempts",
    )
    question = models.ForeignKey(
        Question,
        verbose_name=_("Сұрақ"),
        on_delete=models.CASCADE,
        related_name="+",
    )

    # Бір/көп таңдау үшін: id тізімі
    selected_option_ids = models.JSONField(_("Таңдалған нұсқалар"), blank=True, default=list)
    # shuffle freeze үшін (қажет болса):
    option_order = models.JSONField(_("Нұсқалар реті (freeze)"), blank=True, default=list)
    is_correct = models.BooleanField(_("Дұрыс па"), default=False)
    score = models.DecimalField(_("Ұпай"), max_digits=8, decimal_places=2, default=Decimal("0.00"))
    answered_at = models.DateTimeField(_("Жауап берілген уақыты"), blank=True, null=True)

    class Meta:
        verbose_name = _("Сұрақ әрекеті")
        verbose_name_plural = _("Сұрақ әрекеттері")
        indexes = [
            models.Index(fields=["attempt", "question"]),
        ]

    def __str__(self) -> str:
        return f"{self.question} — әрекет"


class MatchingAttempt(TimeStampedModel):
    attempt = models.OneToOneField(
        TaskAttempt,
        verbose_name=_("Әрекет"),
        on_delete=models.CASCADE,
        related_name="matching_attempt",
    )
    # формат: [{"pair_id": 1, "right_text": "..."}] немесе {"left":"right"} — өзіңе ыңғайлысын бекітесің
    answer = models.JSONField(_("Жауап"), default=dict, blank=True)
    is_correct = models.BooleanField(_("Дұрыс па"), default=False)
    score = models.DecimalField(_("Ұпай"), max_digits=8, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Сәйкестендіру әрекеті")
        verbose_name_plural = _("Сәйкестендіру әрекеттері")

    def __str__(self) -> str:
        return f"{self.attempt} — сәйкестендіру"
