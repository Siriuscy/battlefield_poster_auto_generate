from . import utils, get_proportion
import input
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2


def write_on_pic(coordinate_list, bk_img):
    x_proportion, y_proportion = get_proportion()
    img_pil = Image.fromarray(bk_img)
    draw = ImageDraw.Draw(img_pil)
    print("y_proportion:{}".format(y_proportion))

    for _ in coordinate_list:
        text = input.text_in[_[0]]
        print(text)
        fontpath_headline = "./PingFang-JianZhongHeiTi-2.ttf"
        font_size = utils(_, text) * x_proportion
        font_headline = ImageFont.truetype(fontpath, int(font_size))
        #         text_positon=(_[1]*x_proportion,_[3]*y_proportion)
        text_positon = (_[1] * x_proportion, _[3] * y_proportion)

        print(text_positon)
        # 绘制文字信息
        draw.text(text_positon, text, font=font_headline, fill=(0, 0, 0))
    bk_img = np.array(img_pil)
    cv2.imwrite("add_text_1.jpg", bk_img)
