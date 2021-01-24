from core import generate
from core.utils import get_map_code_list
import input

map_code_index_list, map_code = get_map_code_list()
generate.generate(map_code_index_list=map_code_index_list,
                  text_in=input.text_in,
                  map_code=map_code)
