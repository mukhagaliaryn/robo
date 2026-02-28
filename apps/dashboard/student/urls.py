from django.urls import path
from .views import home, subject, books

app_name = 'student'

urlpatterns = [
    path('', home.student_view, name='dashboard'),
    path('courses/', home.courses_view, name='courses'),
    path('course/<pk>/', home.subject_detail_view, name='subject_detail'),
    path('course/enroll/<int:subject_id>/', home.enroll_user_to_subject, name='enroll_subject'),

    path('user/course/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/', subject.user_lesson_view, name='user_lesson'),
    path(
        'user/course/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/start/',
        subject.lesson_start_handler,
        name='lesson_start'
    ),
    path(
        'user/course/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/task/<task_id>/',
        subject.user_lesson_task_view,
        name='user_lesson_task'
    ),
    path(
        'user/course/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/finish/',
        subject.lesson_finish_handler,
        name='lesson_finish_handler'
    ),
    path(
        'user/course/<subject_id>/chapter/<chapter_id>/lesson/<lesson_id>/feedback/',
        subject.feedback_handler,
        name='feedback_handler'
    ),

    path("library/", books.library_view, name="library"),
    path("library/<int:book_id>/", books.book_detail_view, name="book_detail"),
    path("library/user-book/<int:user_book_id>/", books.user_book_detail_view, name="user_book_detail"),
    path("library/<int:book_id>/toggle/", books.user_book_toggle_view, name="book_toggle"),

    path('simulator/<slug>/', books.simulator_view, name='simulator'),
]
