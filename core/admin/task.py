from django.contrib import admin
from core.admin._mixins import LinkedAdminMixin
from core.forms.task import VideoAdminForm, ReadingAdminForm, QuestionAdminForm, OptionAdminForm, MatchingPairAdminForm
from core.models.task import Task, VideoTask, ReadingTask, TestTask, Question, Option, MatchingTask, MatchingPair


# ----------------------------------------------------------------------------------------------------------------------
# Inlines
# ----------------------------------------------------------------------------------------------------------------------
class TaskInline(admin.TabularInline, LinkedAdminMixin):
    model = Task
    extra = 0
    show_change_link = False
    fields = ('order', 'task_type', 'rating', 'duration', 'is_published', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('order',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class VideoTaskInline(admin.TabularInline):
    model = VideoTask
    extra = 0
    show_change_link = False
    form = VideoAdminForm


class ReadingTaskInline(admin.TabularInline):
    model = ReadingTask
    extra = 0
    show_change_link = False
    form = ReadingAdminForm


class TestTaskInline(admin.TabularInline, LinkedAdminMixin):
    model = TestTask
    extra = 0
    show_change_link = False
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class MatchingTaskInline(admin.TabularInline, LinkedAdminMixin):
    model = MatchingTask
    extra = 0
    show_change_link = False
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class QuestionInline(admin.TabularInline, LinkedAdminMixin):
    model = Question
    extra = 0
    show_change_link = False
    fields = ('order', 'question_type', 'points', 'text', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('order',)
    form = QuestionAdminForm

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    show_change_link = False
    fields = ('text', 'is_correct')
    form = OptionAdminForm


class MatchingPairInline(admin.TabularInline):
    model = MatchingPair
    extra = 0
    show_change_link = False
    fields = ('order', 'left_text', 'right_text')
    ordering = ('order',)
    form = MatchingPairAdminForm


# ----------------------------------------------------------------------------------------------------------------------
# Admins
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('task_type', 'order', 'rating', 'is_published', 'lesson_link')
    list_filter = ('is_published', 'task_type', 'lesson__module__course')
    ordering = ('lesson_id', 'order')
    readonly_fields = ('lesson_link',)

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []

        m = {
            Task.TaskType.VIDEO: [VideoTaskInline],
            Task.TaskType.READING: [ReadingTaskInline],
            Task.TaskType.TEST: [TestTaskInline],
            Task.TaskType.MATCHING: [MatchingTaskInline],
        }
        return m.get(obj.task_type, [])

    def lesson_link(self, obj):
        return self.parent_link(obj, parent_field_name='lesson')

    lesson_link.short_description = 'Сабақ'


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('task_link', 'max_points', 'shuffle_questions', 'shuffle_options', 'task_link')
    search_fields = ('task__title',)
    readonly_fields = ('task_link',)
    inlines = (QuestionInline,)

    def task_link(self, obj):
        return self.parent_link(obj, parent_field_name='task')

    task_link.short_description = 'Тапсырма'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('short_text', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'test_task')
    search_fields = ('text',)
    ordering = ('test_task_id', 'order')
    readonly_fields = ('test_link',)
    inlines = (OptionInline,)
    form = QuestionAdminForm

    def short_text(self, obj):
        t = obj.text or ''
        return (t[:80] + '...') if len(t) > 80 else t

    short_text.short_description = 'Сұрақ'

    def test_link(self, obj):
        return self.parent_link(obj, parent_field_name='test_task')

    test_link.short_description = 'Тест'


@admin.register(MatchingTask)
class MatchingTaskAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('task_link', 'layout', 'shuffle', 'task_link')
    search_fields = ('task__title',)
    readonly_fields = ('task_link',)
    inlines = (MatchingPairInline,)

    def task_link(self, obj):
        return self.parent_link(obj, parent_field_name='task')

    task_link.short_description = 'Тапсырма'

