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
import time


def get_font_size(coordinate_proportion, text, bg_width, bg_height, font_path, draw, multi_line, bg_useful_space,
                  useful_space,
                  font_spacing_proportion=constants.FONT_SPACING_PROPORTION, interval=10, ):
    """

    :param coordinate_proportion: 比例坐标
    :param multi_line: 判断是否换行 TRUE:多行，FALSE：单行
    :param font_path: 字号的文件地址
    :param text: 文字信息
    :param font_spacing_proportion: 行间距
    :return: font_size 间隔为30
    """

    true_width = bg_width * (bg_useful_space[1] - bg_useful_space[0]) / (useful_space[1] - useful_space[0]) * (
            coordinate_proportion[1] - coordinate_proportion[0])
    font_size = 0
    if multi_line:
        text_list = text.split("\n")
        line_num = len(text_list)
        true_height = bg_height * (bg_useful_space[3] - bg_useful_space[2]) / (useful_space[3] - useful_space[2]) * (
                coordinate_proportion[3] - coordinate_proportion[2]) / line_num
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
def write_on_pic(coordinate_list, bg_img, useful_space, text_in,
                 template_shape, font_dic, bg_img_id, map_code):
    img_pil = Image.fromarray(bg_img)
    draw = ImageDraw.Draw(img_pil)

    # 背景图信息处理
    bg_width = bg_img.shape[1]
    bg_height = bg_img.shape[0]
    bg_data = json.load(open(constants.BG_IMG_INFO_PATH, "r"))[bg_img_id]

    # 选择色板：
    if text_in["color_palettes"] == 'color_palettes':
        # color palettes
        palettes = bg_data['palettes']
        mapped_value_list = [palettes[int(_) - 1] for _ in bg_data["mapped"]]
        for _ in mapped_value_list:
            palettes.remove(_)
    elif text_in["color_palettes"] == 'adjacent_color_theory':
        # adjacent_color_theory：
        palettes = [bg_data['adjacent_color_theory']]
    elif text_in["color_palettes"] == 'contrast_color_theory':
        palettes = [bg_data['contrast_color_theory']]

    for _ in coordinate_list:
        key = list(_.keys())[0]
        coordinate_proportion = _[key]
        text = text_in[key]
        text_num = len(text)

        # 背景图的信息获取
        bg_useful_space = bg_data["useful_space"]

        # 随机数取颜色
        random_num = np.random.randint(len(palettes))
        colour = palettes[random_num]

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
            font_size = get_font_size(coordinate_proportion, text, bg_width, bg_height, font_path, draw,
                                      multi_line=False, font_spacing_proportion=constants.FONT_SPACING_PROPORTION,
                                      bg_useful_space=bg_useful_space, useful_space=useful_space)
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
                text_position = (bg_width / 2 - sum_font_width / 2, coordinate_proportion[
                    2] * bg_height + line_num * font_size * (1 + constants.FONT_SPACING_PROPORTION))

                # 绘制文字信息
                draw.text(text_position, _, font=font, fill=(colour[0], colour[1], colour[2]))
                line_num += 1

        else:
            # 计算文字大小
            font_size = get_font_size(coordinate_proportion, text, bg_width, bg_height, font_path, draw,
                                      multi_line=False, interval=10, bg_useful_space=bg_useful_space,
                                      useful_space=useful_space)
            font = ImageFont.truetype(font_path, font_size)

            # 字宽
            sum_font_width = 0
            sum_font_height = 0
            for char in text:
                width, height = draw.textsize(char, font)
                sum_font_width += width
                sum_font_height = height

            # 文字位置，暂时全部居中处理
            # text_position = (bg_width / 2 - sum_font_width / 2, coordinate_proportion[2] * bg_height)
            text_position = (bg_width * (
                    (coordinate_proportion[0] - useful_space[0]) / (useful_space[1] - useful_space[0]) * (
                    bg_useful_space[1] - bg_useful_space[0]) + bg_useful_space[0]), bg_height * (
                                     (coordinate_proportion[2] - useful_space[2]) / (
                                     useful_space[3] - useful_space[2]) * (
                                             bg_useful_space[3] - bg_useful_space[2]) + bg_useful_space[2]))

            # 绘制文字信息
            draw.text(text_position, text, font=font, fill=(colour[0], colour[1], colour[2]))

    bg_img = np.array(img_pil)
    bg_img = Image.fromarray(cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB))
    return bg_img.resize((500, int((bg_img.height / bg_img.width) * 500)))


def generate(mapped_id_list, text_in, map_code):
    data = json.load(open(constants.TEMPLATE_JSON_PATH, "r"))
    bg_img_id = text_in["background_id"]
    bg_path = os.path.join(constants.BG_IMG_PATH, bg_img_id + ".jpg")
    bg_img = cv2.imread(bg_path)

    # 每行放3个
    mapped_pic_num = len(mapped_id_list)
    coloumn = 3
    interval_px = 100
    bg_img_width = 500
    bg_img_height = 800
    if mapped_pic_num % 3 == 0:
        row = mapped_pic_num / 3
    else:
        row = mapped_pic_num / 3 + 1

    canvas = Image.new("RGB",
                       (int(coloumn * bg_img_width + interval_px * (coloumn + 1)),
                        int(row * 800 + interval_px * (row + 1))), (255, 255, 255))

    for counts, _ in enumerate(mapped_id_list):
        coordinate_list = data[_]["element_coordinate_list"]
        useful_space = data[_]["useful_space"]
        template_shape = data[_]["shape"]
        colour_dic = data[_]["element_font_colour"]
        font_dic = data[_]["element_font"]
        img = write_on_pic(coordinate_list=coordinate_list,
                           bg_img=bg_img,
                           useful_space=useful_space,
                           text_in=text_in,
                           template_shape=template_shape,
                           font_dic=font_dic,
                           bg_img_id=bg_img_id,
                           map_code=map_code,
                           )

        position = (int(100 + counts % 3 * (bg_img_width + interval_px)),
                    int(100 + counts // 3 * (bg_img_height + interval_px)))
        canvas.paste(img, position)

    def save_img():
        count = 0
        save_name = bg_img_id + "_" + str(map_code) + "_" + str(count)
        while os.path.exists(os.path.join(constants.OUT_PUT_PATH, save_name + ".jpg")):
            save_name = bg_img_id + "_" + str(map_code) + "_" + str(count)
            count += 1
        canvas.save(os.path.join(constants.OUT_PUT_PATH, save_name + ".jpg"))
        return save_name

    def generate_log(save_name, map_code, text_in):
        try:
            log = json.load(open(constants.GENERATION_LOG_PATH, "r"))
        except:
            log = {}

        new_dic = {}
        new_dic["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        new_dic["map_code"] = map_code
        new_dic["text_in"] = text_in
        new_dic["log"] = input.log_

        log[save_name] = new_dic
        json.dump(log, open(constants.GENERATION_LOG_PATH, "w"), indent=4, ensure_ascii=False)

    save_name = save_img()
    generate_log(save_name, map_code, text_in)


if __name__ == "__main__":
    mapped_id_list, map_code = get_map_code_list()
    generate(mapped_id_list=mapped_id_list,
             text_in=input.text_in,
             map_code=map_code)
