import logging
import os
from io import BytesIO

import requests
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile

from .models import Photo, Review
from .forms import SendPhotoForm, PostReviewForm
from .helpers import add_noise_to_localization


logger = logging.getLogger(__name__)

map_animals_pl = {  # Frontend side
    'red fox': 'Lis rudy',
    'brown bear': 'Niedźwiedź brunatny',
    'grey wolf': 'Wilk szary',
    'domestic cat': 'Kot domowy',
    'common fallow deer': 'Daniel zwyczajny',
    'blank': 'Brak zwierzęcia',
    'european roe deer': 'Sarna europejska',
    'red deer': 'Jeleń szlachetny',
    'pine marten': 'Kuna leśna',
    'domestic dog': 'Pies domowy',
    'martes species': 'Kuna (rodzaj)',
    'american bison': 'Żubr europejski',
    'northern raccoon': 'Szop pracz',
    'eurasian red squirrel': 'Wiewiórka pospolita',
    'wild boar': 'Dzik euroazjatycki',
    'moose': 'Łoś euroazjatycki',
    'european hare': 'Zając szarak',
    'eurasian badger': 'Borsuk europejski',
}


def convert_image_to_webp(uploaded_file) -> ContentFile:
    img = Image.open(uploaded_file)
    img = img.convert("RGB")  # Ensures compatibility (e.g. for PNGs with alpha)

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=85)

    webp_filename = f"{os.path.splitext(uploaded_file.name)[0]}.webp"

    return ContentFile(buffer.getvalue(), name=webp_filename)


def upload(request):
    """
    A site to upload and classify a photo.
    """
    if request.method == "POST":
        form = SendPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            # convert to webp
            image_webp = convert_image_to_webp(form.cleaned_data['image_file'])
            # save image (disk and database)
            image_object = Photo.objects.create(
                is_private = form.cleaned_data['is_private'],
                image = image_webp,
                owner = request.user if request.user.is_authenticated else None
            )

            # The classification is done on a separate server via API
            try:
                url = "http://localhost:8006/predict"

                image_webp.seek(0)
                files = {"image": (image_webp.name, image_webp.read(), "image/webp")}

                # the request
                response = requests.post(url, files=files, timeout=30)
                if not response.ok:
                    raise Exception(f"Error, status: {response.status_code}")
                response = response.json()

                if response.get('category') != 1:
                    image_object.prediction = 'empty'
                else:
                    detected_animal = response.get('detected_animal')
                    bbox = response.get('bbox')
                    confidence = response.get('confidence')
                    image_object.prediction  = detected_animal
                    image_object.prediction_probability = confidence
                    image_object.bbox = bbox
                image_object.save()
            except Exception as e:
                photo_path = image_object.image.path
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                image_object.delete()
                logger.exception(f"Image upload error: {repr(e)}")
                if repr(e):
                    return render(request, "photo/upload.html", {"form": form, "error": repr(e)})
                return render(request, "photo/upload.html", {"form": form, "error": f"Nie można połączyć się z serwerem."})

            return redirect(image_object)
    else:
        form = SendPhotoForm()
    return render(request, "photo/upload.html", {"form": form})


def photo_detail(request, uuid):
    """
    Site to display details of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid)
    post_review_form = PostReviewForm()
    reviews = Review.objects.filter(photo=photo)

    if photo.prediction_1:
        prediction_1 = photo.prediction_1.split(';')[-1]
        prediction_2 = photo.prediction_2.split(';')[-1] if photo.prediction_2  else ''
        prediction_pl = photo.prediction_pl.split(';')[-1] if photo.prediction_pl else ''
        prediction_1_probability = photo.prediction_1_probability
        prediction_2_probability = photo.prediction_2_probability
        return render(request, "photo/details.html", {
            "photo": photo,
            "prediction_1": prediction_1,
            "prediction_2": prediction_2,
            "prediction_pl": prediction_pl,
            "prediction_1_probability": prediction_1_probability,
            "prediction_2_probability": prediction_2_probability,
            "post_review_form": post_review_form,
            "reviews": reviews
        })

    return render(request, "photo/details.html", {
        "photo": photo,
        "post_review_form": post_review_form,
        "reviews": reviews
    })


@login_required
def delete_photo(request, uuid):
    """
    View that handles photo deletion
    Deletes photo from database, disk and reviews associated
    """
    photo = get_object_or_404(Photo, uuid=uuid)
    # delete photo from disk
    photo_path = photo.image.path
    if os.path.exists(photo_path):
        os.remove(photo_path)
    # from database
    photo.delete()
    # reviews are deleted automatically, because of CASCADE

    return redirect('gallery:browse_my')


@login_required
def toggle_photo_privacy(request, uuid):
    """
    View to handle privacy change of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid, owner=request.user)

    if request.method == "POST":
        photo.is_private = not photo.is_private
        photo.save()
        return redirect(photo)
    
    return HttpResponseBadRequest({'error': 'Invalid request'}, status=400)


@login_required
def toggle_review(request, uuid):
    """
    Function to change review status
    review_status values:
     0 - not to be reviewed
     1 - to be reviewed
     2 - reviewed
    """
    photo = get_object_or_404(Photo, uuid=uuid, owner=request.user)

    if request.method == "POST":
        if photo.review_status != 1:
            photo.review_status = 1
        else:
            photo.review_status = 2

        photo.save()
        return redirect(photo)
    
    return HttpResponseBadRequest({'error': 'Invalid request'}, status=400)


@login_required
def post_review(request, uuid):
    """
    View that handles posting a review
    """
    photo = get_object_or_404(Photo, uuid=uuid)
    form = PostReviewForm(request.POST)

    if request.method == "POST" and form.is_valid():
        review_object = Review.objects.create(
            owner = request.user,
            photo = photo,
            review = form.cleaned_data['review']
        )
        review_object.save()

    return redirect(photo)


@login_required
def toggle_helpful(request, review_id:int):
    """
    View that let's owner of photo mark or unmark comment as helpful
    """
    review = get_object_or_404(Review, id=review_id)

    if review.photo.owner == request.user and review.owner != request.user:
        if review.helpful:
            review.owner.score -= 1
        else:
            review.owner.score += 1
        review.owner.save()
        review.helpful = not review.helpful
        review.save()

    return redirect(review.photo)


@login_required
def delete_review(request, review_id:int):
    """
    View that let's post of review delete it
    """
    review = get_object_or_404(Review, id=review_id)

    if review.owner == request.user:
        review.delete()
    
    return redirect(review.photo)


@require_POST
@login_required
def rename_photo(request, uuid):
    photo = get_object_or_404(Photo, uuid=uuid)

    new_name = request.POST.get('custom_name')
    if new_name and photo.owner == request.user:
        photo.custom_name = new_name
        photo.save()

    return redirect(photo)


@require_POST
@login_required
def set_location(request, uuid):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, uuid=uuid)
        lat = request.POST.get('localization_lat')
        lng = request.POST.get('localization_lng')

        if not lat or not lng:
            return HttpResponseBadRequest({'error': 'Invalid request'}, status=400)

        lat = float(lat)
        lng = float(lng)

        if photo.owner == request.user and lat and lng:
            noisy_lat, noisy_lng = add_noise_to_localization(latitude=lat, longitude=lng)
            photo.localization_latitude=noisy_lat
            photo.localization_longitude=noisy_lng
            photo.save()
        return redirect(photo)

    return HttpResponseBadRequest({'error': 'Invalid request'}, status=400)
