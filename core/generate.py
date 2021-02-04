# -*- coding:utf-8 -*-
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from core import constants
import os
from PIL import Image
import json
import input
from core.utils import get_map_code_list
import time
from core import get_palettes


def get_font_size(coordinate_proportion, text, bg_width, bg_height, font_path, draw, multi_line, bg_useful_space,
                  useful_space, font_spacing_proportion=constants.FONT_SPACING_PROPORTION, interval=10, ):
    """

    :param coordinate_proportion: 比例坐标
    :param multi_line: 判断是否换行 TRUE:多行，FALSE：单行
    :param font_path: 字号的文件地址
    :param text: 文字信息
    :param font_spacing_proportion: 行间距
    :param interval:每次加10像素
    :return: font_size 间隔为30
    """

    true_width = bg_width * (bg_useful_space[1] - bg_useful_space[0]) / (useful_space[1] - useful_space[0]) * (
            coordinate_proportion[1] - coordinate_proportion[0])
    true_height = bg_height * (bg_useful_space[3] - bg_useful_space[2]) / (useful_space[3] - useful_space[2]) * (
            coordinate_proportion[3] - coordinate_proportion[2])
    # 网格对齐会出问题
    font_size = 0
    if multi_line:
        text_list = text.split("\n")
        line_num = len(text_list)
        true_height = true_height / line_num

        while True:
            sum_font_height = 0
            font_size += interval
            sum_font_height += font_size * font_spacing_proportion * (line_num - 1)
            font = ImageFont.truetype(font_path, font_size)
            width, height = draw.textsize(text_list[0], font)
            sum_font_height += height
            text_list = text.split('\n')

            width_list = []
            for _ in range(len(text_list)):
                text_line_one_width, height = draw.textsize(text.split('\n')[_], font=font)
                width_list.append(text_line_one_width)
            text_line_one_width = np.array(width_list).max()

            if sum_font_height > true_height or text_line_one_width > true_width:
                return font_size
            else:
                sum_font_height -= font_size * font_spacing_proportion * (line_num - 1)
    else:

        while True:
            font_size += interval
            font = ImageFont.truetype(font_path, font_size)
            sum_font_width, height = draw.textsize(text, font)
            if sum_font_width > true_width or height > true_height:
                return font_size


def get_true_position(coordinate_proportion, useful_space, bg_useful_space):
    return (np.array(coordinate_proportion) - np.array(useful_space) + np.array(bg_useful_space)).tolist()


def write_on_pic(coordinate_list, text_in, bg_img_id):
    if bg_img_id == "created":
        color_palettes_dic = get_palettes.get_color_dic()
        img_pil = Image.new("RGB", size=text_in['setting']['bg_size'], color=color_palettes_dic['bg_color'])

        bg_useful_space = text_in['setting']["useful_space"]
        bg_width = text_in['setting']['bg_size'][0]
        bg_height = text_in['setting']['bg_size'][1]
        white_bg_proportion = text_in['setting']['white_bg_proportion']
    else:
        bg_path = os.path.join(constants.BG_IMG_PATH, bg_img_id + ".jpg")
        img_pil = Image.open(bg_path)
        # 背景图信息处理
        bg_width = img_pil.width
        bg_height = img_pil.height
        bg_data = json.load(open(constants.BG_IMG_INFO_PATH, "r"))[bg_img_id]
        bg_useful_space = bg_data["useful_space"]

        # 选择色板：
        color_setting = text_in['setting']["color_palettes"]
        if color_setting == 'color_palettes':
            # color palettes
            palettes = bg_data['palettes']
            mapped_value_list = [palettes[int(_) - 1] for _ in bg_data["mapped"]]
            for _ in mapped_value_list:
                palettes.remove(_)
        elif color_setting == 'adjacent_color_theory':
            # adjacent_color_theory：
            palettes = [bg_data['adjacent_color_theory']]
        elif color_setting == 'contrast_color_theory':
            palettes = [bg_data['contrast_color_theory']]
        # 随机数取颜色
        colour = palettes[np.random.randint(len(palettes))]

    draw = ImageDraw.Draw(img_pil)

    # write template coordinate data in a dic
    coordinate_proportion_dic = {
        "headline": [],
        "subtitle": [],
        "chart_num": [],
        'chart_title': [],
        'text': [],
        'rectangle_element': [],
        'line_element': [],
        'useful_space': [],
    }
    for _ in coordinate_list:
        key = list(_.keys())[0]
        coordinate_proportion_dic[key].append(_[key])
    try:
        useful_space = coordinate_proportion_dic['useful_space'][0]
    except:
        useful_space = [0, 1, 0, 1]

    # draw background element
    draw.rectangle([bg_width * white_bg_proportion, bg_height * white_bg_proportion,
                    bg_width * (1 - white_bg_proportion), bg_height * (1 - white_bg_proportion)],
                   fill=color_palettes_dic['square_element'], width=0, outline=None)
    if not [] == coordinate_proportion_dic['rectangle_element']:
        for _ in coordinate_proportion_dic['rectangle_element']:
            true_coordinate = get_true_position(_, useful_space, bg_useful_space)
            draw.rectangle(
                [true_coordinate[0] * bg_width, true_coordinate[2] * bg_height, true_coordinate[1] * bg_width,
                 true_coordinate[3] * bg_height],
                fill=color_palettes_dic['rectangle_element'], width=0, outline=None)
    if not [] == coordinate_proportion_dic['line_element']:
        for _ in coordinate_proportion_dic['line_element']:
            true_coordinate = get_true_position(_, useful_space, bg_useful_space)
            draw.rectangle(
                [true_coordinate[0] * bg_width, true_coordinate[2] * bg_height, true_coordinate[1] * bg_width,
                 true_coordinate[3] * bg_height],
                fill=color_palettes_dic['line_element'], width=0, outline=None)

    # 添加texture：
    texture_path = os.path.join(constants.TEXTURE_PATH, text_in['setting']['texture'])
    texture_img = Image.open(texture_path).resize(text_in['setting']['bg_size'])
    r, g, b, a = texture_img.split()
    img_pil.paste(texture_img, [0, 0, text_in['setting']['bg_size'][0], text_in['setting']['bg_size'][1]], mask=a)

    # write characters
    for key, value in text_in['writing'].items():
        # 字体
        font = text_in['font'][key]
        font_path = os.path.join(constants.FONT_PATH, font)
        for _ in range(len(value)):
            text = value[_]
            multi_line = '\n' in text
            # get font size
            coordinate_proportion = coordinate_proportion_dic[key][_]
            font_size = get_font_size(coordinate_proportion, text, bg_width, bg_height, font_path,
                                      draw,
                                      multi_line=multi_line, interval=10,
                                      bg_useful_space=bg_useful_space,
                                      useful_space=useful_space)
            font = ImageFont.truetype(font_path, font_size)
            if multi_line:
                text_list = text.split('\n')
                width_list = []
                for _ in range(len(text_list)):
                    text_line_one_width, height = draw.textsize(text.split('\n')[_], font=font)
                    width_list.append(text_line_one_width)
                text_line_one_width = np.array(width_list).max()
            else:
                text_line_one_width, height = draw.textsize(text, font=font)

            x = bg_width * (
                    (coordinate_proportion[0] - useful_space[0]) / (useful_space[1] - useful_space[0]) * (
                    bg_useful_space[1] - bg_useful_space[0]) + bg_useful_space[0]) + bg_width * (
                        coordinate_proportion[1] - coordinate_proportion[0]) * (
                        bg_useful_space[1] - bg_useful_space[0]) / (
                        useful_space[1] - useful_space[0]) / 2 - text_line_one_width / 2
            y = bg_height * (
                    (coordinate_proportion[2] - useful_space[2]) / (
                    useful_space[3] - useful_space[2]) * (
                            bg_useful_space[3] - bg_useful_space[2]) + bg_useful_space[2])
            text_position = (x, y)

            # 绘制文字信息
            draw.text(text_position, text, font=font, align='center', fill=color_palettes_dic[key])

    return img_pil.resize((500, int((img_pil.height / img_pil.width) * 500)))


def generate(mapped_id_list, text_in, map_code):
    data = json.load(open(constants.TEMPLATE_JSON_PATH, "r"))

    # 每行放3个

    mapped_pic_num = len(mapped_id_list)
    if text_in['setting']['background_id'] == 'created':
        # 多生成几个
        mapped_pic_num = mapped_pic_num * 9
        mapped_id_list = mapped_id_list * 9
    column = 3
    interval_px = 100
    bg_img_width = 500
    bg_img_height = 800
    if mapped_pic_num % 3 == 0:
        row = mapped_pic_num / 3
    else:
        row = mapped_pic_num / 3 + 1

    canvas = Image.new("RGB",
                       (int(column * bg_img_width + interval_px * (column + 1)),
                        int(row * 800 + interval_px * (row + 1))), (255, 255, 255))

    bg_img_id = text_in['setting']["background_id"]

    for counts, _ in enumerate(mapped_id_list):
        coordinate_list = data[_]["element_coordinate_list"]
        img = write_on_pic(coordinate_list=coordinate_list,
                           text_in=text_in,
                           bg_img_id=bg_img_id,
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
        print(save_name)
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
