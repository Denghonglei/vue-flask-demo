import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))

from flask import request, jsonify
from flask_app import app, db
from hairprice.hair_tools import calculate_mass_by_length_and_thickness, get_price_by_details, validate_dict
from hairprice.models import Price

@app.route('/.netlify/functions/hair_estimate', methods=['POST'])
def calculate():
    data = request.get_json()
    length = int(data.get('length'))
    girth = float(data.get('thickness'))
    if girth > 18 or length > 200:
        return jsonify({'code': 400, 'msg': '请输入正确的参数'}), 400
    method = data.get('method', '2')
    is_dyed = data.get('is_dyed', False)
    details = data.get('details', {})
    details['0'] = girth
    if not validate_dict(details):
        return jsonify({'code': 400, 'msg': '围度从上到下呈递减趋势'}), 400
    result, result_data = calculate_mass_by_length_and_thickness(length, details, is_dyed=is_dyed,
                                                                 method=method)
    result_dict = get_price_by_details(dict1=result_data, is_dyed=is_dyed)
    result_dict['weight'] = result
    # 把估价历史存入数据库：
    try:
        # 创建 new_price 对象
        new_price = Price(
            length=length,
            girth=girth,
            is_dyed=is_dyed,
            details=json.dumps(result_dict['details']),
            user_id=request.remote_addr,
            weight=result,
            price=result_dict['total'],
            is_delete=False,
            method=method
        )

        # 将新价格对象添加到数据库
        db.session.add(new_price)
        db.session.commit()
    except Exception as e:
        print(e)
    return jsonify({'result': result_dict})

def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
