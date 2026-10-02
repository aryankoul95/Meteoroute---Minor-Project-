from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="meteoroute-minor-project")


def geocode_place(place: str):
    location = geolocator.geocode(place)

    if location is None:
        return None

    return {
        "name": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude,
    }
