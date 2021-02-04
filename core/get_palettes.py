import pandas as pd
import numpy as np
from generate_background_info.utils import functions_utils
import icecream
import input

data_path = './generate_background_info/original_palettes_dataset/trending_color_palettes.csv'


def get_color_dic(
        data_path=data_path):
    '''

    :param data_path: 输入原始数据，
    :return: colour_hsv：hsv，colour_saves：喜爱度，colour_rgb：rgb的数据，
    以上均为pandas数据
    '''

    data = pd.read_csv(data_path, header=None)
    data.columns = ["1", "2", "3", "4", "5", "6", "7", "8", "saves"]
    data.drop([0], axis=0, inplace=True)
    data.fillna(axis=0, method='ffill', inplace=True)
    data.dropna(axis=0, inplace=True)
    colour_16th = data.iloc[:, :7]

    colour_rgb = colour_16th.copy()
    colour_hsv = colour_16th.copy()
    colour_saves = data.iloc[:, 8].map(lambda x: int(x.strip("saves").strip(" ").replace(",", "")))

    for _ in range(colour_hsv.shape[0]):
        colour_hsv.iloc[_, :] = colour_hsv.iloc[_, :].apply(functions_utils.hex_to_hsv)
    for _ in range(colour_rgb.shape[0]):
        colour_rgb.iloc[_, :] = colour_rgb.iloc[_, :].apply(functions_utils.hex_to_rgb)

    if input.text_in['setting']['created_get_color_palettes']['method'] == 'method_one':
        while True:
            random_num = np.random.randint(0, colour_hsv.shape[0])
            palettes = colour_hsv.iloc[random_num, :]
            df = pd.DataFrame(palettes)
            df.columns = ['hsv']
            df['hue'] = df['hsv'].apply(lambda x: x[0])
            df['saturation'] = df['hsv'].apply(lambda x: x[1])
            df['value'] = df['hsv'].apply(lambda x: x[2])
            df['sv'] = df['hsv'].apply(lambda x: x[1] + x[2])
            df['rgb'] = df['hsv'].apply(lambda x: functions_utils.hsv2rgb(x[0], x[1], x[2]))
            df.drop_duplicates('hue', 'first', inplace=True)

            if input.text_in['setting']['created_get_color_palettes']['threshold'][0] < df.sort_values('sv')[
                'sv'].mean() < \
                    input.text_in['setting']['created_get_color_palettes']['threshold'][1]:
                df.sort_values('sv', inplace=True)
                color_dic = {
                    "headline": tuple(df.iloc[-1, 5]),
                    "subtitle": tuple(df.iloc[-2, 5]),
                    "chart_num": tuple(df.iloc[-1, 5]),
                    'chart_title': tuple(df.iloc[-2, 5]),
                    'text': tuple(df.iloc[-3, 5]),
                    'rectangle_element': tuple(df.iloc[1, 5]),
                    'line_element': tuple(df.iloc[1, 5]),
                    'bg_color': tuple(df.iloc[0, 5]),
                    'square_element':(255,255,255)
                }
                return color_dic


if __name__ == '__main__':
    icecream.ic(get_color_dic())
