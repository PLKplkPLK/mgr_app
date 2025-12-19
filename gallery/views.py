from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator

from photo.models import Photo
from animals import animals_pl_map

app_name = 'gallery'
animals_pl_map = {k: v for k, v in sorted(animals_pl_map.items(), key=lambda item: item[1])}

def add_display_name_to_photos(page_obj: Page) -> Page:
    for photo in page_obj:
        animal_name = photo.custom_name if photo.custom_name else photo.prediction
        photo.display_name = animals_pl_map.get(animal_name)
        print(photo.display_name)
    return page_obj

def browse(request):
    """
    View for browsing images of other users
    """
    photos = Photo.objects.filter(is_private=False).order_by('-upload_time')
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    page_obj = add_display_name_to_photos(page_obj)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })

@login_required
def browse_my(request):
    """
    View for browsing photos of the user
    """
    photos = Photo.objects.filter(owner=request.user.id).order_by('-upload_time')
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    page_obj = add_display_name_to_photos(page_obj)
    
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
    page_obj = add_display_name_to_photos(page_obj)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })

def browse_popular(request):
    """
    View for browsing images of other users
    """
    photos = Photo.objects.filter(is_private=False).order_by('-n_times_seen')
    paginator = Paginator(photos, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    page_obj = add_display_name_to_photos(page_obj)
    
    return render(request, "gallery/browse.html", {
        "page_obj": page_obj
    })