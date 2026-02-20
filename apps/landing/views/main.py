from django.shortcuts import render


# Landing page
# ----------------------------------------------------------------------------------------------------------------------
def landing_view(request):
    context = {}
    return render(request, 'app/page.html', context)
