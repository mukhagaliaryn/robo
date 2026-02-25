from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from core.models import UserCourse, Course, Module, UserModule, UserLesson, Task, UserTask, Lesson
from core.utils.decorators import role_required


# learner dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def learner_dashboard_view(request):
    if request.user.role == 'tutor':
        return redirect('tutor:dashboard')

    user_courses = (
        UserCourse.objects
        .filter(user=request.user)
        .select_related("course", "course__category", "last_lesson")
        .order_by("-started_at", "-id")[:12]  # соңғылары
    )

    context = {
        "user_courses": user_courses,
    }
    return render(request, "app/learner/page.html", context)


# learner courses list page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('learner')
def learner_courses_list_view(request):
    courses = (
        Course.objects
        .select_related("category")
        .order_by("-id")
    )

    enrolled_map = {
        uc.course_id: uc
        for uc in (
            UserCourse.objects
            .filter(user=request.user)
            .select_related("course")
        )
    }

    context = {
        "courses": courses,
        "enrolled_map": enrolled_map,
    }
    return render(request, "app/learner/courses/page.html", context)


# learner course detail page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('learner')
def learner_course_detail_view(request, course_id: int):
    if request.user.role == "tutor":
        return redirect("tutor:dashboard")

    course = get_object_or_404(
        Course.objects.select_related("category"),
        pk=course_id
    )
    user_course = (
        UserCourse.objects
        .filter(user=request.user, course=course)
        .select_related("last_lesson")
        .first()
    )
    modules = (
        Module.objects
        .filter(course=course)
        .prefetch_related("lessons")
        .order_by("order", "id")
    )
    context = {
        "course": course,
        "user_course": user_course,
        "modules": modules,
    }
    return render(request, "app/learner/courses/detail/page.html", context)


# learner_course_enroll action
# ----------------------------------------------------------------------------------------------------------------------
@transaction.atomic
@role_required('learner')
def learner_course_enroll_view(request, course_id: int):
    if request.method != "POST":
        return redirect("learner:course_detail", course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)

    # ------------------------------------------------------------
    # 0) Контент жоқ болса enroll-ды болдырмау (LESSON және TASK)
    # ------------------------------------------------------------
    has_any_lesson = Lesson.objects.filter(module__course=course).exists()
    has_any_task = Task.objects.filter(lesson__module__course=course).exists()

    if (not has_any_lesson) or (not has_any_task):
        messages.error(
            request,
            "Бұл курсқа әзірге сабақтар/тапсырмалар қосылмаған. Кейінірек қайта көріңіз."
        )
        return redirect("learner:course_detail", course_id=course_id)

    # ------------------------------------------------------------
    # 1) Бұрыннан enrolled болса -> continue (last_lesson болса соған)
    # ------------------------------------------------------------
    uc = (
        UserCourse.objects
        .filter(user=request.user, course=course)
        .select_related("last_lesson")
        .first()
    )

    if uc:
        if uc.last_lesson_id:
            ul = (
                UserLesson.objects
                .filter(user_module__user_course=uc, lesson_id=uc.last_lesson_id)
                .select_related("user_module")
                .first()
            )
            if ul:
                return redirect(
                    "learner:study_lesson",
                    uc_id=uc.id,
                    um_id=ul.user_module_id,
                    ul_id=ul.id
                )

        # last_lesson жоқ/табылмады -> бірінші lesson-ға
        first_lesson = (
            Lesson.objects
            .filter(module__course=course)
            .order_by("module__order", "module__id", "order", "id")
            .select_related("module")
            .first()
        )
        if not first_lesson:
            messages.error(request, "Курста сабақ табылмады.")
            return redirect("learner:course_detail", course_id=course_id)

        um = UserModule.objects.filter(user_course=uc, module=first_lesson.module).first()
        ul = UserLesson.objects.filter(user_module__user_course=uc, lesson=first_lesson).first()
        if um and ul:
            return redirect("learner:study_lesson", uc_id=uc.id, um_id=um.id, ul_id=ul.id)

        # fallback
        return redirect("learner:course_detail", course_id=course_id)

    # ------------------------------------------------------------
    # 2) Жаңа enroll: UserCourse
    # ------------------------------------------------------------
    uc = UserCourse.objects.create(
        user=request.user,
        course=course,
        status=UserCourse.Status.IN_PROGRESS,
    )

    # Курстың модульдері ретімен
    modules = list(Module.objects.filter(course=course).order_by("order", "id"))
    if not modules:
        messages.error(request, "Курста модуль жоқ, сондықтан оқу басталмайды.")
        return redirect("learner:course_detail", course_id=course_id)

    # ------------------------------------------------------------
    # 3) UserModule/UserLesson/UserTask tree құру
    # ------------------------------------------------------------
    first_um = None
    first_ul = None

    for mi, m in enumerate(modules):
        um = UserModule.objects.create(
            user_course=uc,
            module=m,
            status=UserModule.Status.IN_PROGRESS if mi == 0 else UserModule.Status.NOT_STARTED,
        )
        if mi == 0:
            first_um = um

        lessons = list(m.lessons.all().order_by("order", "id"))

        for li, lesson in enumerate(lessons):
            ul = UserLesson.objects.create(
                user_module=um,
                lesson=lesson,
                status=UserLesson.Status.NOT_STARTED,
            )

            # course бойынша ең бірінші lesson -> IN_PROGRESS + last_lesson
            if first_ul is None:
                first_ul = ul
                ul.status = UserLesson.Status.IN_PROGRESS
                ul.save(update_fields=["status"])

                uc.last_lesson = lesson
                uc.save(update_fields=["last_lesson"])

                # (қаласаң) модульдің last_lesson-ы болса:
                if hasattr(um, "last_lesson"):
                    um.last_lesson = lesson
                    um.save(update_fields=["last_lesson"])

            tasks = list(Task.objects.filter(lesson=lesson).order_by("order", "id"))

            # lesson ішінде бірде-бір task жоқ болса — ол lesson үшін ештеңе құрмаймыз
            if tasks:
                UserTask.objects.bulk_create(
                    [
                        UserTask(
                            user_lesson=ul,
                            task=t,
                            status=UserTask.Status.NOT_STARTED,
                        )
                        for t in tasks
                    ]
                )

                # тек бірінші lesson-ның бірінші task-ы IN_PROGRESS
                if first_ul and ul.id == first_ul.id:
                    first_task = tasks[0]
                    UserTask.objects.filter(user_lesson=ul, task=first_task).update(
                        status=UserTask.Status.IN_PROGRESS
                    )

    # Егер lessons бар деп тексердік, бірақ first_ul шықпай қалса — қорғаныс
    if not (first_um and first_ul):
        messages.error(request, "Курсты бастау мүмкін болмады. Контент құрылымын тексеріңіз.")
        return redirect("learner:course_detail", course_id=course_id)

    # ------------------------------------------------------------
    # 4) Бірден оқу бетіне redirect
    # ------------------------------------------------------------
    return redirect("learner:study_lesson", uc_id=uc.id, um_id=first_um.id, ul_id=first_ul.id)
