
import random

def add_noise_to_localization(latitude: float, longitude: float, max_noise_lat: float=0.27, max_noise_lng: float=0.44):
    """
    0.27 latitude and 0.44 latitude is about 30 km.
    Returns noised_lat, noised_lng
    """
    noised_lat = latitude + random.uniform(-max_noise_lat, max_noise_lat)
    noised_lng = longitude + random.uniform(-max_noise_lng, max_noise_lng)

    return noised_lat, noised_lng
