import math

def calculate_center_xy(latitude, longitude, scale, max_zoom, min_zoom):
    # 경도와 위도의 범위를 제한
    latitude = max(-90.0, min(90.0, latitude))
    longitude = max(-180.0, min(180.0, longitude))

    # 위도를 라디안으로 변환
    lat = math.radians(latitude)

    # 현재 줌 레벨 계산
    lat_circumference = 40075017 * math.cos(lat) / scale  # 지구 둘레: 약 40075 km
    level = min(max_zoom, max(min_zoom, math.ceil(math.log(lat_circumference) / math.log(2) - 8)))

    max_size = 2 ** level

    # center_x 계산
    center_x = min(max_size - 1, math.floor(((longitude + 180.0) / 360.0) * 2 ** level))

    # center_y 계산
    center_y = min(max_size - 1, math.floor((1.0 - math.log(math.tan(lat) + 1.0 / math.cos(lat)) / math.pi) / 2.0 * 2 ** level))

    return center_x, center_y

def calculate_lat_lon(center_x, center_y, level):
    # 줌 레벨에 따른 최대 타일 크기
    max_size = 2 ** level

    # 경도 계산 (center_x에서 역으로 계산)
    longitude = center_x / max_size * 360.0 - 180.0

    # 위도 계산 (center_y에서 역으로 계산)
    n = math.pi - 2.0 * math.pi * center_y / max_size
    latitude = math.degrees(math.atan(math.sinh(n)))

    return latitude, longitude

def latlon_to_tile_xy(latitude, longitude, zoom):
    x = math.floor((longitude + 180) / 360 * 2**zoom)
    y = math.floor((1 - math.log(math.tan(math.radians(latitude)) + 1 / math.cos(math.radians(latitude))) / math.pi) / 2 * 2**zoom)
    return x, y

# def latlon_to_tile_xy(latitude, longitude, zoom):
#     x = math.floor((longitude + 180) / 360 * 2**zoom)
#     siny = math.sin(math.radians(latitude))
#     y = math.floor((0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)) * 2**zoom)
#     return x, y

# 예시 사용
latitude = 37.392877297564496  
longitude = 127.15654142595137  
zoom = 13  # 최대 줌 레벨

center_x, center_y = latlon_to_tile_xy(latitude, longitude, zoom)
print("Center X:", center_x)
print("Center Y:", center_y)
print("https://mt.google.com/vt/lyrs=s&x={}&y={}&z={}".format(center_x, center_y, zoom))
print("https://map.pstatic.net/nrb/styles/satellite/{}/{}/{}.png".format(zoom, center_x, center_y ))
print("http://localhost:8080/wmts/gm_layer/gm_grid/{}/{}/{}.png".format(zoom, center_x, center_y ))
