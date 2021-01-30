import math
import numpy as np
import cv2
import json
from generate_background_info import constants


def rgb2hsv(color):
    '''

    :param color: (233,233,233)
    :return: h,s,v
    '''
    r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df / mx
    v = mx
    return h, s, v


def read_and_write_cache():
    '''
    对背景图片的聚类分析数据进行缓存，不然运行数据太慢了
    :return:
    '''

    def decorator(original_func):
        try:
            f = json.load(open(constants.CACHE_PATH, "r"))
        except(IOError, ValueError):
            f = {}

        def new_func(id):
            if id not in f:
                f[id] = original_func(id)
                json.dump(f, open(constants.CACHE_PATH, "w"), indent=4)
            return f[id]

        return new_func

    return decorator


def HSVDistance(hsv_1, hsv_2):
    H_1, S_1, V_1 = hsv_1
    H_2, S_2, V_2 = hsv_2
    R = 100
    angle = 30
    h = R * math.cos(angle / 180 * math.pi)
    r = R * math.sin(angle / 180 * math.pi)
    x1 = r * V_1 * S_1 * math.cos(H_1 / 180 * math.pi)
    y1 = r * V_1 * S_1 * math.sin(H_1 / 180 * math.pi)
    z1 = h * (1 - V_1)
    x2 = r * V_2 * S_2 * math.cos(H_2 / 180 * math.pi)
    y2 = r * V_2 * S_2 * math.sin(H_2 / 180 * math.pi)
    z2 = h * (1 - V_2)
    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    return math.sqrt(dx * dx + dy * dy + dz * dz)


@read_and_write_cache()
def get_colour_cluster_list(bk_img_path, num_clusters=2):
    """
    对比度
    :return:颜色聚类
    """
    bk_img = cv2.imread(bk_img_path)
    h, w, ch = bk_img.shape
    data = bk_img.reshape((-1, 3))
    data = np.float32(data)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # 聚类数量

    ret, label, center = cv2.kmeans(data, num_clusters, None, criteria,
                                    num_clusters, cv2.KMEANS_RANDOM_CENTERS)
    clusters = np.zeros([num_clusters], dtype=np.int32)
    for i in range(len(label)):
        clusters[label[i][0]] += 1
    clusters = np.float32(clusters) / float(h * w)
    center = np.int32(center)
    colour_list = []
    for c in np.argsort(clusters)[::-1]:  # 这里对主色按比例从大到小排序 [::-1] 代表首尾反转 如[1,2,3] -> [3, 2, 1]
        b = center[c][0]  # 这一类对应的中心，即 RGB 三个通道的值
        g = center[c][1]
        r = center[c][2]
        h, s, v = rgb2hsv((r, g, b))
        colour_list.append((h, s, v))
    return colour_list


def hex_to_hsv(hex_):
    r = int(hex_[1:3], 16)
    g = int(hex_[3:5], 16)
    b = int(hex_[5:7], 16)
    h, s, v = rgb2hsv((r, g, b))
    return np.array([h, s, v])


def hex_to_rgb(_):
    r = int(_[1:3], 16)
    g = int(_[3:5], 16)
    b = int(_[5:7], 16)
    return r, g, b
