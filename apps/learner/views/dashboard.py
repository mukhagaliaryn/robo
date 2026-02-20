from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# learner dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def learner_dashboard_view(request):
    if request.user.role == 'tutor':
        return redirect('tutor:dashboard')

    context = {}
    return render(request, 'app/learner/page.html', context)
