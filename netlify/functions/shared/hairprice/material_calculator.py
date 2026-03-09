import math


class MaterialCalculator:
    """材料重量和价格计算器"""

    def __init__(self, price_config=None, is_dyed=False):
        """
        初始化计算器

        Args:
            length: 长度
            girth： 围度——一圈的周长
            price_config: 价格配置字典
            is_dyed: 是否染色
        """
        self.is_dyed = is_dyed
        self.price_config = price_config or {
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

        # 如果是染色材料，调整价格配置
        if self.is_dyed:
            self.price_config = {k: v * 0.7 for k, v in self.price_config.items()}

    @staticmethod
    def validate_dict(d):
        """
        验证字典是否满足值随键增大而减小的条件

        Args:
            d: 待验证的字典

        Returns:
            验证结果，True或False
        """
        sorted_keys = sorted(map(int, d.keys()))
        values = [float(d[str(key)]) for key in sorted_keys]
        return all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    @staticmethod
    def convert_details(details):
        """
        将详情列表转换为字典

        Args:
            details: 详情列表，每个元素是包含length和girth的字典

        Returns:
            转换后的字典
        """
        result = {}
        for item in details:
            result[item['length']] = item['girth']
        return result

    @staticmethod
    def convert_result_dict(result_dict):
        """
        将结果字典转换为对象列表

        Args:
            result_dict: 结果字典

        Returns:
            对象列表，每个对象包含length、weight和price属性
        """
        arr = []
        for key, value in result_dict.items():
            obj = {
                'length': key,
                'weight': value[0],
                'price': value[-1]
            }
            arr.append(obj)
        return arr

    def calculate_mass_by_length_and_thickness(self, length, items, method='1'):
        """
        根据长度和厚度计算质量

        Args:
            length: 长度
            items: 包含厚度和周长信息的字典
            method: 计算方法，'1' 或 '2'

        Returns:
            总质量和详细计算结果
        """
        # 转换并排序输入数据
        new_dict = {float(key): float(value) for key, value in items.items()}
        sort_keys = sorted(new_dict.keys(), reverse=True)
        first_key, final_key = sort_keys[0], sort_keys[-1]

        data = {}
        total = 0
        last_key, last_value = 0, 0

        if method in ('OneCut', '1', '一刀剪'):
            # 一刀剪算法
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
        elif method in ('Scissors', '2', '抽剪'):
            # 抽剪算法
            for key in sort_keys:
                if key == first_key:
                    last_value = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                    current_weight = last_value * ((length + 5 + int(key)) / 2)
                    data[key + 5] = int(current_weight)
                    total += current_weight
                    last_key = key
                elif key == final_key:
                    continue
                else:
                    current_area = (new_dict[key] / 2 / math.pi) ** 2 * math.pi
                    current_weight = (current_area - last_value) * (last_key + 5 + key) / 2
                    data[key + 5] = int(current_weight)
                    total += current_weight
                    last_value, last_key = current_area, key

        # 如果是染色材料，总质量打九折
        if self.is_dyed:
            total = total * 0.9

        return int(total), data

    def get_price_by_details(self, dict1):
        """
        根据详情计算价格

        Args:
            dict1: 包含长度和重量信息的字典

        Returns:
            总价格和详细计算结果
        """
        result_dict = {}
        result_sum = 0
        max_price_key = max(self.price_config.keys())

        for key in dict1:
            value1 = dict1[key]
            if key in self.price_config:
                value2 = self.price_config[key]
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    result_dict[key] = [value1, value2, round(value1 * value2, 1)]
                    result_sum += round(value1 * value2, 1)
            elif key > max_price_key:
                value2 = self.price_config[max_price_key]
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    result_dict[key] = [value1, value2, round(value1 * value2, 1)]
                    result_sum += round(value1 * value2, 1)

        return {'total': result_sum, 'details': result_dict}

    def calculate_sum(self, dict1, dict2):
        """
        计算两个字典的加权和

        Args:
            dict1: 第一个字典
            dict2: 第二个字典

        Returns:
            加权和结果
        """
        result = 0
        max_key_in_dict1 = max(dict1.keys()) if dict1 else None

        for key in dict2:
            if key in dict1:
                result += dict1[key] * dict2[key]
            elif max_key_in_dict1 is not None and key > max_key_in_dict1:
                result += dict2[key] * dict1[max_key_in_dict1]

        return result