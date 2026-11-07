import math


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371   # earth radius in km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def nearest(riders, store_lat, store_lng):
    if not riders:
        return None

    best = min(
        riders,
        key=lambda r: (haversine_km(r[1], r[2], store_lat, store_lng), r[0]),
    )
    return best[0]