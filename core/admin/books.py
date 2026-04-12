from django.contrib import admin
from core.forms.books import BookAdminForm
from core.models import Project
from core.models.books import Book, UserBook, Simulator


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("order", "-id")
    form = BookAdminForm


@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "is_saved", "progress", "last_page", "updated_at")
    list_filter = ("is_saved",)
    search_fields = ("user__username", "user__email", "book__title")


@admin.register(Simulator)
class SimulatorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "url", "order")
    ordering = ("order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "url", "order")
    ordering = ("order",)
