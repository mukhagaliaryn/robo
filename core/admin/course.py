from django.contrib import admin
from core.admin._mixins import LinkedAdminMixin
from core.models.course import Category, Course, Module, Lesson


# -----------------------------
# Inlines
# -----------------------------

class CourseInline(admin.TabularInline, LinkedAdminMixin):
    model = Course
    extra = 0
    show_change_link = False
    fields = ('order', 'title', 'slug', 'is_published', 'detail_link')
    readonly_fields = ('detail_link',)
    ordering = ('order',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class ModuleInline(admin.TabularInline, LinkedAdminMixin):
    model = Module
    extra = 0
    show_change_link = False
    fields = ('order', 'title', 'is_published', 'detail_link')
    readonly_fields = ('detail_link', )
    ordering = ('order',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


class LessonInline(admin.TabularInline, LinkedAdminMixin):
    model = Lesson
    extra = 0
    show_change_link = False
    fields = ('order', 'title', 'duration_sec', 'is_published', 'detail_link')
    readonly_fields = ('detail_link', )
    ordering = ('order',)

    def detail_link(self, obj):
        return super().admin_link(obj, label='Толығырақ')

    detail_link.short_description = 'Сілтеме'


# -----------------------------
# Admins
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('title', 'slug', 'order', 'is_published', 'courses_link')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    ordering = ('order', 'title')
    inlines = (CourseInline,)

    def courses_link(self, obj):
        return self.admin_link(obj, label='Ашу')

    courses_link.short_description = 'Категория'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('title', 'level', 'order', 'is_published', 'category_link')
    list_filter = ('is_published', 'level', 'category')
    search_fields = ('title', 'slug')
    ordering = ('order', 'title')
    inlines = (ModuleInline,)
    readonly_fields = ('category_link', )

    def category_link(self, obj):
        return self.parent_link(obj, parent_field_name='category')

    category_link.short_description = 'Категория'


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('title', 'order', 'is_published', 'course_link')
    list_filter = ('is_published', 'course')
    search_fields = ('title',)
    ordering = ('course_id', 'order')
    inlines = (LessonInline,)
    readonly_fields = ('course_link', )

    def course_link(self, obj):
        return self.parent_link(obj, parent_field_name='course')

    course_link.short_description = 'Курс'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin, LinkedAdminMixin):
    list_display = ('title', 'order', 'duration_sec', 'is_published', 'module_link')
    list_filter = ('is_published', 'module__course')
    search_fields = ('title',)
    ordering = ('module_id', 'order')
    readonly_fields = ('module_link', )

    def module_link(self, obj):
        return self.parent_link(obj, parent_field_name='module')

    module_link.short_description = 'Модуль'
