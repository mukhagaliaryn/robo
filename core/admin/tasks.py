from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin
from core.forms.subjects import ReadingAdminForm
from core.models import Task, Question, Option, Video, MatchingColumn, MatchingItem, Reading


# Task admin
# ----------------------------------------------------------------------------------------------------------------------
# Video Tab
class VideoTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Video
    extra = 0


# Reading Tab
class ReadingTab(admin.TabularInline):
    model = Reading
    extra = 0
    form = ReadingAdminForm


# Question Tab
class QuestionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Question
    fields = ('order', 'text', 'question_type', 'view_link', )
    extra = 0
    readonly_fields = ('view_link', )

    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_question_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = 'Сұраққа сілтеме'


# Matching Tab
class MatchingColumnTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = MatchingColumn
    extra = 0
    readonly_fields = ('view_link', )

    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:core_matchingcolumn_change', args=[obj.pk])
            return format_html('<a href="{}" class="view-link">Толығырақ</a>', url)
        return '-'

    view_link.short_description = 'Сәйкес бағанға сілтеме'


# ----------------------- Task admin -----------------------
@admin.register(Task)
class TaskAdmin(SummernoteModelAdmin):
    list_display = ('lesson', 'rating', 'duration', 'order', )
    readonly_fields = ('lesson_link', )

    def lesson_link(self, obj):
        if obj.lesson:
            url = reverse('admin:core_lesson_change', args=[obj.lesson.id])
            return format_html('<a href="{}" class="view-link">🔗 {}</a>', url, obj.lesson.title)
        return '-'

    lesson_link.short_description = 'Сабаққа сілтеме'

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []

        inline_instances = []

        if obj.task_type == 'video':
            inline_instances = [VideoTab(self.model, self.admin_site)]
        elif obj.task_type == 'reading':
            inline_instances = [ReadingTab(self.model, self.admin_site)]
        elif obj.task_type == 'test':
            inline_instances = [QuestionTab(self.model, self.admin_site)]
        elif obj.task_type == 'matching':
            inline_instances = [MatchingColumnTab(self.model, self.admin_site)]

        return inline_instances


# Task type:Test admin
# ----------------------------------------------------------------------------------------------------------------------
# Option Tab
class OptionTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = Option
    fields = ('text', 'is_correct', )
    extra = 0


# Question Admin
@admin.register(Question)
class QuestionAdmin(SummernoteModelAdmin):
    readonly_fields = ('task_link', )
    inlines = (OptionTab, )

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {}</a>', url, obj.task)
        return '—'

    task_link.short_description = 'Сұраққа сілтеме'


# Task type:MatchingColumn admin
# ----------------------------------------------------------------------------------------------------------------------
# MatchingItemTab
class MatchingItemTab(SummernoteModelAdminMixin, admin.TabularInline):
    model = MatchingItem
    extra = 0


# MatchingColumnAdmin
@admin.register(MatchingColumn)
class MatchingColumnAdmin(SummernoteModelAdmin):
    list_display = ('label', 'task', )
    inlines = (MatchingItemTab, )
    readonly_fields = ('task_link',)

    def task_link(self, obj):
        if obj.task:
            url = reverse('admin:core_task_change', args=[obj.task.id])
            return format_html('<a href="{}" class="view-link">🔗 {}</a>', url, obj.task.get_task_type_display())
        return '—'

    task_link.short_description = 'Тапсырмаға сілтеме'