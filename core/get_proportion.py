import cv2
from . import constants


def get_proportion():
    """

    :return: x,y的比例
    """
    bk_img = cv2.imread(constants.BG_IMG_PATH)
    orginal_img = cv2.imread(constants.BG_IMG_PATH)
    x_proportion = bk_img.shape[1] / orginal_img.shape[1]
    y_proportion = bk_img.shape[0] / orginal_img.shape[0]
    return x_proportion, y_proportion
