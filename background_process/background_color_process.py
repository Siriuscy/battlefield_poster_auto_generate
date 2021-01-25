from colour import find_palettes
import os
import cv2
import numpy as np
from colour.utils import functions_utils

'''
为每一个background_img 定制模板信息
'''

background_img_path = "../bg_img"
bk_img_list = os.listdir(background_img_path)
clusters_num = 2


def get_colour_cluster_list(bk_img_path, num_clusters=clusters_num):
    """
    对比度
    :return:颜色聚类
    """
    bk_img = cv2.imread(bk_img_path )
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
        h, s, v = functions_utils.rgb2hsv(r, g, b)
        colour_list.append((h, s, v))
    return colour_list


def get_bk_img_palettes():
    pass
