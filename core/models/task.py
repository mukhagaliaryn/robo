from __future__ import annotations
from decimal import Decimal
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
        READING = 'reading', _('Оқылым'),
        TEST = 'test', _('Тест')
        MATCHING = 'matching', _('Сәйкестендіру')
        # WRITING = 'writing', _('Жазбаша'),

    lesson = models.ForeignKey(
        Lesson, verbose_name=_('Сабақ'),
        on_delete=models.CASCADE, related_name='tasks',
    )
    title = models.CharField(_('Тапсырма атауы'), max_length=255)
    task_type = models.CharField(_('Тапсырма түрі'), max_length=20, choices=TaskType.choices)
    order = models.PositiveIntegerField(_('Реті'), default=0)
    # Бағалау шкаласы 1-10
    rating = models.PositiveSmallIntegerField(_('Балл (1–10)'), default=0)
    duration_sec = models.PositiveIntegerField(_('Уақыт шектеуі (сек)'), default=0)
    is_required = models.BooleanField(_('Міндетті ме'), default=True)
    # UI/логика параметрлері (shuffle, time_limit, layout т.б.)
    params = models.JSONField(_('Параметрлер'), blank=True, default=dict)

    class Meta:
        verbose_name = _('Тапсырма')
        verbose_name_plural = _('Тапсырмалар')
        ordering = ['lesson_id', 'order']
        constraints = [
            models.UniqueConstraint(fields=['lesson', 'order'], name='uniq_task_order_in_lesson'),
            models.CheckConstraint(
                name='chk_task_rating_1_10',
                condition=(models.Q(rating__gte=1) & models.Q(rating__lte=10))
            ),
        ]
        indexes = [
            models.Index(fields=['lesson', 'order']),
            models.Index(fields=['task_type']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self) -> str:
        return f"{self.lesson.title} — {self.title}"


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
        return f"Видео: {self.task.title}"


# Reading
# ----------------------------------------------------------------------------------------------------------------------
class ReadingTask(models.Model):
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
        return f'Оқу: {self.task.title}'


# Test
# ----------------------------------------------------------------------------------------------------------------------
class TestTask(TimeStampedModel):
    task = models.OneToOneField(
        Task, verbose_name=_('Тапсырма'),
        on_delete=models.CASCADE, related_name='test',
        limit_choices_to={"task_type": Task.TaskType.TEST},
    )
    shuffle_questions = models.BooleanField(_('Сұрақтарды араластыру'), default=True)
    shuffle_options = models.BooleanField(_('Нұсқаларды араластыру'), default=True)

    class Meta:
        verbose_name = _('Тест тапсырма')
        verbose_name_plural = _('Тест тапсырмалар')

    def __str__(self) -> str:
        return f"Тест: {self.task.title}"


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
    points = models.DecimalField(_('Ұпай'), max_digits=6, decimal_places=2, default=Decimal('1.00'))
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
        return f"Сұрақ: {self.text[:60]}"


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
        return self.text


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
    layout = models.CharField(_('Көрсету түрі'), max_length=10, choices=Layout.choices, default=Layout.ROW)
    shuffle = models.BooleanField(_('Араластыру'), default=True)

    class Meta:
        verbose_name = _('Сәйкестендіру тапсырма')
        verbose_name_plural = _('Сәйкестендіру тапсырмалар')

    def __str__(self) -> str:
        return f"Сәйкестендіру: {self.task.title}"


# MatchingPair
class MatchingPair(TimeStampedModel):
    matching_task = models.ForeignKey(
        MatchingTask, verbose_name=_('Сәйкестендіру тапсырма'),
        on_delete=models.CASCADE, related_name='pairs',
    )
    left_text = models.CharField(_('Сол жақ мәтін'), max_length=255)
    right_text = models.CharField(_('Оң жақ мәтін'), max_length=255)
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
