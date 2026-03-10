import sys
import os
import re
import smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))

from flask import request, jsonify
from flask_app import app, db
from models.models import Message

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

@app.route('/.netlify/functions/message_submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name')
    contact_info = data.get('contactInfo')
    message_content = data.get('message')

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
                        name + contact_info + message_content)
        executor.submit(send_email_async, '973104082@qq.com', 'Jozu留言消息，请及时处理',
                        name + contact_info + message_content)
        return jsonify({"message": "留言提交成功！"})
    except Exception as e:
        # 回滚数据库会话
        db.session.rollback()
        return jsonify({"message": f"留言提交失败: {str(e)}"}), 500

def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
