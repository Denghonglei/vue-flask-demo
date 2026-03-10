# netlify/functions/lambda_function.py
import os
import sys

# 项目根目录（lambda_function.py 位于 netlify/functions/ 下，所以上两级是根目录）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# 导入 Flask 应用
from backend.app import app

# 导入 serverless-wsgi 适配 Netlify
import serverless_wsgi

# Netlify 函数入口（必须命名为 handler）
def handler(event, context):
    # 适配 WSGI 协议
    return serverless_wsgi.handle_request(app, event, context)