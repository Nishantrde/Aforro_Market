_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def encode(lat, lng, precision=6):
    lat_lo, lat_hi = -90.0, 90.0
    lng_lo, lng_hi = -180.0, 180.0
    code, bits, count, use_lng = "", 0, 0, True
    while len(code) < precision:
        if use_lng:
            mid = (lng_lo + lng_hi) / 2
            if lng >= mid: bits = (bits << 1) | 1; lng_lo = mid
            else:          bits = bits << 1;       lng_hi = mid
        else:
            mid = (lat_lo + lat_hi) / 2
            if lat >= mid: bits = (bits << 1) | 1; lat_lo = mid
            else:          bits = bits << 1;       lat_hi = mid
        use_lng = not use_lng
        count += 1
        if count == 5:
            code += _BASE32[bits]
            bits, count = 0, 0
    return code

# precision 6 = 30 bits = 15 for lng + 15 for lat
LAT_STEP = 180 / 2**15     # about 0.0055 degrees (about 600 m)
LNG_STEP = 360 / 2**15     # about 0.011 degrees (about 1.2 km)

def cells_around(lat, lng):
    # the rider's cell + 8 neighbours: shift one cell in every direction and re-encode
    return {
        encode(lat + dy * LAT_STEP, lng + dx * LNG_STEP)
        for dy in (-1, 0, 1)
        for dx in (-1, 0, 1)
    }
    