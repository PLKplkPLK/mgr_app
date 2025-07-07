from django.shortcuts import render#, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from photo.models import Photo

app_name = 'gallery'

def browse(request):
    """
    View for browsing images of other users
    """
    photos = Photo.objects.filter(is_private=False)[:10]
    
    return render(request, "gallery/browse.html", {
        "photos": photos
    })

@login_required
def browse_my(request):
    """
    View for browsing photos of the user
    """
    photos = Photo.objects.filter(owner=request.user.id)

    return render(request, "gallery/browse.html", {
        "photos": photos
    })

@login_required
def browse_reviews(request):
    """
    View for browsing to be reviewed photos
    """
    photos = Photo.objects.filter(is_private=False, review_status=1)
    
    return render(request, "gallery/browse.html", {
        "photos": photos
    })