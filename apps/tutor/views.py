from django.shortcuts import render
from core.utils.decorators import role_required


# tutor dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('manager')
def tutor_dashboard_view(request):
    return render(request, 'app/tutor/dashboard.html')
