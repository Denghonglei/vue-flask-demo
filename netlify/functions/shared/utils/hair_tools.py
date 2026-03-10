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
                current_weight = last_value * ((length -5 + int(key)) / 2)
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
        for key,value in dict2.items():
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

