# backend/app.py
import sys
import os
import json
import re
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from netlify.functions.shared.utils.response import make_err_response, make_succ_response, make_succ_empty_response

# 添加shared目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'netlify', 'functions', 'shared'))

# 导入业务模块（兼容测试模式）
try:
    from backend import db
    from netlify.functions.shared import calculate_mass_by_length_and_thickness, get_price_by_details, validate_dict
    from netlify.functions.shared.models import Price, Message
except Exception as e:
    print(f"业务模块导入失败，将运行在测试模式: {e}")
    db = None
    calculate_mass_by_length_and_thickness = None
    get_price_by_details = None
    validate_dict = None
    Price = None
    Message = None

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 全局跨域

# 邮件配置
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.163.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'ln80656155@163.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'VGXTT3KBm6paD9Nd')  # 180天过期
MAIL_USE_TLS = bool(os.getenv('MAIL_USE_TLS', True))
# 创建线程池执行器
executor = ThreadPoolExecutor(max_workers=5)

def send_email_async(to, subject, body):
    """异步发送邮件的函数"""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = MAIL_USERNAME
        msg['To'] = to

        # 使用SSL连接163邮箱SMTP服务器
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        print(f"邮件已成功发送至: {to}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP认证失败，请检查邮箱用户名和授权码")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP服务错误: {str(e)}")
        return False
    except Exception as e:
        print(f"发送邮件时发生未知错误: {str(e)}")
        return False

# 定义所有接口
@app.route('/hair/estimate', methods=['GET', 'POST'])
def hair_estimate():
    """头发估价接口"""
    if not all([calculate_mass_by_length_and_thickness, get_price_by_details, validate_dict, Price, db]):
        # 测试模式返回模拟数据
        return make_succ_response({
            "estimate": "1000-2000 元",
            "weight": 150,
            "details": {"level1": 100, "level2": 50},
            "total": 1500
        }, "hair_estimate 接口调用成功(测试模式)")

    data = request.get_json()
    length = int(data.get('length'))
    girth = float(data.get('thickness'))
    if girth > 18 or length > 200:
        return make_err_response('请输入正确的参数', 400)

    method = data.get('method', '2')
    is_dyed = data.get('is_dyed', False)
    details = data.get('details', {})
    details['0'] = girth

    if not validate_dict(details):
        return make_err_response('围度从上到下呈递减趋势', 400)

    result, result_data = calculate_mass_by_length_and_thickness(
        length, details, is_dyed=is_dyed, method=method
    )
    result_dict = get_price_by_details(dict1=result_data, is_dyed=is_dyed)
    result_dict['weight'] = result

    # 把估价历史存入数据库
    try:
        new_price = Price(
            length=length,
            girth=girth,
            is_dyed=is_dyed,
            details=json.dumps(result_dict.get('details', {})),
            user_id=request.remote_addr,
            weight=result,
            price=result_dict.get('total', 0),
            is_delete=False,
            method=method
        )
        db.session.add(new_price)
        db.session.commit()
    except Exception as e:
        print(f"保存估价记录失败: {e}")

    return make_succ_response(result_dict, "估价成功")

@app.route('/message/submit', methods=['POST'])
def message_submit():
    """留言提交接口"""
    if not all([Message, db]):
        return make_succ_empty_response("留言提交成功(测试模式)")

    data = request.get_json()
    name = data.get('name', '')
    contact_info = data.get('contactInfo', '')
    message_content = data.get('message', '')

    new_message = Message(
        name=name,
        contact_info=contact_info,
        message=message_content
    )

    try:
        # 将新留言添加到数据库会话
        db.session.add(new_message)
        # 提交数据库会话
        db.session.commit()
        # 提交异步任务
        executor.submit(send_email_async, '2593910366@qq.com', 'Jozu留言消息，请及时处理',
                        f"姓名：{name}\n联系方式：{contact_info}\n留言内容：{message_content}")
        executor.submit(send_email_async, '973104082@qq.com', 'Jozu留言消息，请及时处理',
                        f"姓名：{name}\n联系方式：{contact_info}\n留言内容：{message_content}")
        return make_succ_empty_response("留言提交成功！")
    except Exception as e:
        # 回滚数据库会话
        db.session.rollback()
        return make_err_response(f"留言提交失败: {str(e)}", 500)

@app.route('/list-questions', methods=['GET'])
def list_questions():
    """问题列表接口"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    search = request.args.get('search', '', type=str)

    # 模拟数据
    questions = [
        {"id": 1, "title": "如何预约服务？", "content": "可以通过线上表单直接预约"},
        {"id": 2, "title": "服务价格是多少？", "content": "根据不同项目价格不同，详情请看价目表"},
        {"id": 3, "title": "营业时间是几点？", "content": "周一至周日 9:00-21:00"},
        {"id": 4, "title": "可以上门服务吗？", "content": "暂时不支持上门服务，欢迎到店体验"},
        {"id": 5, "title": "支持哪些支付方式？", "content": "支持微信、支付宝、银行卡支付"}
    ]

    # 搜索过滤
    if search:
        questions = [q for q in questions if search in q['title'] or search in q['content']]

    # 分页
    total = len(questions)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_questions = questions[start:end]

    return make_succ_response({
        "list": paginated_questions,
        "total": total,
        "page": page,
        "pageSize": page_size
    }, "问题列表获取成功")

@app.route('/pre-book', methods=['POST'])
def pre_book():
    """预约接口"""
    data = request.get_json()
    return make_succ_response({
        "booking_id": "BOOK" + str(hash(str(data)))[:6],
        "info": data
    }, "预约成功")

# 全局异常处理
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"接口异常: {str(e)}", exc_info=True)
    return make_err_response(f"服务器繁忙，请稍后再试: {str(e)}")

@app.errorhandler(404)
def not_found(e):
    return make_err_response(f"接口 {request.path} 不存在")

@app.errorhandler(405)
def method_not_allowed(e):
    return make_err_response(f"请求方法不允许")

# 本地运行入口
if __name__ == '__main__':
    app.run(debug=True, port=5000)
