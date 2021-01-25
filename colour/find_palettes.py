import pandas as pd
import numpy as np
from colour import colour_constants
from colour.utils import functions_utils
import math


def hex_to_hsv(hex_):
    r = int(hex_[1:3], 16)
    g = int(hex_[3:5], 16)
    b = int(hex_[5:7], 16)
    h, s, v = functions_utils.rgb2hsv(r, g, b)
    return np.array([h, s, v])


def hex_to_rgb(_):
    r = int(_[1:3], 16)
    g = int(_[3:5], 16)
    b = int(_[5:7], 16)
    return (r, g, b)


def data_process(data_path=colour_constants.PALETTES_DATA_PATH):
    data = pd.read_csv(data_path, header=None)
    data.columns = ["1", "2", "3", "4", "5", "6", "7", "8", "saves"]
    data.drop([0], axis=0, inplace=True)
    data.fillna(axis=0, method='ffill', inplace=True)
    data.dropna(axis=0, inplace=True)
    colour_8 = data.iloc[:, :7]
    colour_in16th = colour_8.copy()
    colour_saves = data.iloc[:, 8].map(lambda x: int(x.strip("saves").strip(" ").replace(",", "")))
    for _ in range(colour_8.shape[0]):
        colour_8.iloc[_, :] = colour_8.iloc[_, :].apply(hex_to_hsv)

    return colour_8, colour_saves, colour_in16th


def calculate(colour_data, main_colour):
    for _ in range(colour_data.shape[0]):
        colour_data.iloc[_, :] = colour_data.iloc[_, :].apply(lambda x: functions_utils.HSVDistance(x, main_colour))
    return colour_data


def get_palettes(main_colour, num_counts=2):
    """

    :param main_colour: (rgb) 元祖
    :return: 色卡集合
    """
    h, s, v = functions_utils.rgb2hsv(main_colour[0], main_colour[1], main_colour[2])
    colour_in_hsv, colour_saves, colour_in16th = data_process()
    print(colour_in_hsv)
    colour_dis = calculate(colour_data=colour_in_hsv, main_colour=[h, s, v])

    def get_min_distance_index(num=num_counts, df=colour_dis):
        """

        :param num: 匹配时，拿聚类的前几作为匹配数据
        :param df: distance的pandas数据
        :return: 色号的index
        """
        value_list = []
        for _ in range(df.shape[0]):
            value = np.array(df.iloc[_, :].sort_values()[:num]).sum()
            value_list.append(value)
        index_ = value_list.index(max(value_list))
        return index_

    index = get_min_distance_index(num_counts)
    return set([hex_to_rgb(_) for _ in colour_in16th.iloc[index, :].tolist()])
    # calculate(colour_data=colour_in_16th)


if __name__ == "__main__":
    _ = get_palettes(main_colour=(19, 19, 234), num_counts=2)
    print(_)
