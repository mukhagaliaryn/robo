from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.teacher_dashboard_view, name='dashboard'),

    path("courses/", views.teacher_courses_view, name="courses"),
    path("courses/<int:pk>/", views.teacher_course_detail_view, name="course_detail"),

    path("books/", views.teacher_books_view, name="books"),
    path("books/<int:pk>/", views.teacher_book_detail_view, name="book_detail"),

    path("user-subject/<int:pk>/", views.user_subject_detail_view, name="user_subject_detail"),
    path(
        "user-subject/<int:user_subject_id>/lesson/<int:user_lesson_id>/modal/",
        views.user_lesson_modal_view,
        name="user_lesson_modal",
    ),

    path("user-subject/<int:pk>/", views.user_subject_detail_view, name="user_subject_detail"),
    path(
        "user-subject/<int:user_subject_id>/lesson/<int:user_lesson_id>/modal/",
        views.user_lesson_modal_view,
        name="user_lesson_modal",
    ),
]