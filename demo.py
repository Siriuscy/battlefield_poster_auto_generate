from core import generate
from core.utils import get_map_code_list
import input

mapped_id_list, map_code = get_map_code_list()
generate.generate(mapped_id_list=mapped_id_list,
                  text_in=input.text_in,
                  map_code=map_code)
