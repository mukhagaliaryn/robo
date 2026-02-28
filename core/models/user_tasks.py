from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Task, Option, UserLesson, Video, Question, MatchingItem, MatchingColumn, Reading


# UserTask model
# ----------------------------------------------------------------------------------------------------------------------
class UserTask(models.Model):
    user_lesson = models.ForeignKey(
        UserLesson, on_delete=models.CASCADE,
        related_name='user_tasks', verbose_name=_('Қолданушының сабағы')
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='user_tasks', verbose_name=_('Тапсырма')
    )
    submitted_at = models.DateTimeField(_('Жіберілген уақыты'), auto_now_add=True)
    rating = models.PositiveSmallIntegerField(_('Жалпы бағасы'), default=0)
    is_completed = models.BooleanField(_('Орындалды'), default=False)

    class Meta:
        verbose_name = _('Қолданушының тапсырмасы')
        verbose_name_plural = _('Қолданушының тапсырмалары')

    def __str__(self):
        return f'{self.user_lesson.user} | {self.task}'


# UserVideo model
# ----------------------------------------------------------------------------------------------------------------------
class UserVideo(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Қолданушының тапсырмасы')
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE,
        related_name='user_videos', verbose_name=_('Видеосабақ')
    )
    watched_seconds = models.PositiveIntegerField(_('Қараған уақыт (сек)'), default=0)
    is_completed = models.BooleanField(_('Аяқталған'), default=False)

    class Meta:
        verbose_name = _('Қолданушының видеосабағы')
        verbose_name_plural = _('Қолданушының видеосабақтары')


# UserReading
# ----------------------------------------------------------------------------------------------------------------------
class UserReading(models.Model):
    user_task = models.OneToOneField(UserTask, on_delete=models.CASCADE, related_name='user_reading')
    reading = models.ForeignKey(
            Reading, on_delete=models.CASCADE,
            related_name='user_reading', verbose_name=_('Оқу мәтіні')
    )
    is_read = models.BooleanField(default=False)
    read_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Қолданушының оқу мәтіні')
        verbose_name_plural = _('Қолданушының оқу мәтіндері')


# Test model
# ----------------------------------------------------------------------------------------------------------------------
# UserAnswer model
class UserAnswer(models.Model):
    user_task = models.ForeignKey(
        UserTask, on_delete=models.CASCADE, null=True,
        related_name='user_options', verbose_name=_('Қолданушы тапсырмасы')
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, null=True,
        related_name='user_options', verbose_name=_('Жауап')
    )
    options = models.ManyToManyField(Option, related_name='user_answers', verbose_name=_('Таңдалған жауаптар'))

    class Meta:
        verbose_name = _('Таңдалған жауап')
        verbose_name_plural = _('Таңдалған жауаптар')


# UserMatchingAnswer model
# ----------------------------------------------------------------------------------------------------------------------
class UserMatchingAnswer(models.Model):
    user_task = models.ForeignKey(
        UserTask, related_name='matching_answers',
        on_delete=models.CASCADE, verbose_name=_('Қолданушының тапсырмасы')
    )
    item = models.ForeignKey(
        MatchingItem, on_delete=models.CASCADE, verbose_name=_('Жауап')
    )
    selected_column = models.ForeignKey(
        MatchingColumn, on_delete=models.CASCADE,
        verbose_name=_('Баған'), null=True, blank=True,
    )
    is_correct = models.BooleanField(_('Дұрыс жауап'), default=False)

    def check_answer(self):
        self.is_correct = self.item.correct_column_id == self.selected_column_id
        self.save()

    class Meta:
        verbose_name = _('Қолданушының сәйкестендіруі')
        verbose_name_plural = _('Қолданушының сәйкестендірулері')