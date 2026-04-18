import logging
import os

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest

from account.models import Correction
from .models import Photo, Review
from .forms import SendPhotoForm, PostReviewForm
from .helpers import (cleanup_photo_upload_failure, convert_image_to_webp,
                      create_photo_from_response, get_cell_bounds,
                      get_photo_display_names, parse_bbox, request_prediction)
from animals import animals_list, animals_pl_map


logger = logging.getLogger(__name__)
animals_pl_map = {
    k: v for k, v in sorted(animals_pl_map.items(), key=lambda item: item[1])
}


def upload(request):
    """A site to upload and classify a photo."""
    if request.method != "POST":
        form = SendPhotoForm()
        return render(request, "photo/upload.html", {"form": form})

    form = SendPhotoForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "photo/upload.html", {"form": form})

    image_webp = convert_image_to_webp(form.cleaned_data["image_file"])
    image_object = None

    try:
        response = request_prediction(image_webp)
        image_object = create_photo_from_response(
            request,
            is_private=form.cleaned_data["is_private"],
            image_webp=image_webp,
            response=response,
        )
    except requests.RequestException as exc:
        if image_object:
            cleanup_photo_upload_failure(image_object)
        logger.exception("Image upload error: %s", exc)
        return render(
            request,
            "photo/upload.html",
            {"form": form, "error": "Nie można połączyć się z serwerem."},
        )
    except Exception as exc:
        if image_object:
            cleanup_photo_upload_failure(image_object)
        logger.exception("Image upload error: %s", exc)
        return render(
            request,
            "photo/upload.html",
            {
                "form": form,
                "error": "Wystąpił błąd podczas przetwarzania pliku.",
            },
        )

    return redirect(image_object)


def photo_detail(request, uuid: str):
    """
    Site to display details of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid)

    if photo.is_private and photo.owner != request.user:
        return HttpResponse("Unauthorized", status=401)

    photo.n_times_seen = photo.n_times_seen + 1
    photo.save()

    post_review_form = PostReviewForm()
    reviews = Review.objects.filter(photo=photo)

    photo_display_name, prediction_display_name, prediction_display_name_2 = (
        get_photo_display_names(photo, animals_pl_map)
    )
    bbox = parse_bbox(photo)
    cell_bounds = get_cell_bounds(photo, request.user)

    return render(
        request,
        "photo/details.html",
        {
            "photo": photo,
            "photo_display_name": photo_display_name,
            "prediction_display_name": prediction_display_name,
            "prediction_display_name_2": prediction_display_name_2,
            "post_review_form": post_review_form,
            "reviews": reviews,
            "animals_map": animals_pl_map.items(),
            "bbox": bbox,
            "cell_bounds": cell_bounds,
        },
    )


@login_required
def delete_photo(request, uuid: str):
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

    return redirect("gallery:browse_my")


@login_required
def toggle_photo_privacy(request, uuid: str):
    """
    View to handle privacy change of a photo
    """
    photo = get_object_or_404(Photo, uuid=uuid, owner=request.user)

    if request.method == "POST":
        photo.is_private = not photo.is_private
        photo.save()
        return redirect(photo)

    return HttpResponseBadRequest({"error": "Invalid request"}, status=400)


@login_required
def toggle_review(request, uuid: str):
    """
    Function to change review status
    review_status values:
     0 - not to be reviewed
     1 - to be reviewed
    """
    photo = get_object_or_404(Photo, uuid=uuid)

    post_and_authorized = request.method == "POST" and (
        photo.owner == request.user or request.user.protector
    )
    if post_and_authorized:
        if photo.review_status == 1:
            photo.review_status = 0
        else:
            photo.review_status = 1

        photo.save()
        return redirect(photo)

    return HttpResponseBadRequest({"error": "Invalid request"}, status=400)


@login_required
def post_review(request, uuid: str):
    """
    View that handles posting a review
    """
    photo = get_object_or_404(Photo, uuid=uuid)
    form = PostReviewForm(request.POST)

    if request.method == "POST" and form.is_valid():
        review_object = Review.objects.create(
            owner=request.user, photo=photo, review=form.cleaned_data["review"]
        )
        review_object.save()

    return redirect(photo)


@login_required
def toggle_helpful(request, review_id: int):
    """
    View that let's owner of photo mark or unmark comment as helpful
    """
    review = get_object_or_404(Review, id=review_id)

    if review.photo.owner == request.user and review.owner != request.user:
        if review.helpful:
            review.owner.score -= 1  # type: ignore
        else:
            review.owner.score += 1  # type: ignore
        review.owner.save()
        review.helpful = not review.helpful
        review.save()

    return redirect(review.photo)


@login_required
def delete_review(request, review_id: int):
    """
    View that let's post of review delete it
    """
    review = get_object_or_404(Review, id=review_id)

    if review.owner == request.user:
        review.delete()

    return redirect(review.photo)


@require_POST
@login_required
def rename_photo(request, uuid: str):
    """Change photo's custom name."""
    photo = get_object_or_404(Photo, uuid=uuid)
    new_name = request.POST.get("custom_name")
    if new_name not in animals_list:
        return HttpResponseBadRequest()

    if new_name and (photo.owner == request.user or request.user.protector):
        if request.user != photo.owner:
            log = Correction(
                user=request.user,
                message=(
                    f"Changed name of photo '{photo.uuid}' from "
                    f"'{photo.custom_name}' to '{new_name}'"
                ),
            )
            log.save()
        photo.custom_name = new_name
        photo.save()

    return redirect(photo)


@require_POST
@login_required
def set_location(request, uuid: str):
    if request.method == "POST":
        photo = get_object_or_404(Photo, uuid=uuid)
        lat = request.POST.get("localization_lat")
        lng = request.POST.get("localization_lng")

        if not lat or not lng:
            return HttpResponseBadRequest(
                {"error": "Invalid request"}, status=400
            )

        lat = float(lat)
        lng = float(lng)

        if photo.owner == request.user and lat and lng:
            photo.localization_latitude = lat
            photo.localization_longitude = lng
            photo.save()
        return redirect(photo)

    return HttpResponseBadRequest({"error": "Invalid request"}, status=400)
