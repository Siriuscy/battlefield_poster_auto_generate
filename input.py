text_in = {
    'writing':
        {"headline": ["双十一战报"],
         "subtitle": ["—截止11月11日23：59—"],
         "chart_num": ["10000件"],
         'chart_title': ["本店销售总量突破"],
         'text': ["双11就是干", "感谢每一个奋斗在前线\n员工，你们是最棒de人"],
         # 'text': ["感谢每一个奋斗在前线员工，你们是最棒de人"],
         },
    'setting':
        {"background_id": "created",
         "color_palettes": "color_palettes",
         'bg_size': (3543, 4724),
         'useful_space': [0.1, 0.9, 0.05, 0.95],
         'created_get_color_palettes': {
             'method': 'method_one',
             'threshold': (1.6, 1.7)
         },
         'texture': 'texture_1.png',
         'white_bg_proportion': 0.05

         },
    'font': {
        'headline': 'Pangmenzhengdao.ttf',
        'subtitle': 'ZhanKuKuHei-1.ttf',
        'chart_num': 'Youshebiaotihei.ttf',
        'chart_title': 'NotoSansCJKsc-Black.ttf',
        'text': 'NotoSansCJKsc-Black.ttf',

    }

}
'''
about setting:
writing:["headline", "subtitle", "chart_title", "chart_num", "text", "image"]
setting:
'background_id':bg_id or 'created'
'color_palettes':adjacent_color_theory,contrast_color_theory,color_palettes,
if bg is created:
    bg_size:size
    useful_space:useful_space
    color:bg color
    font:font
    created_get_color_palettes:
        method_one:sort_value by saturation + value choose low value to be background and high
        value to be the color of font,and dont use high saturation and value(del value > threshold)
        
'''

# 日志
log_ = {}
log_['color_palettes'] = text_in['setting']['color_palettes']
log_["log_2/1"] = "把横纵坐标保留一位小数，相当于用网格切分了"
log_["log_2/1_1"] = "临近色 色彩理论 +(30),保留明度和饱和度"
log_["log_2/1_2"] = "用了useful_space,第一次调优"
log_["log_2/1_3"] = "align=centre"
log_["log_2/3_1"] = "用的0203test数据集，增加了101120的map_code编码"
log_["log_2/3_2"] = '对于x轴，划分为10等分，对于y轴保留小数点，'
log_["log_2/3_3"] = '更正了颜色问题，'
