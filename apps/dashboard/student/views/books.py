from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from core.models import Book, UserBook
from core.utils.decorators import role_required


# library page
# ----------------------------------------------------------------------------------------------------------------------
@role_required("student")
def library_view(request):
    q = (request.GET.get("q") or "").strip()

    books = Book.objects.filter(is_active=True)
    if q:
        books = books.filter(title__icontains=q)

    user_books = UserBook.objects.filter(user=request.user, is_saved=True).select_related("book")
    ub_map = {ub.book_id: ub for ub in user_books}
    items = []
    for b in books.order_by("order", "-id"):
        items.append({
            "book": b,
            "user_book": ub_map.get(b.id),
        })

    context = {
        "items": items,
        "q": q,
    }
    return render(request, "app/dashboard/student/library/page.html", context)


@role_required("student")
def book_detail_view(request, book_id: int):
    book = get_object_or_404(Book, pk=book_id, is_active=True)
    user_book = UserBook.objects.filter(user=request.user, book=book, is_saved=True).first()
    context = {
        "book": book,
        "user_book": user_book,
    }
    return render(request, "app/dashboard/student/library/detail/page.html", context)


@role_required("student")
@require_POST
def user_book_toggle_view(request, book_id: int):
    book = get_object_or_404(Book, pk=book_id, is_active=True)
    ub, created = UserBook.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={"is_saved": True}
    )
    if not created:
        ub.is_saved = not ub.is_saved
        ub.save(update_fields=["is_saved", "updated_at"])

    if ub.is_saved:
        messages.success(request, "Кітап кітапханаңызға сақталды ✅")
        return redirect("student:user_book_detail", user_book_id=ub.id)

    messages.info(request, "Кітап кітапханаңыздан алынды")
    return redirect("student:library")


@login_required
@role_required("student")
def user_book_detail_view(request, user_book_id: int):
    ub = get_object_or_404(
        UserBook.objects.select_related("book"),
        pk=user_book_id,
        user=request.user,
        is_saved=True
    )
    context = {
        "user_book": ub,
        "book": ub.book,
    }
    return render(request, "app/dashboard/student/user/library/page.html", context)


@role_required("student")
def simulator_view(request):
    return render(request, "app/dashboard/student/simulator/page.html")