from django.core.cache import cache

def geoHash(location, div = 10):
    lat_range = [-90, 90]
    lon_range = [-180, 180]

    hash = ""
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"

    bit = 0
    value = 0

    for i in range(div * 5):

        if i % 2 == 0:
            mid = (lon_range[0] + lon_range[1])/2

            if location[0] >= mid:
                value = (value << 1) | 1
                lon_range[0] = mid
            else:
                value = (value << 1) | 0
                lon_range[1] = mid
                
        else:
            mid = (lat_range[0] + lat_range[1])/2
        
            if location[1] >= mid:
                value = (value << 1) | 1
                lat_range[0] = mid
            else:
                value = (value << 1) | 0
                lat_range[1] = mid

        bit += 1

        if bit == 5:
            hash += base32[value]
            value = 0
            bit = 0

    cache.set(f'{hash}', location, 60) # RMEMBER!!!! to remove 60 sec in  production otherwise the cache data will keep on deleting

    return hash

if __name__ == "__main__":
    print(geoHash((-122.4194, 37.7749)))

    

