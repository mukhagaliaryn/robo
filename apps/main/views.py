from django.shortcuts import render, redirect

from core.models import Subject


def main_view(request):
    if request.user.is_authenticated:
        return redirect('student:dashboard')

    courses = Subject.objects.filter(is_public=True)

    context = {
        'courses': courses,
    }
    return render(request, 'app/page.html', context)
