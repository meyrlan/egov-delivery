import requests
import secrets
import string
from core.models import *
from math import radians, sin, cos, sqrt, atan2


def get_random_code(length: int = 4) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def get_address_lat_lng(full_address: str):
    response = requests.get(
        f"https://geocode-maps.yandex.ru/1.x",
        params={
            "apikey": "64a40e41-9d55-41fb-9c6f-ae3092d0ecdd",
            "geocode": full_address,
            "format": "json",
        }
    )
    print(full_address)
    print(response.json())
    lat_lng = response.json()['response'][
        "GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split(" ")
    return lat_lng[1], lat_lng[0]


def get_route_payment_amount(source_address, target_address):
    if not source_address or not target_address or not source_address.lat or not source_address.lng or not target_address.lat or not target_address.lng:
        return 945
    lat1, lon1 = source_address.lat, source_address.lng
    lat2, lon2 = target_address.lat, target_address.lng

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c

    print(distance)
    return max(850, distance * 250)
