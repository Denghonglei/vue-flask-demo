import sys
import json
import re
import os
import sqlite3
import random
import smtplib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.utils import formataddr

# 创建线程池执行器，异步发送邮件不阻塞主流程
executor = ThreadPoolExecutor(max_workers=5)


def json_str_to_dict(input_data):
    """
    将 JSON 字符串转换为字典，非 JSON 字符串则返回原数据
    :param input_data: 任意输入（可能是 JSON 字符串/字典/其他类型）
    :return: 解析后的字典 | 原输入数据
    """
    if not isinstance(input_data, str):
        return input_data

    clean_str = input_data.strip()
    if not (clean_str.startswith(('{', '[')) and clean_str.endswith(('}', ']'))):
        return input_data

    try:
        parsed_data = json.loads(clean_str)
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"[警告] JSON 解析失败：{e} | 原始数据：{input_data[:100]}")
        return input_data


# ---------------  驼峰/下划线互转公共工具  ---------------
def camel_to_snake(name):
    """驼峰命名转下划线命名：isDyed → is_dyed"""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def snake_to_camel(name):
    """下划线命名转驼峰命名：is_dyed → isDyed"""
    parts = name.split('_')
    return parts[0] + ''.join(part.title() for part in parts[1:])


def convert_dict_keys(data, convert_func):
    """递归转换字典的所有键名（支持嵌套字典/列表）"""
    if isinstance(data, dict):
        return {
            convert_func(key) if isinstance(key, str) else key:
            convert_dict_keys(value, convert_func)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_dict_keys(item, convert_func) for item in data]
    else:
        return data
# --------------------------------------------------------


def init_db():
    """初始化SQLite数据库，创建预约表"""
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()

    # 创建预约表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            type TEXT NOT NULL,
            city TEXT,
            address TEXT,
            date TEXT,
            time TEXT,
            express_company TEXT,
            tracking_number TEXT,
            is_know_rules INTEGER,
            length INTEGER NOT NULL,
            is_dyed INTEGER NOT NULL,
            remark TEXT,
            created_at TEXT NOT NULL,
            status INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


def generate_order_no():
    """生成唯一订单号：年月日时分秒 + 4位随机数"""
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"YD{now}{random_num}"


def send_email_notification(booking_data, order_no):
    """发送新预约通知邮件"""
    try:
        # 从环境变量读取邮件配置
        SMTP_SERVER = os.getenv('MAIL_SERVER', 'smtp.163.com')
        SMTP_PORT = int(os.getenv('MAIL_PORT', 465))
        SENDER_EMAIL = os.getenv('MAIL_USERNAME', 'ln80656155@163.com')
        SENDER_PASSWORD = os.getenv('MAIL_PASSWORD', 'VGXTT3KBm6paD9Nd')
        MAIL_USE_TLS = bool(os.getenv('MAIL_USE_TLS', True))
        # 收件人列表，可以配置多个邮箱，用逗号分隔
        RECEIVER_EMAIL = os.getenv('MAIL_RECEIVER', 'ln80656155@163.com,2593910366@qq.com').split(',')

        # 构造邮件内容
        booking_type_text = '上门回收' if booking_data['type'] == 'door' else '快递回收'
        time_text_map = {
            'morning': '上午 9:00-12:00',
            'afternoon': '下午 14:00-18:00',
            'evening': '晚上 18:00-21:00'
        }

        content = f"""
        <h3>🎉 新的预约订单提醒</h3>
        <p><strong>订单号：</strong>{order_no}</p>
        <p><strong>预约类型：</strong>{booking_type_text}</p>
        <p><strong>姓名：</strong>{booking_data['name']}</p>
        <p><strong>手机号码：</strong>{booking_data['phone']}</p>
        <p><strong>头发长度：</strong>{booking_data['length']} cm</p>
        <p><strong>是否烫染：</strong>{'是' if booking_data['is_dyed'] else '否'}</p>
        """

        if booking_data['type'] == 'door':
            content += f"""
            <p><strong>所在城市：</strong>{booking_data['city']}</p>
            <p><strong>详细地址：</strong>{booking_data['address']}</p>
            <p><strong>期望上门日期：</strong>{booking_data['date']}</p>
            <p><strong>期望上门时间：</strong>{time_text_map.get(booking_data['time'], booking_data['time'])}</p>
            """
        else:
            content += f"""
            <p><strong>快递公司：</strong>{booking_data['express_company']}</p>
            <p><strong>快递单号：</strong>{booking_data['tracking_number']}</p>
            <p><strong>是否知晓规则：</strong>{'是' if booking_data['is_know_rules'] else '否'}</p>
            """

        if booking_data.get('remark'):
            content += f"<p><strong>备注信息：</strong>{booking_data['remark']}</p>"

        content += f"<p><strong>提交时间：</strong>{booking_data['created_at']}</p>"

        # 构造邮件
        msg = MIMEText(content, 'html', 'utf-8')
        msg['From'] = formataddr(('长发回收系统', SENDER_EMAIL))
        # 处理多个收件人
        msg['To'] = ', '.join([formataddr(('管理员', email)) for email in RECEIVER_EMAIL])
        msg['Subject'] = f'新预约通知 - {order_no}'

        # 发送邮件（兼容TLS和SSL模式）
        if MAIL_USE_TLS and SMTP_PORT == 587:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        # 不要打印到stdout，避免和返回的JSON结果混合
        # print(f"邮件通知发送成功，订单号：{order_no}")
        return True
    except Exception as e:
        # 不要打印到stdout，避免和返回的JSON结果混合
        # print(f"邮件通知发送失败：{e}")
        return False


def save_booking_data(booking_data):
    """保存预约数据到SQLite数据库"""
    try:
        # 初始化数据库
        init_db()

        # 生成订单号
        order_no = generate_order_no()
        booking_data['order_no'] = order_no
        booking_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        booking_data['is_dyed'] = 1 if booking_data.get('is_dyed') else 0
        booking_data['is_know_rules'] = 1 if booking_data.get('is_know_rules') else 0

        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()

        # 插入数据
        cursor.execute('''
            INSERT INTO bookings (
                order_no, name, phone, type, city, address, date, time,
                express_company, tracking_number, is_know_rules, length,
                is_dyed, remark, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_data['order_no'],
            booking_data['name'],
            booking_data['phone'],
            booking_data['type'],
            booking_data.get('city', ''),
            booking_data.get('address', ''),
            booking_data.get('date', ''),
            booking_data.get('time', ''),
            booking_data.get('express_company', ''),
            booking_data.get('tracking_number', ''),
            booking_data.get('is_know_rules', 0),
            booking_data['length'],
            booking_data['is_dyed'],
            booking_data.get('remark', ''),
            booking_data['created_at']
        ))

        conn.commit()
        conn.close()
        return True, order_no
    except Exception as e:
        # 不要打印到stdout，避免和返回的JSON结果混合
        # print(f"保存预约数据失败：{e}")
        return False, None


def main(params):
    """预约上门/快递回收业务逻辑"""
    params = json_str_to_dict(params)
    # 统一转换入参驼峰转下划线
    params = convert_dict_keys(params, camel_to_snake)

    # 基础参数验证
    required_fields = ['name', 'phone', 'length', 'type']
    if params.get('type') == 'door':
        required_fields.extend(['city', 'address', 'date', 'time'])
    else:
        required_fields.extend(['express_company', 'tracking_number', 'is_know_rules'])

    missing_fields = [field for field in required_fields if not params.get(field)]
    if missing_fields:
        result = {
            'code': 400,
            'message': f"缺少必填字段：{', '.join(missing_fields)}"
        }
        return convert_dict_keys(result, snake_to_camel)

    # 手机号验证
    phone = params.get('phone')
    if not re.match(r'^1[3-9]\d{9}$', phone):
        result = {
            'code': 400,
            'message': "请输入正确的手机号码"
        }
        return convert_dict_keys(result, snake_to_camel)

    # 保存预约数据
    save_success, order_no = save_booking_data(params)
    if not save_success:
        result = {
            'code': 500,
            'message': "预约提交失败，请稍后重试"
        }
        return convert_dict_keys(result, snake_to_camel)

    # 异步发送邮件通知，不影响主流程，发送失败也不影响预约结果
    executor.submit(send_email_notification, params, order_no)

    # 返回成功，带订单号
    result = {
        'code': 0,
        'message': "预约提交成功",
        'order_no': order_no
    }
    return convert_dict_keys(result, snake_to_camel)


if __name__ == '__main__':
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "name": "张三",
        "phone": "13800138000",
        "type": "door",
        "city": "上海",
        "address": "浦东新区某某路123号",
        "date": "2026-03-15",
        "time": "morning",
        "length": 50,
        "isDyed": False,
        "remark": "上午来之前请提前打电话"
    }
    result = main(params)
    print(json.dumps(result, ensure_ascii=False))
