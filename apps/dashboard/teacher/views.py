from django.db.models import Avg, Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from core.models import Subject, UserSubject, UserChapter, UserLesson, User, Book, UserTask, Task, UserMatchingAnswer, \
    UserAnswer, UserReading, UserVideo, Chapter, Lesson
from core.utils.decorators import role_required


def _safe_round(value, digits=0):
    if value is None:
        return 0
    try:
        return round(float(value), digits)
    except Exception:
        return 0


@role_required("teacher")
def teacher_dashboard_view(request):
    # ---------------------------
    # 1) Жалпы көрсеткіштер (cards)
    # ---------------------------
    learners_total = User.objects.filter(user_type="student").count()
    enrolled_learners = (
        User.objects.filter(user_type="student", user_subjects__isnull=False)
        .distinct()
        .count()
    )
    courses_count = Subject.objects.count()
    books_count = Book.objects.count()

    # ---------------------------
    # 2) Жалпы орташа мәндер (барлық user_courses бойынша)
    # ---------------------------
    subject_avg = UserSubject.objects.aggregate(
        avg_rating=Avg("rating"),
        avg_percentage=Avg("percentage"),
    )
    chapter_avg = UserChapter.objects.aggregate(
        avg_rating=Avg("rating"),
        avg_percentage=Avg("percentage"),
    )
    lesson_avg = UserLesson.objects.aggregate(
        avg_rating=Avg("rating"),
        avg_percentage=Avg("percentage"),
    )

    overall = {
        "subject_avg_rating": _safe_round(subject_avg["avg_rating"], 0),
        "subject_avg_percentage": _safe_round(subject_avg["avg_percentage"], 2),
        "chapter_avg_rating": _safe_round(chapter_avg["avg_rating"], 0),
        "chapter_avg_percentage": _safe_round(chapter_avg["avg_percentage"], 2),
        "lesson_avg_rating": _safe_round(lesson_avg["avg_rating"], 0),
        "lesson_avg_percentage": _safe_round(lesson_avg["avg_percentage"], 2),
    }

    # ---------------------------
    # 3) Table: барлық қолданушы курстары + filter/search
    # ---------------------------
    q = (request.GET.get("q") or "").strip()
    subject_id = (request.GET.get("subject") or "").strip()
    user_id = (request.GET.get("user") or "").strip()

    user_courses_qs = (
        UserSubject.objects.select_related("user", "subject")
        .all()
        .order_by("-created_at", "-id")
    )

    if subject_id:
        user_courses_qs = user_courses_qs.filter(subject_id=subject_id)

    if user_id:
        user_courses_qs = user_courses_qs.filter(user_id=user_id)

    if q:
        user_courses_qs = user_courses_qs.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__email__icontains=q)
            | Q(subject__name__icontains=q)
        )

    # Dropdown-тар үшін деректер
    subjects = Subject.objects.all().order_by("name")
    learners = (
        User.objects.filter(user_type="student", user_subjects__isnull=False)
        .distinct()
        .order_by("first_name", "last_name", "username")
    )

    context = {
        "generics": {
            "learners_total": learners_total,
            "enrolled_learners": enrolled_learners,
            "courses_count": courses_count,
            "books_count": books_count,
        },
        "overall": overall,
        "user_courses": user_courses_qs,
        "subjects": subjects,
        "learners": learners,
        "filters": {
            "q": q,
            "subject": subject_id,
            "user": user_id,
        },
    }
    return render(request, "app/dashboard/teacher/page.html", context)


# user_subject_detail page
# ----------------------------------------------------------------------------------------------------------------------
@role_required("teacher")
def user_subject_detail_view(request, pk: int):
    us = get_object_or_404(
        UserSubject.objects.select_related("user", "subject"),
        pk=pk,
    )
    chapters = (
        UserChapter.objects
        .filter(user_subject=us)
        .select_related("chapter")
        .order_by("id")
    )
    lessons = (
        UserLesson.objects
        .filter(user_subject=us)
        .select_related("lesson")
        .order_by("id")
    )

    chapter_to_user_chapter = {uc.chapter_id: uc.id for uc in chapters}
    lessons_by_chapter = {}

    for ul in lessons:
        uc_id = getattr(ul, "user_chapter_id", None)
        if not uc_id:
            ch_id = getattr(ul, "chapter_id", None)
            if ch_id:
                uc_id = chapter_to_user_chapter.get(ch_id)

        if not uc_id and getattr(ul, "lesson", None):
            ch_id = getattr(ul.lesson, "chapter_id", None)
            if ch_id:
                uc_id = chapter_to_user_chapter.get(ch_id)

        if not uc_id:
            continue

        lessons_by_chapter.setdefault(uc_id, []).append(ul)

    ch_avg = UserChapter.objects.filter(user_subject=us).aggregate(
        avg_rating=Avg("rating"),
        avg_percentage=Avg("percentage"),
    )
    ls_avg = UserLesson.objects.filter(user_subject=us).aggregate(
        avg_rating=Avg("rating"),
        avg_percentage=Avg("percentage"),
    )
    overall = {
        "course_rating": _safe_round(getattr(us, "rating", 0), 0),
        "course_percentage": _safe_round(getattr(us, "percentage", 0), 0),

        "chapter_avg_rating": _safe_round(ch_avg["avg_rating"], 0),
        "chapter_avg_percentage": _safe_round(ch_avg["avg_percentage"], 0),

        "lesson_avg_rating": _safe_round(ls_avg["avg_rating"], 0),
        "lesson_avg_percentage": _safe_round(ls_avg["avg_percentage"], 0),
    }

    return render(
        request,
        "app/dashboard/teacher/user_subject/page.html",
        {
            "us": us,
            "overall": overall,
            "chapters": chapters,
            "lessons_by_chapter": lessons_by_chapter,
        },
    )


@role_required("teacher")
def user_lesson_modal_view(request, user_subject_id: int, user_lesson_id: int):
    us = get_object_or_404(
        UserSubject.objects.select_related("user", "subject"),
        pk=user_subject_id
    )
    ul = get_object_or_404(
        UserLesson.objects.select_related("lesson", "user"),
        pk=user_lesson_id,
        user_subject=us,
    )

    base_tasks = Task.objects.filter(lesson=ul.lesson).order_by("order", "id")

    user_tasks = (
        UserTask.objects
        .filter(user_lesson=ul)
        .select_related("task")
    )
    user_task_map = {ut.task_id: ut for ut in user_tasks}
    user_task_ids = [ut.id for ut in user_tasks]

    # -----------------------
    # Preload user content
    # -----------------------
    videos_by_ut = {}
    for uv in (
        UserVideo.objects
        .filter(user_task_id__in=user_task_ids)
        .select_related("video")
        .order_by("id")
    ):
        videos_by_ut.setdefault(uv.user_task_id, []).append(uv)

    reading_by_ut = {
        ur.user_task_id: ur
        for ur in (
            UserReading.objects
            .filter(user_task_id__in=user_task_ids)
            .select_related("reading")
        )
    }

    answers_by_ut = {}
    for a in (
        UserAnswer.objects
        .filter(user_task_id__in=user_task_ids)
        .select_related("question")
        .prefetch_related("options", "question__options")
        .order_by("question__order", "id")
    ):
        selected_ids = set(a.options.values_list("id", flat=True))
        option_rows = []
        for opt in a.question.options.all():
            option_rows.append({
                "id": opt.id,
                "text": opt.text,
                "is_correct": bool(opt.is_correct),
                "is_selected": opt.id in selected_ids,
            })

        answers_by_ut.setdefault(a.user_task_id, []).append({
            "question_text": a.question.text,
            "question_type": a.question.question_type,
            "options": option_rows,
        })

    matching_by_ut = {}
    for ma in (
        UserMatchingAnswer.objects
        .filter(user_task_id__in=user_task_ids)
        .select_related("item", "selected_column", "item__correct_column")
        .order_by("id")
    ):
        matching_by_ut.setdefault(ma.user_task_id, []).append(ma)

    # -----------------------
    # Build UI rows
    # -----------------------
    task_rows = []
    for t in base_tasks:
        ut = user_task_map.get(t.id)

        percent = 0
        if ut:
            if t.rating and t.rating > 0:
                percent = round((ut.rating / t.rating) * 100)
            else:
                percent = 100 if ut.is_completed else 0

        extra = {}
        if ut:
            extra["videos"] = videos_by_ut.get(ut.id, [])
            extra["reading"] = reading_by_ut.get(ut.id)
            extra["answers"] = answers_by_ut.get(ut.id, [])
            extra["matching"] = matching_by_ut.get(ut.id, [])

        task_rows.append({
            "task": t,
            "user_task": ut,
            "percent": percent,
            "extra": extra,
        })

    return render(
        request,
        "app/dashboard/teacher/user_subject/partials/_lesson_modal.html",
        {"us": us, "ul": ul, "task_rows": task_rows},
    )


# ----------------------------------------------------------------------------------------------------------------------
def admin_change_url(obj) -> str:
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.pk],
    )


@role_required("teacher")
def teacher_courses_view(request):
    courses = Subject.objects.all().order_by("name", "id")
    course_cards = []
    for s in courses:
        course_cards.append({
            "obj": s,
            "admin_change_url": admin_change_url(s),
        })
    return render(
        request,
        "app/dashboard/teacher/courses/page.html",
        {"course_cards": course_cards},
    )

@role_required("teacher")
def teacher_books_view(request):
    books = Book.objects.all().order_by("title", "id")
    book_cards = []
    for b in books:
        book_cards.append({
            "obj": b,
            "admin_change_url": admin_change_url(b),
        })

    return render(
        request,
        "app/dashboard/teacher/books/page.html",
        {"book_cards": book_cards},
    )
