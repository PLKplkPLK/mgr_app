from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Photo

from datetime import datetime
import uuid

from absl import flags
from speciesnet.scripts import run_model

@login_required
def upload(request):
    """
    A site to upload and classify a photo
    """
    MAX_FILE_SIZE = 1e7 # 10 MB

    # DOS protections should be added. Like: frequency of requests, image size
    if request.method == "POST" and request.FILES['image_file']:
        image = request.FILES["image_file"]

        if image.size > MAX_FILE_SIZE:
            return render(request, "upload.html", {'error': 'Zbyt duży plik'})
        
        image_uuid = uuid.uuid4()

        classify_image(image_uuid)

        image_object = Photo.objects.create(
            uuid = image_uuid,
            upload_time = datetime.now.strftime('%Y-%m-%d %H:%M:%S'),
            is_private = request.POST["is_private"],
            owner_id = request.user.id
        )
        image_object.save()

        return redirect('')
    else:
        return render(request, "upload.html")

@login_required
def classify_image(image_uuid: str) -> str:
    """
    Function that classifies image, based on it's path.
    Returns string with animal's name
    """
    # można sprawdzić --target_species_txt w helpie
    flags.FLAGS(['run_model'])
    flags.FLAGS.filepaths = "test_images/" + image_uuid + ".jpg"
    flags.FLAGS.country = "POL"
    flags.FLAGS.progress_bars = False
    flags.FLAGS.predictions_json = "test_images/" + image_uuid + ".json"

    run_model.main(['run_model'])
