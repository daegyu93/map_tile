import cv2
import numpy as np
import requests
import math

def download_tile(x, y, zoom):
    url = f"https://map.pstatic.net/nrb/styles/satellite/{zoom}/{x}/{y}.png"
    print(url)
    response = requests.get(url)
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

def stitch_tiles(x_start, x_end, y_start, y_end, zoom):
    sample_tile = download_tile(x_start, y_start, zoom)
    tile_height, tile_width, _ = sample_tile.shape

    stitched_image = np.zeros((tile_height * (y_end - y_start + 1),
                               tile_width * (x_end - x_start + 1),
                               3), dtype=np.uint8)

    for y in range(y_start, y_end + 1):
        for x in range(x_start, x_end + 1):
            tile_image = download_tile(x, y, zoom)
            stitched_image[(y - y_start) * tile_height: (y - y_start + 1) * tile_height,  
                           (x - x_start) * tile_width: (x - x_start + 1) * tile_width] = tile_image

    return stitched_image

def latlon_to_tile_xy(latitude, longitude, zoom):
    x = math.floor((longitude + 180) / 360 * 2**zoom)
    y = math.floor((1 - math.log(math.tan(math.radians(latitude)) + 1 / math.cos(math.radians(latitude))) / math.pi) / 2 * 2**zoom)
    return x, y

def tile_xy_to_latlon(x, y, zoom):
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        tile_width, tile_height = param['tile_size']
        x_tile_offset = x // tile_width
        y_tile_offset = y // tile_height

        x_tile = param['x_start'] + x_tile_offset
        y_tile = param['y_start'] + y_tile_offset

        lat, lon = tile_xy_to_latlon(x_tile + (x % tile_width) / tile_width, 
                                     y_tile + (y % tile_height) / tile_height, 
                                     param['zoom'])

        print(f"Clicked position - Latitude: {lat}, Longitude: {lon}")

latitude = 37.392877297564496  
longitude = 127.15654142595137  
zoom = 15  

center_x, center_y = latlon_to_tile_xy(latitude, longitude, zoom)

size = 3
x_start, x_end = center_x - size, center_x + size
y_start, y_end = center_y - size, center_y + size

stitched_image = stitch_tiles(x_start, x_end, y_start, y_end, zoom)

frame = cv2.resize(stitched_image, (800, 800), interpolation=cv2.INTER_AREA)

cv2.imshow("Stitched Satellite Image", frame)

params = {
    'x_start': x_start,
    'y_start': y_start,
    'zoom': zoom,
    'tile_size': (frame.shape[1] // (x_end - x_start + 1), frame.shape[0] // (y_end - y_start + 1))
}

cv2.setMouseCallback("Stitched Satellite Image", on_mouse, params)

cv2.waitKey(0)
cv2.destroyAllWindows()
