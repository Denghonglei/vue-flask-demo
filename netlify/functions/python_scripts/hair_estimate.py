import sys
import json

import math


def validate_dict(d):
    # 将字典的键转换为整数类型并排序
    sorted_keys = sorted(map(int, d.keys()))
    values = [float(d[str(key)]) for key in sorted_keys]
    # 检查值是否随着键的增大而减小或相等
    return all(values[i] >= values[i + 1] for i in range(len(values) - 1))


def convert_details(details):
    result = {}
    for item in details:
        result[item['length']] = item['girth']
    return result


def convert_result_dict(result_dict):
    arr = []
    for key, value in result_dict.items():
        obj = dict()
        obj['length'] = key
        obj['weight'] = value[0]
        obj['price'] = value[-1]
        arr.append(obj)
    return arr


def calculate_mass_by_length_and_thickness(length, items, is_dyed=False, method='1'):
    new_dict = {}
    data = {}
    total = 0
    for key in items.keys():
        new_key = float(key)
        new_value = float(items[key])
        new_dict[new_key] = new_value
    last_key, last_value = 0, 0  # value是横截面面积
    sort_keys = sorted([key for key in new_dict.keys()], reverse=True)  # key值从大到小
    first_key, final_key = sort_keys[0], sort_keys[-1]
    if method == 'OneCut' or method == '1' or method == '一刀剪':
        for key in sort_keys:
            if key == first_key:
                last_value = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                current_weight = last_value * ((length - 5 + int(key)) / 2)
                data[key] = int(current_weight)
                total += current_weight
                last_key = key

            else:
                current_area = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                current_weight = (current_area - last_value) * (last_key + key) / 2
                data[key] = int(current_weight)
                total += current_weight
                last_value, last_key = current_area, key
    elif method == 'Scissors' or method == '2' or method == '抽剪':
        # 当method为2时，输出dict的key值加5，去掉最后一个key的重量
        for key in sort_keys:
            if key == first_key:
                last_value = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                current_weight = last_value * ((length + 5 + int(key)) / 2)
                data[key + 5] = int(current_weight)
                total += current_weight
                last_key = key
            elif key == final_key:
                pass
            else:
                current_area = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                current_weight = (current_area - last_value) * (last_key + 5 + key) / 2
                data[key + 5] = int(current_weight)
                total += current_weight
                last_value, last_key = current_area, key
        pass
    if is_dyed:
        total = total * 0.9
    return int(total), data


def get_price_by_details(dict1, dict2=None, is_dyed=False):
    if not dict2:
        dict2 = {
            0: 0.5,
            20: 0.6,
            25: 0.8,
            30: 1.5,
            35: 2,
            40: 2.5,
            45: 3,
            50: 5,
            55: 5.5,
            60: 6,
            65: 6.5,
            70: 7,
            75: 7.5,
            80: 8,
            85: 8.5
        }
    if is_dyed == True:
        for key, value in dict2.items():
            dict2[key] = value * 0.7

    result_dict = {}
    result_sum = 0
    max_dict2_key = max(dict2.keys())
    for key in dict1:
        value1 = dict1[key]
        if key in dict2:
            value2 = dict2[key]
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                result_dict[key] = [value1, value2, round(value1 * value2, 1)]
                result_sum += round(value1 * value2, 1)
        elif key > max_dict2_key:
            value2 = dict2[max_dict2_key]
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                result_dict[key] = [value1, value2, round(value1 * value2, 1)]
                result_sum += round(value1 * value2, 1)

    return {'total': result_sum, 'details': result_dict}


def calculate_sum(dict1, dict2):
    result = 0
    max_key_in_dict1 = max(dict1.keys()) if dict1 else None
    for key in dict2:
        if key in dict1:
            result += dict1[key] * dict2[key]
        elif max_key_in_dict1 is not None and key > max_key_in_dict1:
            result += dict2[key] * dict1[max_key_in_dict1]
    return result


import json


def json_str_to_dict(input_data):
    """
    将 JSON 字符串转换为字典，非 JSON 字符串则返回原数据
    :param input_data: 任意输入（可能是 JSON 字符串/字典/其他类型）
    :return: 解析后的字典 | 原输入数据
    :raises: 仅在明确是 JSON 格式但解析失败时抛出异常（可选关闭）
    """
    # 第一步：判断输入是否为字符串类型（非字符串直接返回）
    if not isinstance(input_data, str):
        return input_data

    # 第二步：去除字符串两端空白（处理 "\n  {\"key\":123}  " 这类情况）
    clean_str = input_data.strip()

    # 第三步：判断是否为 JSON 格式（以 {/[ 开头，以 }/] 结尾）
    if not (clean_str.startswith(('{', '[')) and clean_str.endswith(('}', ']'))):
        return input_data

    # 第四步：尝试解析 JSON 字符串为字典/列表
    try:
        parsed_data = json.loads(clean_str)
        # 若解析结果是列表，可根据需求转为字典（如 {"data": 列表}），或直接返回
        # 这里选择直接返回（如需强制转字典，可取消下面注释）
        # if isinstance(parsed_data, list):
        #     return {"data": parsed_data}
        return parsed_data
    except json.JSONDecodeError as e:
        # 解析失败：打印调试信息，返回原字符串（也可选择抛出异常）
        print(f"[警告] JSON 解析失败：{e} | 原始数据：{input_data[:100]}")
        # 若需要严格模式（解析失败直接报错），取消下面注释
        # raise ValueError(f"无效的 JSON 字符串：{e}") from e
        return input_data


# ---------------  驼峰/下划线互转公共工具  ---------------
import re


def camel_to_snake(name):
    """驼峰命名转下划线命名：isDyed → is_dyed"""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name):
    """下划线命名转驼峰命名：is_dyed → isDyed"""
    parts = name.split('_')
    return parts[0] + ''.join(part.title() for part in parts[1:])


def convert_dict_keys(data, convert_func):
    """递归转换字典的所有键名（支持嵌套字典/列表）
    :param data: 要转换的数据（字典/列表/其他类型）
    :param convert_func: 键名转换函数（camel_to_snake 或 snake_to_camel）
    """
    if isinstance(data, dict):
        return {
            convert_func(key) if isinstance(key, str) else key:
                convert_dict_keys(value, convert_func)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_dict_keys(item, convert_func) for item in data]
    else:
        return data


# --------------------------------------------------------


def main(params):
    """业务逻辑：头发健康评估"""
    params = json_str_to_dict(params)
    # 【统一转换入参】把前端传的驼峰键转成下划线（isDyed → is_dyed）
    params = convert_dict_keys(params, camel_to_snake)

    length = int(params.get('length'))
    girth = float(params.get('thickness'))
    if girth > 18 or length > 200:
        result = {'code': 400, 'msg': '请输入正确的参数'}
        # 【统一转换出参】把返回的下划线键转成驼峰返回给前端
        return convert_dict_keys(result, snake_to_camel)
    method = params.get('method', '2')
    is_dyed = params.get('is_dyed', False)
    details = params.get('details')
    details['0'] = girth
    if not validate_dict(details):
        result = {'code': 400, 'msg': '围度从上到下呈递减趋势'}
        return convert_dict_keys(result, snake_to_camel)
    result, result_data = calculate_mass_by_length_and_thickness(length, details, is_dyed=is_dyed,
                                                                 method=method)
    result_dict = get_price_by_details(dict1=result_data, is_dyed=is_dyed)
    result_dict['weight'] = result
    # 把估价历史存入数据库：

    # 【统一转换出参】下划线转驼峰返回
    return convert_dict_keys(result_dict, snake_to_camel)


if __name__ == '__main__':
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "length": 50,
        "thickness": 8.8,
        "method": "一刀剪",
        "is_dyed": False,
        "details": {
            "30": 6,
            "40": 5
        }
    }
    result = main(params)
    print(json.dumps(result, ensure_ascii=False))
