import redis
from .geohash import encode, cells_around
from django.conf import settings


class RedisLocations:
    def __init__(self, url):
        self.r = redis.from_url(url, socket_connect_timeout=1, socket_timeout=1)

    def update(self, partner_id, lat, lng):
        self.remove(partner_id)                      # leave the old cell first
        cell = encode(lat, lng)
        self.r.sadd(f"zone:{cell}", partner_id)      # bucket: set of rider ids
        self.r.set(f"rider:{partner_id}", f"{lat},{lng},{cell}", ex=1800)

    def remove(self, partner_id):
        val = self.r.get(f"rider:{partner_id}")
        if val is not None: cell = val.decode().split(",")[2]
        self.r.srem(f"zone:{cell}", partner_id)
        self.r.delete(f"rider:{partner_id}")

    def nearby(self, lat, lng):
        riders = []
        for cell in cells_around(lat, lng):
            for pid in self.r.smembers(f"zone:{cell}"):
                pid = int(pid)                       # Redis returns bytes
                val = self.r.get(f"rider:{pid}")
                if val is None:                      # key expired, skip him
                    continue
                rlat, rlng, _ = val.decode().split(",")
                riders.append((pid, float(rlat), float(rlng)))
        return riders

class MemoryLocations:
    def __init__(self):
        self.riders = {}

    def update(self, partner_id, lat, lng):
        self.riders[partner_id] = (lat, lng)

    def remove(self, partner_id):
        self.riders.pop(partner_id, None)

    def all(self):
        return [(pid, lat, lng) for pid, (lat, lng) in self.riders.items()]

    def nearby(self, lat, lng):
        return self.all()     # in tests, every rider counts as "nearby"


def get_locations():
    if settings.REDIS_URL and not settings.RUNNING_TESTS:
        return RedisLocations(settings.REDIS_URL)
    return MemoryLocations()

locations = get_locations()
