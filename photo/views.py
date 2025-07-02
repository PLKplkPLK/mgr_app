from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseBadRequest

import requests

from .models import Photo
from .forms import SendPhotoForm

@login_required
def upload(request):
    """
    A site to upload and classify a photo
    """
    if request.method == "POST":
        form = SendPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            # save image (disk and database)
            image_object = Photo.objects.create(
                is_private = form.cleaned_data['is_private'],
                image = form.cleaned_data['image_file'],
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

                image_object.prediction_1  = response['classifications']['classes'][0]
                image_object.prediction_2  = response['classifications']['classes'][1]
                image_object.prediction_pl = response['prediction']
                image_object.prediction_1_probability = response['classifications']['scores'][0]
                image_object.prediction_2_probability = response['classifications']['scores'][1]
                image_object.save()
            except Exception as e:
                # the photo file still stays on disk - TODO
                image_object.delete()
                return render(request, "upload.html", {"form": form, "error": "Nie można połączyć się z serwerem"})

            return redirect(image_object)
    else:
        form = SendPhotoForm()
    return render(request, "upload.html", {"form": form})

@login_required
def photo_detail(request, uuid):
    """
    Site to display details of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid)

    if photo.prediction_1:
        prediction_1 = photo.prediction_1.split(';')[-1]
        prediction_2 = photo.prediction_2.split(';')[-1]
        prediction_pl = photo.prediction_pl.split(';')[-1]
        prediction_1_probability = photo.prediction_1_probability
        prediction_2_probability = photo.prediction_2_probability
        return render(request, "details.html", {
            "photo": photo,
            "prediction_1": prediction_1,
            "prediction_2": prediction_2,
            "prediction_pl": prediction_pl,
            "prediction_1_probability": prediction_1_probability,
            "prediction_2_probability": prediction_2_probability
        })

    return render(request, "details.html", {"photo": photo})
    
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
