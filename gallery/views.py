from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from photo.models import Photo

app_name = 'gallery'

def browse(request):
    """
    View for browsing images of other users
    """
    photos = Photo.objects.filter(is_private=False)
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })

@login_required
def browse_my(request):
    """
    View for browsing photos of the user
    """
    photos = Photo.objects.filter(owner=request.user.id)
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })

@login_required
def browse_reviews(request):
    """
    View for browsing to be reviewed photos
    """
    photos = Photo.objects.filter(is_private=False, review_status=1)
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })