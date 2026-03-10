import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))

from flask import request, jsonify
from flask_app import app, db
from models.models import ConfigDataModel
from utils.common_utils import list_api_response

@app.route('/.netlify/functions/api_list_questions', methods=['GET'])
def list_questions():
    # 获取查询参数
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    # 获取所有以 filter_ 开头的参数，用于多字段过滤
    filter_params = {key.replace('filter_', ''): value for key, value in request.args.items() if
                     key.startswith('filter_')}
    query = ConfigDataModel.query.filter_by(data_type='1')

    # 搜索功能
    if search:
        query = query.filter(
            (ConfigDataModel.key.ilike(f'%{search}%')) | (ConfigDataModel.value.ilike(f'%{search}%'))
        )

    # 多字段过滤功能
    for field, value in filter_params.items():
        if hasattr(ConfigDataModel, field):
            query = query.filter(getattr(ConfigDataModel, field) == value)

    # 分页功能
    paginated_result = query.paginate(page=page, per_page=page_size, error_out=False)

    # 格式化数据
    items = [item.to_dict() for item in query]

    return list_api_response(
        code=0,
        message="请求成功",
        data=items,
        total=paginated_result.total,
        page=page,
        page_size=page_size
    )

def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
