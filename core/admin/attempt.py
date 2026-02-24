from django.contrib import admin
from core.admin._mixins import LinkedAdminMixin
from core.models.attempt import (
    UserCourse,
    UserModule,
    UserLesson,
    UserTask,
    TaskAttempt,
    VideoProgress,
    QuestionAttempt,
    MatchingAttempt,
)


# ----------------------------------------------------------------------------------------------------------------------
# Inlines (иерархия бойынша)
# ----------------------------------------------------------------------------------------------------------------------
class UserModuleInline(admin.TabularInline, LinkedAdminMixin):
    model = UserModule
    extra = 0
    show_change_link = False
    fields = ('module', 'status', 'progress_percent', 'percentage', 'score', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('module_id',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class UserLessonInline(admin.TabularInline, LinkedAdminMixin):
    model = UserLesson
    extra = 0
    show_change_link = False
    fields = ('lesson', 'status', 'progress_percent', 'percentage', 'score', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('lesson_id',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class UserTaskInline(admin.TabularInline, LinkedAdminMixin):
    model = UserTask
    extra = 0
    show_change_link = False
    fields = ('task', 'status', 'attempts_count', 'score', 'submitted_at', 'graded_at', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('task_id',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class VideoProgressInline(admin.TabularInline, LinkedAdminMixin):
    model = VideoProgress
    extra = 0
    show_change_link = False
    fields = ('watched_sec', 'last_position_sec', 'is_completed', 'detail_link')
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class TaskAttemptInline(admin.TabularInline, LinkedAdminMixin):
    model = TaskAttempt
    extra = 0
    show_change_link = False
    fields = ('attempt_no', 'status', 'score', 'started_at', 'submitted_at', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('attempt_no',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class QuestionAttemptInline(admin.TabularInline, LinkedAdminMixin):
    model = QuestionAttempt
    extra = 0
    show_change_link = False
    fields = ('question', 'is_correct', 'score', 'answered_at', 'detail_link')
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class MatchingAttemptInline(admin.TabularInline, LinkedAdminMixin):
    model = MatchingAttempt
    extra = 0
    show_change_link = False
    fields = ('is_correct', 'score', 'detail_link')
    readonly_fields = ('detail_link',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


# ----------------------------------------------------------------------------------------------------------------------
# Admins
# ----------------------------------------------------------------------------------------------------------------------
@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'status', 'progress_percent', 'percentage', 'score', 'started_at', 'completed_at', 'course_link')
    list_filter = ('status', 'course')
    search_fields = ('user__username', 'user__email', 'course__title')
    ordering = ('-id',)
    readonly_fields = ('course_link',)
    inlines = (UserModuleInline,)

    def course_link(self, obj):
        return self.parent_link(obj, parent_field_name='course')

    course_link.short_description = 'Курс'


@admin.register(UserModule)
class UserModuleAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user_course', 'status', 'progress_percent', 'percentage', 'score', 'user_course_link')
    list_filter = ('status', 'module__course')
    search_fields = ('user_course__user__username', 'user_course__user__email', 'module__title', 'module__course__title')
    ordering = ('-id',)
    inlines = (UserLessonInline,)

    def user_course_link(self, obj):
        return self.parent_link(obj, parent_field_name='user_course')

    user_course_link.short_description = 'Қолданушы курсы'


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'lesson_link', 'module_link', 'course_link', 'status', 'progress_percent', 'percentage', 'score', 'self_link')
    list_filter = ('status', 'lesson__module__course')
    search_fields = (
        'user_module__user_course__user__username',
        'user_module__user_course__user__email',
        'lesson__title',
        'lesson__module__title',
        'lesson__module__course__title',
    )
    ordering = ('-id',)
    inlines = (UserTaskInline,)

    def user(self, obj):
        return obj.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def lesson_link(self, obj):
        return self.parent_link(obj, parent_field_name='lesson')

    lesson_link.short_description = 'Сабақ'

    def module_link(self, obj):
        return self.parent_link(obj.lesson, parent_field_name='module')

    module_link.short_description = 'Модуль'

    def course_link(self, obj):
        return self.parent_link(obj.lesson.module, parent_field_name='course')

    course_link.short_description = 'Курс'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Сабақ прогресі'


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'task_link', 'task_type', 'status', 'attempts_count', 'score', 'submitted_at', 'graded_at', 'lesson_link', 'self_link')
    list_filter = ('status', 'task__task_type', 'task__lesson__module__course')
    search_fields = (
        'user_lesson__user_module__user_course__user__username',
        'user_lesson__user_module__user_course__user__email',
        'task__title',
        'task__lesson__title',
    )
    ordering = ('-id',)
    inlines = (VideoProgressInline, TaskAttemptInline)

    def user(self, obj):
        return obj.user_lesson.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def task_type(self, obj):
        return obj.task.task_type

    task_type.short_description = 'Түрі'

    def task_link(self, obj):
        return self.parent_link(obj, parent_field_name='task')

    task_link.short_description = 'Тапсырма'

    def lesson_link(self, obj):
        return self.parent_link(obj.user_lesson, parent_field_name='lesson')

    lesson_link.short_description = 'Сабақ'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Қолданушы тапсырмасы'


@admin.register(TaskAttempt)
class TaskAttemptAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'user_task_link', 'attempt_no', 'status', 'score', 'started_at', 'submitted_at', 'self_link')
    list_filter = ('status', 'user_task__task__task_type')
    search_fields = (
        'user_task__user_lesson__user_module__user_course__user__username',
        'user_task__user_lesson__user_module__user_course__user__email',
        'user_task__task__title',
    )
    ordering = ('-id',)
    inlines = (QuestionAttemptInline, MatchingAttemptInline)

    def user(self, obj):
        return obj.user_task.user_lesson.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def user_task_link(self, obj):
        return self.parent_link(obj, parent_field_name='user_task')

    user_task_link.short_description = 'Қолданушы тапсырмасы'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Әрекет'


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'user_task_link', 'watched_sec', 'last_position_sec', 'is_completed', 'self_link')
    list_filter = ('is_completed',)
    search_fields = (
        'user_task__user_lesson__user_module__user_course__user__username',
        'user_task__user_lesson__user_module__user_course__user__email',
        'user_task__task__title',
    )
    ordering = ('-id',)

    def user(self, obj):
        return obj.user_task.user_lesson.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def user_task_link(self, obj):
        return self.parent_link(obj, parent_field_name='user_task')

    user_task_link.short_description = 'Қолданушы тапсырмасы'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Видео прогресс'


@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'attempt_link', 'question', 'is_correct', 'score', 'answered_at', 'self_link')
    list_filter = ('is_correct',)
    search_fields = (
        'attempt__user_task__user_lesson__user_module__user_course__user__username',
        'attempt__user_task__task__title',
        'question__text',
    )
    ordering = ('-id',)

    def user(self, obj):
        return obj.attempt.user_task.user_lesson.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def attempt_link(self, obj):
        return self.parent_link(obj, parent_field_name='attempt')

    attempt_link.short_description = 'Әрекет'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Нәтиже'


@admin.register(MatchingAttempt)
class MatchingAttemptAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('user', 'attempt_link', 'is_correct', 'score', 'self_link')
    list_filter = ('is_correct',)
    search_fields = (
        'attempt__user_task__user_lesson__user_module__user_course__user__username',
        'attempt__user_task__task__title',
    )
    ordering = ('-id',)

    def user(self, obj):
        return obj.attempt.user_task.user_lesson.user_module.user_course.user

    user.short_description = 'Қолданушы'

    def attempt_link(self, obj):
        return self.parent_link(obj, parent_field_name='attempt')

    attempt_link.short_description = 'Әрекет'

    def self_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    self_link.short_description = 'Matching нәтиже'