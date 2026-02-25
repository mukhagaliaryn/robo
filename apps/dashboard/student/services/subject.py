from django.contrib import messages
from core.models import Option


# user_lesson_task_view
# ----------------------------------------------------------------------------------------------------------------------
# get_related_data
def get_related_data(user_task):
    task_type = user_task.task.task_type
    data = {}

    if task_type == 'video':
        data['user_videos'] = user_task.user_videos.all()

    if task_type == 'reading':
        data["reading"] = getattr(user_task.task, "reading", None)
        data["user_reading"] = getattr(user_task, "user_reading", None)

    elif task_type == 'test':
        data['user_answers'] = user_task.user_options.select_related('question').prefetch_related('options').order_by('question__order')

    elif task_type == 'matching':
        data['user_matchings'] = user_task.matching_answers.all()

    return data


# handle_post_request
def handle_post_request(request, user_task):
    handlers = {
        'video': handle_video,
        'reading': handle_reading,
        'test': handle_test,
        'matching': handle_matching,
    }
    handler = handlers.get(user_task.task.task_type)
    if handler:
        return handler(request, user_task)


# ---------------------- VIDEO ----------------------
def handle_video(request, user_task):
    videos = user_task.user_videos.all()
    for uv in videos:
        uv.watched_seconds = int(request.POST.get(f'watched_{uv.id}', 0))
        uv.is_completed = True
        uv.save()

    if all(uv.is_completed for uv in videos):
        user_task.is_completed = True
        user_task.rating = user_task.task.rating
        user_task.save()
        messages.success(request, 'Видеосабақ аяқталды')


# ---------------------- READING ----------------------
def handle_reading(request, user_task):
    ur = getattr(user_task, "user_reading", None)
    if ur is None:
        messages.error(request, "Reading прогресі табылмады.")
        return

    ur.is_read = True
    ur.read_seconds = int(request.POST.get("read_seconds", 0) or 0)
    ur.save(update_fields=["is_read", "read_seconds"])

    user_task.is_completed = True
    user_task.rating = user_task.task.rating
    user_task.save(update_fields=["is_completed", "rating"])

    messages.success(request, "Оқу тапсырмасы аяқталды")


# ---------------------- TEST ----------------------
def handle_test(request, user_task):
    questions = [ua.question for ua in user_task.user_options.all()]
    total_questions = len(questions)
    total_score = 0

    for user_answer in user_task.user_options.select_related('question').prefetch_related('question__options'):
        question = user_answer.question
        selected_ids = request.POST.getlist(f'question_{question.id}')
        selected_ids = list(map(int, selected_ids)) if selected_ids else []

        valid_ids = set(question.options.values_list('id', flat=True))
        selected_ids = [opt_id for opt_id in selected_ids if opt_id in valid_ids]

        selected_options = Option.objects.filter(id__in=selected_ids)
        user_answer.options.set(selected_options)

        correct_ids = set(question.options.filter(is_correct=True).values_list('id', flat=True))
        selected_set = set(selected_ids)

        # -------------------------
        # Бағалау логикасы
        # -------------------------
        if question.question_type == 'simple':
            if len(selected_set) == 1 and selected_set.pop() in correct_ids:
                total_score += 1

        elif question.question_type == 'multiple':
            if correct_ids:
                correct_selected = len(selected_set & correct_ids)
                wrong_selected = len(selected_set - correct_ids)

                partial_score = (correct_selected - wrong_selected) / len(correct_ids)
                if partial_score < 0:
                    partial_score = 0

                total_score += partial_score
            else:
                total_score += 0

    full_rating = user_task.task.rating or 1
    if total_questions == 0:
        score = 0
        messages.error(request, 'Тестте сұрақтар жоқ.')
    else:
        ratio = total_score / total_questions
        score = round(full_rating * ratio)

        if ratio == 1:
            messages.success(request, 'Барлық сұраққа дұрыс жауап бердіңіз!')
        elif ratio == 0:
            messages.error(request, 'Барлық жауап қате.')
        else:
            messages.info(
                request,
                f'Ұпай {score} қойылды ({round(ratio*100)}% дұрыс жауап).'
            )

    user_task.rating = score
    user_task.is_completed = True
    user_task.save()


# ---------------------- MATCHING ----------------------
def handle_matching(request, user_task):
    for answer in user_task.matching_answers.all():
        selected_column_id = request.POST.get(f'column_{answer.item.id}')
        if selected_column_id:
            answer.selected_column_id = int(selected_column_id)
            answer.check_answer()

    answers = user_task.matching_answers.all()
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    wrong = total - correct

    full_rating = user_task.task.rating
    score = 0

    if wrong == 0:
        score = full_rating
    elif wrong == 1:
        score = full_rating / 2 if full_rating > 1 else 0
    elif wrong > total / 2:
        score = 0
    else:
        score = full_rating / 2 if full_rating > 1 else 0

    user_task.rating = round(score, 2)
    user_task.is_completed = True
    user_task.save()
    messages.success(request, 'Сәйкестендіру тапсырмасы аяқталды')
