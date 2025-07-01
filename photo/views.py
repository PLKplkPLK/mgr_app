from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Photo
from .forms import SendPhotoForm
from .classification import run_speciesnet_model

@login_required
def upload(request):
    """
    A site to upload and classify a photo
    """
    MAX_FILE_SIZE = 1e7 # 10 MB

    if request.method == "POST":
        form = SendPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            # save image (disk and database)
            image_object = Photo.objects.create(
                is_private = form.cleaned_data['is_private'],
                image = form.cleaned_data['image_file'],
                owner_id = request.user
            )

            # classify image
            run_speciesnet_model(
                filepath=image_object.image.path,
                country="POL",
                predictions_json="predictions/" + str(image_object.uuid) + ".json"
            )

            image_object.prediction = # zrobić jako server???

            image_object.save()

            return redirect(image_object)
    else:
        form = SendPhotoForm()
    return render(request, "upload.html", {"form": form})

@login_required
def photo_detail(request, uuid):
    photo = get_object_or_404(Photo, uuid=uuid)
    return render(request, "details.html", {"photo": photo})
