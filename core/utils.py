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
    key_list = []
    value_list = []
    content = input.text_in
    print(content)
    for key, value in content.items():
        key_list.append(key)
        value_list.append(value)

    num_dic = Counter(key_list)

    map_code = ""
    for _ in constants.MAP_CODE_ELEMENT_LIST:
        num = num_dic[_]
        map_code += str(num)

    with open(constants.TEMPLATE_JSON_PATH, "r") as e:
        template = json.loads(e.read())

    index = pd.Series(template["map_code"])
    map_index_list = index[index.values == map_code].index.tolist()
    return map_index_list, map_code
