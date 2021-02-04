from core import constants
from collections import Counter
import json
import pandas as pd
import input


def get_map_code_list():
    """
    in:input.py
    :return: map_code_index
    """
    # 计算map_code
    content = input.text_in['writing']
    map_code = ""
    for _ in constants.MAP_CODE_ELEMENT_LIST:
        try:
            num = len(content[_])
            map_code += str(num)
        except KeyError:
            map_code += str(0)
    print(map_code)
    template = json.load(open(constants.TEMPLATE_JSON_PATH, "r"))

    mapped_id_list = []
    for _ in template:
        if template[_]["map_code"] == map_code:
            mapped_id_list.append(_)

    return mapped_id_list, map_code




if __name__ == "__main__":
    _, a = get_map_code_list()
    print(_)
