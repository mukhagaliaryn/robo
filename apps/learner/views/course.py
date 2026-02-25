from django.shortcuts import get_object_or_404, redirect, render
from core.models.attempt import UserCourse, UserModule, UserLesson, UserTask
from core.utils.decorators import role_required


@role_required("learner")
def learner_study_lesson_view(request, uc_id: int, um_id: int, ul_id: int):
    user_course = get_object_or_404(
        UserCourse.objects.select_related("course", "course__category", "last_lesson"),
        pk=uc_id,
        user=request.user,
    )

    user_module = get_object_or_404(
        UserModule.objects.select_related("module"),
        pk=um_id,
        user_course=user_course,
    )

    user_lesson = get_object_or_404(
        UserLesson.objects.select_related("lesson", "lesson__module"),
        pk=ul_id,
        user_module=user_module,
    )
    if user_lesson.lesson.module_id != user_module.module_id:
        return redirect("learner:course_detail", course_id=user_course.course_id)

    user_tasks = (
        UserTask.objects
        .filter(user_lesson=user_lesson)
        .select_related("task")
        .order_by("task__order", "task__id")
    )

    context = {
        "user_course": user_course,
        "user_module": user_module,
        "user_lesson": user_lesson,
        "user_tasks": user_tasks,
    }
    return render(request, "app/learner/study/lesson/page.html", context)