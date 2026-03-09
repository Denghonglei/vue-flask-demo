import sys
import os
import re
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))

from flask import request, jsonify
from flask_app import app, db
from hairprice.models import Booking
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor

# 配置邮件信息
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

# 数据验证
def validate_booking(data):
    errors = {}

    # 验证日期格式
    try:
        datetime.strptime(data.get('date', ''), '%Y-%m-%d')
    except ValueError:
        errors['date'] = '日期格式不正确，应为YYYY-MM-DD'

    # 验证时间段
    valid_time_slots = ['09:00-11:00', '11:00-13:00', '13:00-15:00',
                        '15:00-17:00', '17:00-19:00', '19:00-21:00', 'morning', 'afternoon', 'evening']
    if data.get('time') not in valid_time_slots:
        errors['time_slot'] = '无效的时间段'

    # 验证地址
    if not data.get('address'):
        errors['address'] = '地址不能为空'

    # 验证姓名
    if not data.get('name'):
        errors['name'] = '姓名不能为空'

    # 验证手机号
    phone_pattern = r'^1[3-9]\d{9}$'
    if not re.match(phone_pattern, data.get('phone', '')):
        errors['phone'] = '手机号格式不正确'

    return errors

@app.route('/.netlify/functions/api_pre_book', methods=['POST'])
def create_booking():
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求数据不能为空', 'code': 400}), 400

    errors = validate_booking(data)
    if errors:
        return jsonify({'errors': errors, 'code': 400}), 400

    try:
        # 转换日期格式
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        new_booking = Booking(
            date=booking_date,
            time_slot=data['time'],
            address=data['address'],
            name=data['name'],
            phone=data['phone'],
            notes=data.get('remark', '')
        )

        db.session.add(new_booking)
        db.session.commit()

        # 提交异步邮件任务
        executor.submit(send_email_async, '2593910366@qq.com', 'Jozu预约消息，请及时处理',
                        data['name'] + '联系电话：' + data['phone'] + '地址：' + data['address'] + '预约时间：' + data[
                            'date'] + data['time'])
        executor.submit(send_email_async, '973104082@qq.com', 'Jozu预约消息，请及时处理',
                        data['name'] + '联系电话：' + data['phone'] + '地址：' + data['address'] + '预约时间：' + data[
                            'date'] + data['time'])

        # 返回成功响应
        return jsonify({
            'message': '预约成功',
            'order_number': f"HS{datetime.now().strftime('%Y%m%d')}{new_booking.id:04d}",
            'code': 200
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'code': 500}), 500

def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
