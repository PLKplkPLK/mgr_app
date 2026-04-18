import json
import math
import os
import random
from io import BytesIO
from typing import Any

import requests
from PIL import Image
from django.core.files.base import ContentFile

from .models import Photo


MAX_IMAGE_SIZE = 1e7
PREDICTION_API_URL = "http://localhost:8006/predict"


def add_noise_to_localization(
    latitude: float,
    longitude: float,
    max_noise_lat: float = 0.27,
    max_noise_lng: float = 0.44,
) -> tuple[float, float]:
    """
    Add noise to coordinates.
    0.27 latitude and 0.44 longitude is about 30 km.
    """
    noised_lat = latitude + random.uniform(-max_noise_lat, max_noise_lat)
    noised_lng = longitude + random.uniform(-max_noise_lng, max_noise_lng)
    return noised_lat, noised_lng


def convert_image_to_webp(uploaded_file) -> ContentFile:
    img = Image.open(uploaded_file)
    img = img.convert("RGB")  # Compatibility (e.g. for PNGs with alpha)
    img.thumbnail((2000, 2000))

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=85)

    webp_filename = f"{os.path.splitext(uploaded_file.name)[0]}.webp"
    return ContentFile(buffer.getvalue(), name=webp_filename)


def request_prediction(
    image_webp: ContentFile, url: str = PREDICTION_API_URL, timeout: int = 30
) -> dict[str, Any]:
    image_webp.seek(0)
    files = {"image": (image_webp.name, image_webp.read(), "image/webp")}
    response = requests.post(url, files=files, timeout=timeout)
    response.raise_for_status()
    return response.json()


def create_photo_from_response(
    request, is_private: bool, image_webp: ContentFile,
    response: dict[str, Any]
) -> Photo:
    image_object = Photo.objects.create(
        is_private=is_private,
        image=image_webp,
        owner=request.user if request.user.is_authenticated else None,
        prediction="",
        prediction_confidence=0,
        review_status=1,
    )

    if response.get("category") != 1:
        image_object.prediction = "empty"
    else:
        image_object.prediction = response.get("detected_animal")
        image_object.prediction_confidence = response.get("confidence", 0)
        image_object.prediction_2 = response.get("detected_animal_2", "empty")
        image_object.prediction_confidence_2 = response.get("confidence_2", 0)
        bbox = response.get("bbox") or [0, 0, 0, 0]
        image_object.bbox = json.dumps(bbox)
        if image_object.prediction_confidence > 0.9:
            image_object.review_status = 0

    image_object.save()
    return image_object


def cleanup_photo_upload_failure(image_object: Photo | None) -> None:
    if image_object is None:
        return

    image_object.image.delete(save=False)
    image_object.delete()


def get_photo_display_names(
    photo: Photo, animals_map: dict[str, str]
) -> tuple[str | None, str | None, str | None]:
    photo_display_name = (
        photo.custom_name if photo.custom_name else photo.prediction
    )
    return (
        animals_map.get(photo_display_name),
        animals_map.get(photo.prediction),
        animals_map.get(photo.prediction_2),
    )


def parse_bbox(photo: Photo) -> list[float]:
    if not photo.bbox:
        return [0, 0, 0, 0]

    bbox = json.loads(photo.bbox)
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return [0, 0, 0, 0]

    return [float(element) * 100 for element in bbox]


def get_cell_bounds(
    photo: Photo, current_user, grid_size: float = 0.3
) -> list[float] | None:
    if (
        photo.owner == current_user
        or not photo.localization_latitude
        or not photo.localization_longitude
    ):
        return None

    lat = photo.localization_latitude
    lng = photo.localization_longitude
    cell_lat_start = math.floor(lat / grid_size) * grid_size
    cell_lng_start = math.floor(lng / grid_size) * grid_size
    return [
        cell_lat_start,
        cell_lng_start,
        cell_lat_start + grid_size,
        cell_lng_start + grid_size,
    ]
