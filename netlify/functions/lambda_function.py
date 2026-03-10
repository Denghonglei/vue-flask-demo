# netlify/functions/lambda_function.py
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# 导入 Flask 应用
from backend.app import app

# 导入 serverless-wsgi 适配 Netlify
import serverless_wsgi

# Netlify 函数入口（必须命名为 handler）
def handler(event, context):
    # 适配 WSGI 协议
    return serverless_wsgi.handle_request(app, event, context)