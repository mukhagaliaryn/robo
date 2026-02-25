from django.urls import path
from .views import account, dashboard, course

app_name = 'learner'

urlpatterns = [
    # account urls...
    path('account/me/', account.account_view, name='account'),
    path('account/settings/', account.settings_view, name='settings'),

    path('', dashboard.learner_dashboard_view, name='dashboard'),
    path("courses/", dashboard.learner_courses_list_view, name="courses_list"),
    path("courses/<int:course_id>/", dashboard.learner_course_detail_view, name="course_detail"),
    path("courses/<int:course_id>/enroll/", dashboard.learner_course_enroll_view, name="course_enroll"),

    path(
        "study/ucourse/<int:uc_id>/umodule/<int:um_id>/ulesson/<int:ul_id>/",
        course.learner_study_lesson_view,
        name="study_lesson",
    ),
]
