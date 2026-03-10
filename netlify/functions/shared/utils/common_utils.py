# 定义一个通用的返回数据封装函数
from flask import request, jsonify
import re
from run import app

def response_wrapper(code=0, message='success', data=None):
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)


# 统一接口返回格式的函数
def list_api_response(code, message, data=None, total=None, page=None, page_size=None):
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    if total is not None:
        response["total"] = total
    if page is not None:
        response["page"] = page
    if page_size is not None:
        response["page_size"] = page_size
    return jsonify(response)


# 驼峰转下划线
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# 下划线转驼峰
def snake_to_camel(name):
    components = name.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


# 转换字典键名
def convert_dict_keys(data, conversion_func):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = conversion_func(key)
            if isinstance(value, (dict, list)):
                new_data[new_key] = convert_dict_keys(value, conversion_func)
            else:
                new_data[new_key] = value
        return new_data
    elif isinstance(data, list):
        return [convert_dict_keys(item, conversion_func) for item in data]
    return data


# 请求前处理
@app.before_request
def convert_request_params():
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        if data:
            request._cached_json = (convert_dict_keys(data, camel_to_snake), request._cached_json[1])
            request._json = None
    elif request.method == 'GET':
        new_args = {}
        for key, value in request.args.items():
            new_key = camel_to_snake(key)
            new_args[new_key] = value
        request.args = type(request.args)(new_args)


# 响应后处理
@app.after_request
def convert_response(response):
    if response.content_type == 'application/json':
        data = response.get_json()
        if data:
            new_data = convert_dict_keys(data, snake_to_camel)
            response.set_data(jsonify(new_data).data)
    return response