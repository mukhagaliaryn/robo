from __future__ import annotations
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.course import Lesson
from core.models.generics import TimeStampedModel, PublishModel


# ----------------------------------------------------------------------------------------------------------------------
# Tasks
# ----------------------------------------------------------------------------------------------------------------------

# Task
class Task(TimeStampedModel, PublishModel):
    class TaskType(models.TextChoices):
        VIDEO = 'video', _('Видео')
        READING = 'reading', _('Оқылым')
        TEST = 'test', _('Тест')
        MATCHING = 'matching', _('Сәйкестендіру')

    lesson = models.ForeignKey(
        Lesson, verbose_name=_('Сабақ'),
        on_delete=models.CASCADE, related_name='tasks',
    )
    task_type = models.CharField(_('Тапсырма түрі'), max_length=20, choices=TaskType.choices)
    order = models.PositiveIntegerField(_('Реті'), default=0)
    is_gradable = models.BooleanField(
        _('Бағалана ма'),
        default=True,
        help_text=_('Видео/оқылым үшін False, тест/сәйкестендіру үшін True'),
    )
    rating = models.PositiveSmallIntegerField(
        _('Балл (1–10)'),
        blank=True,
        null=True,
        help_text=_('Тек баға қойылатын тапсырмалар үшін'),
    )
    duration = models.PositiveIntegerField(_('Уақыты (мин)'), default=0)
    is_required = models.BooleanField(_('Міндетті ме'), default=True)

    class Meta:
        verbose_name = _('Тапсырма')
        verbose_name_plural = _('Тапсырмалар')
        ordering = ['lesson_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['lesson', 'order'], name='uniq_task_order_in_lesson'),
            models.CheckConstraint(
                name='chk_task_grading_rules',
                condition=(
                        (models.Q(task_type__in=['video', 'reading']) & models.Q(is_gradable=False) & models.Q(
                            rating__isnull=True))
                        |
                        (models.Q(task_type__in=['test', 'matching']) & models.Q(is_gradable=True) & models.Q(
                            rating__gte=1) & models.Q(rating__lte=10))
                ),
            ),
        ]
        indexes = [
            models.Index(fields=['lesson', 'order']),
            models.Index(fields=['task_type']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return f"{self.lesson.title} — {self.get_task_type_display()}"

    def save(self, *args, **kwargs):
        if self.task_type in ['video', 'reading']:
            self.is_gradable = False
            self.rating = None
        else:
            self.is_gradable = True
            if self.rating is None:
                self.rating = 1
        super().save(*args, **kwargs)


# Video
# ----------------------------------------------------------------------------------------------------------------------
class VideoTask(TimeStampedModel):
    task = models.OneToOneField(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='video',
        limit_choices_to={"task_type": Task.TaskType.VIDEO},
    )
    url = models.TextField(_('Видео сілтемесі'))
    min_watch_sec = models.PositiveIntegerField(_('Минимум қарау уақыты (сек)'), default=0)
    allow_skip = models.BooleanField(_('Өткізіп жіберуге бола ма'), default=True)

    class Meta:
        verbose_name = _('Видео тапсырма')
        verbose_name_plural = _('Видео тапсырмалар')

    def __str__(self) -> str:
        return f"Видео: {self.task.pk}"


# Reading
# ----------------------------------------------------------------------------------------------------------------------
class ReadingTask(TimeStampedModel):
    task = models.OneToOneField(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='reading',
        limit_choices_to={'task_type': 'reading'},
    )
    content = models.TextField(
        _('Оқу мәтіні'),
        help_text=_('Қолданушыға көрсетілетін мәтін'),
    )

    class Meta:
        verbose_name = _('Оқу тапсырмасы')
        verbose_name_plural = _('Оқу тапсырмалары')

    def __str__(self) -> str:
        return f'Оқу: {self.task.pk}'


# Test
# ----------------------------------------------------------------------------------------------------------------------
class TestTask(TimeStampedModel):
    task = models.OneToOneField(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='test',
        limit_choices_to={"task_type": Task.TaskType.TEST},
    )
    title = models.CharField(_('Тақырыбы'), max_length=128)
    max_points = models.PositiveSmallIntegerField(_('Макс. ұпай'), default=0)
    shuffle_questions = models.BooleanField(_('Сұрақтарды араластыру'), default=True)
    shuffle_options = models.BooleanField(_('Нұсқаларды араластыру'), default=True)

    class Meta:
        verbose_name = _('Тест тапсырма')
        verbose_name_plural = _('Тест тапсырмалар')

    def __str__(self) -> str:
        return f"Тест: {self.title}"


# Question
class Question(TimeStampedModel):
    class QuestionType(models.TextChoices):
        SINGLE = 'single', _('Бір дұрыс жауап')
        MULTI = 'multi', _('Бірнеше дұрыс жауап')

    test_task = models.ForeignKey(
        TestTask, verbose_name=_('Тест тапсырма'),
        on_delete=models.CASCADE, related_name='questions',
    )
    text = models.TextField(_('Сұрақ мәтіні'))
    question_type = models.CharField(_('Сұрақ түрі'), max_length=10, choices=QuestionType.choices, default=QuestionType.SINGLE)
    points = models.PositiveSmallIntegerField(_('Ұпай'), default=0)
    order = models.PositiveIntegerField(_('Реті'), default=0)

    class Meta:
        verbose_name = _('Сұрақ')
        verbose_name_plural = _('Сұрақтар')
        ordering = ['test_task_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['test_task', 'order'], name='uniq_question_order_in_test_task'),
        ]
        indexes = [
            models.Index(fields=['test_task', 'order']),
        ]

    def __str__(self) -> str:
        return f"Сұрақ: {self.pk}"


# Option
class Option(TimeStampedModel):
    question = models.ForeignKey(
        Question, verbose_name=_('Сұрақ'),
        on_delete=models.CASCADE, related_name='options',
    )
    text = models.TextField(_('Жауап нұсқасы'))
    is_correct = models.BooleanField(_('Дұрыс па'), default=False)

    class Meta:
        verbose_name = _('Нұсқа')
        verbose_name_plural = _('Нұсқалар')

    def __str__(self) -> str:
        return f"Нұсқа: {self.pk}"


# Matching
# ----------------------------------------------------------------------------------------------------------------------
# MatchingTask
class MatchingTask(TimeStampedModel):
    class Layout(models.TextChoices):
        ROW = 'row', _('Қатар (row)')
        COL = 'col', _('Баған (col)')

    task = models.OneToOneField(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='matching',
        limit_choices_to={'task_type': Task.TaskType.MATCHING},
    )
    title = models.CharField(_('Тақырыбы'), max_length=128)
    layout = models.CharField(_('Көрсету түрі'), max_length=10, choices=Layout.choices, default=Layout.ROW)
    shuffle = models.BooleanField(_('Араластыру'), default=True)

    class Meta:
        verbose_name = _('Сәйкестендіру тапсырма')
        verbose_name_plural = _('Сәйкестендіру тапсырмалар')

    def __str__(self) -> str:
        return f"Сәйкестендіру: {self.title}"


# MatchingPair
class MatchingPair(TimeStampedModel):
    matching_task = models.ForeignKey(
        MatchingTask, verbose_name=_('Сәйкестендіру тапсырма'),
        on_delete=models.CASCADE, related_name='pairs',
    )
    left_text = models.TextField(_('Сол жақ мәтін'))
    right_text = models.TextField(_('Оң жақ мәтін'))
    order = models.PositiveIntegerField(_('Реті'), default=0)

    class Meta:
        verbose_name = _('Жұп')
        verbose_name_plural = _('Жұптар')
        ordering = ['matching_task_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['matching_task', 'order'], name='uniq_pair_order_in_matching'),
        ]

    def __str__(self) -> str:
        return f"{self.left_text} → {self.right_text}"


# class WritingTask(TimeStampedModel):
#     class AnswerMode(models.TextChoices):
#         TEXT = 'text', _('Мәтін')
#         NUMBER = 'number', _('Сан')
#         SYMBOL = 'symbol', _('Символ/таңба')
#
#     class CompareMode(models.TextChoices):
#         EXACT = 'exact', _('Дәл сәйкес')
#         CASE_INSENSITIVE = 'case_insensitive', _('Регистрсіз салыстыру')
#         TRIM_CASE_INSENSITIVE = 'trim_case_insensitive', _('Бос орын + регистрсіз')
#
#     task = models.OneToOneField(
#         Task, verbose_name=_('Тапсырма'),
#         on_delete=models.CASCADE, related_name='writing',
#         limit_choices_to={'task_type': Task.TaskType.WRITING},
#     )
#     prompt = models.TextField(_('Нұсқаулық/мәтін'), help_text=_('Қолданушы оқитын мәтін/тапсырма шарты'))
#     answer_mode = models.CharField(_('Жауап форматы'), max_length=20, choices=AnswerMode.choices, default=AnswerMode.TEXT)
#     compare_mode = models.CharField(_('Тексеру тәсілі'), max_length=30, choices=CompareMode.choices, default=CompareMode.TRIM_CASE_INSENSITIVE)
#     correct_answer = models.CharField(_('Дұрыс жауап'), max_length=255)
#
#     # Дұрыс/қате болғандағы көрсетілетін түсіндірме (optional)
#     explanation_ok = models.TextField(_('Дұрыс болса түсіндірме'), blank=True)
#     explanation_bad = models.TextField(_('Қате болса түсіндірме'), blank=True)
#
#     class Meta:
#         verbose_name = _('Енгізу тапсырма')
#         verbose_name_plural = _('Енгізу тапсырмалар')
#
#     def __str__(self) -> str:
#         return f"Енгізу: {self.task.title}"
