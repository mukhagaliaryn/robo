from django.shortcuts import render, redirect

from core.models import Subject, Book


def main_view(request):
    if request.user.is_authenticated:
        return redirect('student:dashboard')

    courses = Subject.objects.filter(is_public=True)
    books = Book.objects.filter(is_active=True)
    context = {
        'courses': courses,
        'books': books,
    }
    return render(request, 'app/page.html', context)
