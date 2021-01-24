import pandas as pd
import numpy as np
from core import constants
import requests
import os
from io import BytesIO
from PIL import Image
import cv2
from collections import Counter
import json


def download_img(data_path=constants.DATA_PATH, save_path=constants.ORIGINAL_IMG_SAVE_PATH,
                 empty_labeled_num=1):
    downloaded_error_timeout_num = 0
    data_df = pd.read_csv(data_path)
    for i in np.arange(data_df.shape[0]):
        if data_df["Label"][i] == "{}":
            empty_labeled_num += 1
            continue
        else:
            url = data_df["Labeled Data"][i]
            id = data_df["DataRow ID"][i]
            img_name = id + ".jpg"
            if os.path.exists(os.path.join(save_path, img_name)):
                print("{}_downloaded exists".format(img_name))
                continue
            else:
                r = requests.get(url, timeout=10)
                f = BytesIO(r.content)
                img = Image.open(f)
                img = img.convert('RGB')
                path = os.path.join(save_path, img_name)
                img.save(path)
                print("{} downloaded".format(img_name))
    print("downloaded_error_timeout_num:{}".format(downloaded_error_timeout_num))
    print("empty_labeled_num:{}".format(empty_labeled_num))


def write_json(new_dic):
    if not os.path.exists(constants.TEMPLATE_JSON_PATH):
        with open(constants.TEMPLATE_JSON_PATH, "w+") as e:
            json.dump({"id_list": [], "map_code": [], "template": []}, e)

    with open(constants.TEMPLATE_JSON_PATH, "r") as f:
        initial_data = json.loads(f.read())

    if new_dic["id"] in initial_data["id_list"]:
        print("{} exists,write_json_continue".format(new_dic["id"]))
    else:
        with open(constants.TEMPLATE_JSON_PATH, "w+") as f:
            initial_data["id_list"].append(new_dic["id"])
            initial_data["map_code"].append(new_dic["map_code"])
            initial_data["template"].append(new_dic)
            json.dump(initial_data, f)


def generate_template_library():
    """
    模板：原图的id 原图尺寸 元素坐标 元素的字体色号 元素的匹配槽
    :return:
    """
    data = pd.read_csv(constants.DATA_PATH)
    for i in range(data.shape[0]):
        index_id = data["DataRow ID"][i]
        print("{} starts ".format(index_id))
        new_dic = {}
        img_path = os.path.join(constants.ORIGINAL_IMG_SAVE_PATH, index_id + ".jpg")
        img = cv2.imread(img_path)
        img_shape = img.shape
        img_height = img_shape[0]
        img_width = img_shape[1]

        element_coordinate_list = []
        element_font = {}
        element_font_colour = {}

        # 判断有没有数值
        if data["Label"][i] == "{}":
            continue

        for _ in np.arange(len(json.loads(data["Label"][i])["objects"])):
            if "bbox" in json.loads(data["Label"][i])["objects"][_]:
                dic_position = {}
                top = json.loads(data["Label"][i])["objects"][_]["bbox"]["top"]
                left = json.loads(data["Label"][i])["objects"][_]["bbox"]["left"]
                height = json.loads(data["Label"][i])["objects"][_]["bbox"]["height"]
                width = json.loads(data["Label"][i])["objects"][_]["bbox"]["width"]
                title = json.loads(data["Label"][i])["objects"][_]["title"]
                x1 = left / img_width,
                x2 = (left + width) / img_width,
                y1 = top / img_height,
                y2 = (top + height) / img_height
                dic_position[title] = (x1[0], x2[0], y1[0], y2)
                element_coordinate_list.append(dic_position)
            if "point" in json.loads(data["Label"][i])["objects"][_]:
                position_x = json.loads(data["Label"][i])["objects"][_]["point"]["x"]
                position_y = json.loads(data["Label"][i])["objects"][_]["point"]["y"]
                colour = img[position_y, position_x]
                title = json.loads(data["Label"][i])["objects"][_]["title"]
                element_font_colour[title] = colour.tolist()
        for _ in np.arange(len(json.loads(data["Label"][i])["classifications"])):
            title = json.loads(data["Label"][i])["classifications"][_]["title"]
            font = json.loads(data["Label"][i])["classifications"][_]["answer"]["title"]
            element_font[title] = font

        # 找到space_useful
        for index, _ in enumerate(element_coordinate_list):
            if "space_useful" in _.keys():
                space_useful_index = index
                img_useful_space = element_coordinate_list[space_useful_index]["space_useful"]
                element_coordinate_list.pop(space_useful_index)
        else:
            img_useful_space = [0, 1.0, 0, 1.0]

        # map_code
        # ["headline", "subtitle", "chart_title", "chart_num", "text", "image"]
        element_list = [key for i in element_coordinate_list for key, value in i.items()]
        num_dic = Counter(element_list)
        map_code = ""
        for _ in constants.MAP_CODE_ELEMENT_LIST:
            num = num_dic[_]
            map_code += str(num)

        # load context
        new_dic["id"] = index_id
        new_dic["map_code"] = map_code
        new_dic["shape"] = (img_shape[1], img_shape[0])
        new_dic["useful_space"] = img_useful_space
        new_dic["element_coordinate_list"] = element_coordinate_list
        new_dic["element_font_colour"] = element_font_colour
        new_dic["element_font"] = element_font
        # print(element_coordinate_list, element_font_colour)
        # print(element_font)
        # print(new_dic)
        write_json(new_dic)


def pipeline():
    download_img()
    generate_template_library()


if __name__ == "__main__":
    pipeline()
