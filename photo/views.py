from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile

import requests
import os
from PIL import Image
from io import BytesIO

from .models import Photo, Review
from .forms import SendPhotoForm, PostReviewForm
from .helpers import add_noise_to_localization


map_animals_pl = {
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
    'american bison': 'Żubr europejski', # trochę oszustwo
    'northern raccoon': 'Szop pracz',
    'eurasian red squirrel': 'Wiewiórka pospolita',
    'wild boar': 'Dzik euroazjatycki',
    'moose': 'Łoś euroazjatycki',
    'european hare': 'Zając szarak',
    'eurasian badger': 'Borsuk europejski',
}


def convert_image_to_webp(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.convert("RGB")  # Ensures compatibility (e.g. for PNGs with alpha)

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=85)

    webp_filename = f"{os.path.splitext(uploaded_file.name)[0]}.webp"

    return ContentFile(buffer.getvalue(), name=webp_filename)


@login_required
def upload(request):
    """
    A site to upload and classify a photo
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
                owner = request.user
            )

            # The classification is done on a separate server via API
            try:
                url = "http://localhost:8008/predict"
                data = {
                    "instances": [
                        {
                            "filepath": "http://127.0.0.1:8000" + image_object.image.url,
                            "country": "POL"
                        }
                    ]
                }
                response = requests.post(url, json=data).json()
                response = response['predictions'][0]

                image_object.prediction_1  = map_animals_pl.setdefault(response['classifications']['classes'][0].strip().split(";")[-1], response['classifications']['classes'][0].strip().split(";")[-1])
                image_object.prediction_2  = map_animals_pl.setdefault(response['classifications']['classes'][1].strip().split(";")[-1], response['classifications']['classes'][1].strip().split(";")[-1])
                image_object.prediction_pl = map_animals_pl.setdefault(response['prediction'].strip().split(";")[-1], response['prediction'].strip().split(";")[-1])
                image_object.prediction_1_probability = response['classifications']['scores'][0] * 100 # percent
                image_object.prediction_2_probability = response['classifications']['scores'][1] * 100 # percent
                image_object.save()
            except Exception as e:
                photo_path = image_object.image.path
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                image_object.delete()
                return render(request, "photo/upload.html", {"form": form, "error": "Nie można połączyć się z serwerem"})

            return redirect(image_object)
    else:
        form = SendPhotoForm()
    return render(request, "photo/upload.html", {"form": form})


@login_required
def photo_detail(request, uuid):
    """
    Site to display details of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid)
    post_review_form = PostReviewForm()
    reviews = Review.objects.filter(photo=photo)

    if photo.prediction_1:
        prediction_1 = photo.prediction_1.split(';')[-1]
        prediction_2 = photo.prediction_2.split(';')[-1]
        prediction_pl = photo.prediction_pl.split(';')[-1]
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
        lat = float(request.POST.get('localization_lat'))
        lng = float(request.POST.get('localization_lng'))

        if photo.owner == request.user and lat and lng:
            noisy_lat, noisy_lng = add_noise_to_localization(latitude=lat, longitude=lng)
            photo.localization_latitude=noisy_lat
            photo.localization_longitude=noisy_lng
            photo.save()
        return redirect(photo)

    return HttpResponseBadRequest({'error': 'Invalid request'}, status=400)
