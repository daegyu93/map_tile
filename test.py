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
    # 첫 번째 타일 다운로드로 타일 크기를 확인
    sample_tile = download_tile(x_start, y_start, zoom)
    tile_height, tile_width, _ = sample_tile.shape

    # 전체 이미지를 담을 빈 캔버스 생성
    stitched_image = np.zeros((tile_height * (y_end - y_start + 1),  # y와 x의 크기를 바르게 설정
                               tile_width * (x_end - x_start + 1),
                               3), dtype=np.uint8)

    # 타일을 하나씩 다운로드하고, 캔버스에 위치시키기
    for y in range(y_start, y_end + 1):  # y를 먼저 반복
        for x in range(x_start, x_end + 1):  # x를 나중에 반복
            tile_image = download_tile(x, y, zoom)
            stitched_image[(y - y_start) * tile_height: (y - y_start + 1) * tile_height,  
                           (x - x_start) * tile_width: (x - x_start + 1) * tile_width] = tile_image

    return stitched_image


def latlon_to_tile_xy(latitude, longitude, zoom):
    x = math.floor((longitude + 180) / 360 * 2**zoom)
    y = math.floor((1 - math.log(math.tan(math.radians(latitude)) + 1 / math.cos(math.radians(latitude))) / math.pi) / 2 * 2**zoom)
    return x, y

latitude = 37.392877297564496  
longitude = 127.15654142595137  
zoom = 19  

center_x, center_y = latlon_to_tile_xy(latitude, longitude, zoom)

size = 5
x_start, x_end = center_x - size, center_x + size
y_start, y_end = center_y - size, center_y + size

stitched_image = stitch_tiles(x_start, x_end, y_start, y_end, zoom)

frame = cv2.resize(stitched_image, (540, 540), interpolation=cv2.INTER_AREA)

# 결과 이미지 확인
cv2.imshow("Stitched Satellite Image", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

