# -*- coding:utf-8 -*-
import pandas as pd
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import matplotlib.pyplot as plt
from core import constants
import requests
import os
from io import BytesIO
from PIL import Image
import cv2
import json
import input
from collections import Counter
from core.utils import get_map_code_list


def get_font_size(coordinate_proportion, text, bk_width, bk_height, font_path, draw, multi_line,
                  font_spacing_proportion=constants.FONT_SPACING_PROPORTION, interval=10):
    """

    :param coordinate_proportion: 比例坐标
    :param multi_line: 判断是否换行 TRUE:多行，FALSE：单行
    :param font_path: 字号的文件地址
    :param text: 文字信息
    :param font_spacing_proportion: 行间距
    :return: font_size 间隔为30
    """

    true_width = bk_width * (coordinate_proportion[1] - coordinate_proportion[0])
    font_size = 0
    if multi_line:
        text_list = text.split("\n")
        line_num = len(text_list)
        true_height = bk_height * (coordinate_proportion[3] - coordinate_proportion[1]) / line_num
        while True:
            sum_font_height = 0
            font_size += interval
            sum_font_height += font_size * font_spacing_proportion * (line_num - 1)
            font = ImageFont.truetype(font_path, font_size)
            width, height = draw.textsize(text_list[0], font)
            sum_font_height += height
            if sum_font_height > true_height:
                return font_size
            else:
                sum_font_height -= font_size * font_spacing_proportion * (line_num - 1)
    else:
        while True:
            sum_font_width = 0
            font_size += interval
            font = ImageFont.truetype(font_path, font_size)
            for char in text:
                width, height = draw.textsize(char, font)
                sum_font_width += width
            if sum_font_width > true_width:
                return font_size


# todo usefulspace 还没用
def write_on_pic(coordinate_list, bk_img, useful_space, text_in,
                 template_shape, font_dic, colour_dic, bk_img_id, map_code):
    img_pil = Image.fromarray(bk_img)
    draw = ImageDraw.Draw(img_pil)
    bk_width = bk_img.shape[1]
    bk_height = bk_img.shape[0]

    for _ in coordinate_list:
        key = list(_.keys())[0]
        coordinate_proportion = _[key]
        text = text_in[key]
        text_num = len(text)

        try:
            colour_key = key + "_colour"
            colour = colour_dic[colour_key]
        except:
            colour = [100, 100, 100]
            if "background" in key:
                print("has _with_ground")
            # print("generate_backgound_info missing")

        try:
            font_key = key + "_font"
            font = font_dic[font_key]
        except:
            font = "Lanting Tehei Jian.TTF"
            # print("font missing")
        font_path = os.path.join(constants.FONT_PATH, font)

        # 判断是否换行 ，原则是要在框架内，换行则按照列的尺寸来定
        if "\n" in text:
            text_list = text.split("\n")
            # 计算文字大小
            font_size = get_font_size(coordinate_proportion, text, bk_width, bk_height, font_path, draw,
                                      multi_line=False, font_spacing_proportion=constants.FONT_SPACING_PROPORTION)
            font = ImageFont.truetype(font_path, font_size)

            line_num = 0
            for _ in text_list:
                # 字宽
                sum_font_width = 0
                sum_font_height = 0
                for char in _:
                    width, height = draw.textsize(char, font)
                    sum_font_width += width
                    sum_font_height = height

                # 文字位置，暂时全部居中处理 ,多行设置行间距
                text_position = (bk_width / 2 - sum_font_width / 2, coordinate_proportion[
                    2] * bk_height + line_num * font_size * (1 + constants.FONT_SPACING_PROPORTION))

                # 绘制文字信息
                draw.text(text_position, _, font=font, fill=(colour[0], colour[1], colour[2]))
                line_num += 1

        else:
            # 计算文字大小
            font_size = get_font_size(coordinate_proportion, text, bk_width, bk_height, font_path, draw,
                                      multi_line=False, interval=10)
            font = ImageFont.truetype(font_path, font_size)

            # 字宽
            sum_font_width = 0
            sum_font_height = 0
            for char in text:
                width, height = draw.textsize(char, font)
                sum_font_width += width
                sum_font_height = height

            # 文字位置，暂时全部居中处理
            # text_position = (bk_width / 2 - sum_font_width / 2, coordinate_proportion[2] * bk_height)
            text_position = (coordinate_proportion[0] * bk_width, coordinate_proportion[2] * bk_height)

            # 绘制文字信息
            draw.text(text_position, text, font=font, fill=(colour[0], colour[1], colour[2]))

    bk_img = np.array(img_pil)
    count = 0
    save_name = bk_img_id + "_" + str(map_code) + "_" + str(count)

    while os.path.exists(os.path.join(constants.OUT_PUT_PATH, save_name + ".jpg")):
        save_name = bk_img_id + "_" + str(map_code) + "_" + str(count)
        count += 1

    cv2.imwrite(os.path.join(constants.OUT_PUT_PATH, save_name + ".jpg"), bk_img)
    with open(os.path.join(constants.OUT_PUT_PATH, save_name + ".txt"), "w+") as e:
        e.writelines(str(text_in))


def generate(map_code_index_list, text_in, map_code):
    with open(constants.TEMPLATE_JSON_PATH, "r") as e:
        data = json.loads(e.read())
    for _ in map_code_index_list:
        template = data["template"][_]
        coordinate_list = template["element_coordinate_list"]
        bk_img_id = text_in["background_id"]
        bk_img = cv2.imread(os.path.join(constants.BG_IMG_PATH, bk_img_id))
        useful_space = template["useful_space"]
        template_shape = template["shape"]
        colour_dic = template["element_font_colour"]
        font_dic = template["element_font"]
        write_on_pic(coordinate_list=coordinate_list,
                     bk_img=bk_img,
                     useful_space=useful_space,
                     text_in=text_in,
                     template_shape=template_shape,
                     colour_dic=colour_dic,
                     font_dic=font_dic,
                     bk_img_id=bk_img_id,
                     map_code=map_code,
                     )


if __name__ == "__main__":
    map_code_index_list, map_code = get_map_code_list()
    generate(map_code_index_list=map_code_index_list,
             text_in=input.text_in,
             map_code=map_code)
