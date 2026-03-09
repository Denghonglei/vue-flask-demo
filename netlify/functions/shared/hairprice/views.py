import json
import os
import re
import smtplib
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from sqlite3 import IntegrityError

import requests
from flask import request, jsonify
from functools import wraps
from flask import abort
from flask_caching import Cache
from flasgger import Swagger

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource, reqparse, abort
from sqlalchemy import desc

from config import Config
from run import app
from wxcloudrun import db
from wxcloudrun.common_utils import response_wrapper, list_api_response
from wxcloudrun.hairprice.hair_tools import calculate_mass_by_length_and_thickness, get_price_by_details, \
    convert_details, convert_result_dict, validate_dict
from wxcloudrun.hairprice.models import User, Hair, Price, Appointment, ConfigDataModel, Message, Booking, ExpressOrder

app.config[
    'JWT_SECRET_KEY'] = """b'\xfa\xc3\xaf\xe8x\xbe\x8a\x8cqM\xcc\xb9/+\xfb\\\xb4\xbc\x9b\x18]\xf7zc'"""  # 使用 os.urandom 生成安全的密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['CACHE_TYPE'] = 'SimpleCache'  # 使用简单的内存缓存
app.config['CACHE_DEFAULT_TIMEOUT'] = 86400  # 缓存默认超时时间（秒），这里设置为1天

app.config['SWAGGER'] = {
    'title': '我的 API',
    'uiversion': 3  # Swagger UI 版本
}

swagger = Swagger(app)

api = Api(app)
jwt = JWTManager(app)
cache = Cache(app)

# 定义角色常量
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
ROLE_MEMBER = 'member'


# 权限装饰器
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            openid = get_jwt_identity()
            current_user = User.query.filter_by(openid=openid).first()
            if current_user.role != role:
                abort(403)  # 拒绝访问
            return f(*args, **kwargs)

        return decorated_function

    return wrapper


@app.route('/hair/estimate', methods=['POST'])
def calculate():
    """
    获取估价
    ---
    tags:
      - Hair Estimate
    parameters:
      - name: length
        in: body
        required: true
        type: integer
        description: Hair length in cm
      - name: thickness
        in: body
        required: true
        type: number
        format: float
        description: Hair thickness in cm
      - name: method
        in: body
        required: false
        type: string
        description: Method for calculation (default is '2')
      - name: isDyed
        in: body
        required: false
        type: boolean
        description: Whether the hair is dyed
      - name: details
        in: body
        required: true
        type: object
        description: Additional details for calculation
    responses:
      200:
        description: Estimated price and weight
        schema:
          type: object
          properties:
            result:
              type: object
              properties:
                weight:
                  type: number
                  format: float
                  description: Calculated weight
                details:
                  type: object
                  description: Detailed calculation results
      400:
        description: Invalid input parameters
    """
    data = request.get_json()
    length = int(data.get('length'))
    girth = float(data.get('thickness'))
    if girth > 18 or length > 200:
        return jsonify({'code': 400, 'msg': '请输入正确的参数'}), 400
    method = data.get('method', '2')
    is_dyed = data.get('is_dyed')
    details = data.get('details')
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


@app.route('/login', methods=['POST'])
def login():
    code = request.json.get('code')
    if not code:
        return jsonify({'code': 400, 'msg': '缺少code参数'}), 400

    # 调用微信接口获取openid
    wx_response = requests.get(
        'https://api.weixin.qq.com/sns/jscode2session',
        params={
            'appid': Config.WECHAT_APPID,  # 替换为你的小程序AppID
            'secret': Config.WECHAT_APPSECRET,  # 替换为你的小程序AppSecret
            'js_code': code,
            'grant_type': 'authorization_code'
        }
    )
    wx_data = wx_response.json()
    openid = wx_data.get('openid')

    if not openid:
        # openid = 'oCo1D6lyo2R7-VrMBfSQRKoROVUE'  # 调试用

        return jsonify({'code': 400, 'msg': '获取openid失败'}), 400
    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(username='name' + openid, role='user', openid=openid)
        db.session.add(user)
        db.session.commit()
    access_token = create_access_token(identity=openid)  # user_id是用户的唯一标识符
    return jsonify({'code': 0, 'data': {'token': access_token}}), 200


class HairResource(Resource):
    @jwt_required()
    def get(self, hair_id=None):
        current_user_id = get_jwt_identity()
        if hair_id:
            hair = Hair.query.filter_by(id=hair_id, user_id=current_user_id).first()
            if not hair:
                abort(404, message="Hair not found")
            return hair.to_dict()  # 假设模型有 to_dict 方法
        else:
            hairs = Hair.query.filter_by(user_id=current_user_id).all()
            return [hair.to_dict() for hair in hairs]

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('length', type=int, required=True)
        parser.add_argument('girth', type=float, required=True)
        parser.add_argument('is_permed', type=bool)
        parser.add_argument('details')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        new_hair = Hair(
            length=args['length'],
            girth=args['girth'],
            user_id=current_user_id,
            is_permed=args['is_permed'],
            details=args['details']
        )
        db.session.add(new_hair)
        db.session.commit()
        return new_hair.to_dict(), 201

    @jwt_required()
    def put(self, hair_id):
        parser = reqparse.RequestParser()
        parser.add_argument('length', type=int)
        parser.add_argument('girth', type=float)
        parser.add_argument('is_permed', type=bool)
        parser.add_argument('details')
        args = parser.parse_args()

        current_user_id = get_jwt_identity()
        hair = Hair.query.filter_by(id=hair_id, user_id=current_user_id).first()
        if not hair:
            abort(404, message="Hair not found")

        if args['length'] is not None:
            hair.length = args['length']
        if args['girth'] is not None:
            hair.girth = args['girth']
        if args['is_permed'] is not None:
            hair.is_permed = args['is_permed']
        if args['details'] is not None:
            hair.details = args['details']

        db.session.commit()
        return hair.to_dict()

    @jwt_required()
    def delete(self, hair_id):
        current_user_id = get_jwt_identity()
        hair = Hair.query.filter_by(id=hair_id, user_id=current_user_id).first()
        if not hair:
            abort(404, message="Hair not found")

        db.session.delete(hair)
        db.session.commit()
        return '', 204


api.add_resource(HairResource, '/hairs', '/hairs/<int:hair_id>')


def extend_membership_expiry(user_id, openid, days):
    if user_id:
        user = User.query.filter_by(id=user_id).first()
    elif openid:
        user = User.query.filter_by(openid=openid).first()
    else:
        return jsonify({"msg": "User not found"}), 404
    if not user:
        return jsonify({'error': 'User not found'}), 404

    current_time = datetime.utcnow()
    if user.membership_expiry is None or user.membership_expiry < current_time:
        new_expiry = current_time + timedelta(days=days)
    else:
        new_expiry = user.membership_expiry + timedelta(days=days)

    user.membership_expiry = new_expiry
    db.session.commit()
    return jsonify({'message': 'Membership expiry extended successfully', 'new_expiry': new_expiry.isoformat()}), 200


@app.route('/user/modify_info', methods=['POST'])
@jwt_required()
@role_required(ROLE_ADMIN)
def modify_userinfo():
    req_data = request.get_json()
    user_id = req_data.get('user_id', None)
    openid = req_data.get('openid', None)

    days = req_data.get('days')

    if not user_id or not days:
        return jsonify({'error': 'user_id and days are required'}), 400
    try:
        days = int(days)
    except ValueError:
        return jsonify({'error': 'days must be an integer'}), 400

    return extend_membership_expiry(user_id=user_id, openid=openid, days=days)


# 控制权限，用户分为三类，普通用户user、管理员admin、会员member
def access_control():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            openid = get_jwt_identity()
            user = User.query.filter_by(openid=openid).first()

            if user.role == 'admin':
                return f(*args, **kwargs)
            if user.role == 'member' and user.membership_expiry > datetime.utcnow():
                return f(*args, **kwargs)
            else:
                today = datetime.utcnow().date()
                cache_key = f"access_count:{user.id}:{today}"
                access_count = cache.get(cache_key)
                if access_count is None:
                    access_count = 0

                if access_count < 6:
                    access_count += 1
                    cache.set(cache_key, access_count, timeout=86400)  # 缓存一天
                    return f(*args, **kwargs)
                else:
                    return jsonify({'message': 'Daily access limit exceeded'}), 403

        return decorated_function

    return decorator


class PriceResource(Resource):
    @jwt_required()
    def get(self, price_id=None):
        current_user_id = get_jwt_identity()
        if price_id:
            price = Price.query.filter_by(id=price_id, user_id=current_user_id, is_delete=False).first()
            if not price:
                abort(404, message="Hair not found")
            return response_wrapper(data=price.to_dict())  # 假设模型有 to_dict 方法
        else:
            # 获取查询参数
            search = request.args.get('search', '')
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            data = request.args
            print(data)
            # 获取所有以 filter_ 开头的参数，用于多字段过滤
            filter_params = {key.replace('filter_', ''): value for key, value in request.args.items() if
                             key.startswith('filter_')}
            query = Price.query.filter_by(user_id=current_user_id, is_delete=False).order_by(desc(Price.created_at))

            # 构建查询对象
            # query = Item.query

            # 搜索功能
            if search:
                query = query.filter(
                    (Price.method.ilike(f'%{search}%')) | (Price.length.ilike(f'%{search}%'))
                )

            # 多字段过滤功能
            for field, value in filter_params.items():
                if hasattr(Price, field):
                    query = query.filter(getattr(Price, field) == value)

            # 分页功能
            paginated_result = query.paginate(page=page, per_page=page_size, error_out=False)

            # 格式化数据
            items = [price.to_dict() for price in query]

            return list_api_response(
                code=0,
                message="请求成功",
                data=items,
                total=paginated_result.total,
                page=page,
                page_size=page_size
            )

            # return response_wrapper(data=[price.to_dict() for price in hairs])

    @jwt_required()
    def post(self):
        # 通过其他接口实现
        pass
        # return new_hair.to_dict(), 201

    @jwt_required()
    def put(self, hair_id):
        # 通过其他接口实现
        pass

    @jwt_required()
    def delete(self, price_id):
        current_user_id = get_jwt_identity()
        price = Price.query.filter_by(id=price_id, user_id=current_user_id, is_delete=False).first()
        if not price:
            abort(404, message="Hair not found")

        price.is_delete = True
        db.session.commit()
        return response_wrapper()


api.add_resource(PriceResource, '/prices', '/prices/<int:price_id>')


@app.route('/api/estimate', methods=['POST'])
@jwt_required()
@access_control()
def price_protected():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 使用 get() 方法获取参数并提供默认值
    length = int(data.get('length', 0))
    girth = float(data.get('girth', 0.0))
    method = data.get('method', '2')
    is_dyed = data.get('is_dyed', False)

    # 确保 girth 是有效的
    if girth <= 0:
        return jsonify({'error': 'Girth must be greater than 0'}), 400

    # 将 girth 添加到 details 字典中
    details = convert_details(data.get('details'))
    details['0'] = girth

    # 计算质量和价格
    result, result_data = calculate_mass_by_length_and_thickness(length, details, is_dyed=is_dyed, method=method)
    result_dict = get_price_by_details(result_data, is_dyed=is_dyed)
    result_dict['weight'] = result
    result_dict['details'] = convert_result_dict(result_dict['details'])

    # 创建 new_price 对象
    new_price = Price(
        length=length,
        girth=girth,
        is_dyed=is_dyed,
        details=json.dumps(result_dict['details']),
        user_id=current_user_id,
        weight=result,
        price=result_dict['total'],
        is_delete=False,
        method=method
    )

    # 将新价格对象添加到数据库
    db.session.add(new_price)
    db.session.commit()

    return response_wrapper(code=0, message='success', data=new_price.to_dict())


@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    expected_time = datetime.fromisoformat(data['expected_time'])
    expected_location = data['expected_location']
    contact_number = data['contact_number']

    # 查找用户的最新 Hair 信息
    latest_hair = Hair.query.filter_by(user_id=current_user_id).order_by(Hair.created_at.desc()).first()
    latest_price = Price.query.filter_by(user_id=current_user_id).order_by(Price.created_at.desc()).first()

    new_appointment = Appointment(
        user_id=current_user_id,
        expected_time=expected_time,
        expected_location=expected_location,
        contact_number=contact_number,
        hair_id=latest_hair.id if latest_hair else None,
        price_id=latest_price.id if latest_price else None
    )

    db.session.add(new_appointment)
    db.session.commit()

    return new_appointment.to_dict(), 201


@app.route('/api/appointments/<int:appointment_id>/confirm', methods=['PUT'])
@jwt_required()
@role_required(ROLE_ADMIN)  # 假设有一个装饰器用于检查管理员权限
def confirm_appointment(appointment_id):
    data = request.get_json()
    actual_price = data.get('actual_price', None)
    weight = data.get('weight', None)
    actual_time = data.get('actual_time', None)
    appointment = Appointment.query.filter_by(appointment_id=appointment_id)
    appointment.status = 'in_progress'
    if actual_time:
        appointment.actual_time = actual_time
    if actual_price and weight:
        appointment.actual_price = actual_price
        appointment.weight = weight
        appointment.status = 'completed'
    appointment.updated_at = datetime.utcnow()
    db.session.commit()

    return appointment.to_dict(), 200


@app.route('/api/appointments/<int:appointment_id>', methods=['GET'])
@role_required(ROLE_ADMIN)
@jwt_required()
def get_appointment(appointment_id):
    appointment = Appointment.query.filter_by(appointment_id=appointment_id)
    return {
        'appointment': appointment.to_dict(),
        'hair': appointment.hair.to_dict() if appointment.hair else None,
        'price': appointment.price.to_dict() if appointment.price else None
    }, 200


@app.route('/api//user/appointments', methods=['GET'])
@jwt_required()
def get_user_appointments():
    current_user_id = get_jwt_identity()  # 获取当前用户的 ID
    appointments = Appointment.query.filter_by(user_id=current_user_id).all()  # 查询用户的所有预约

    # 将预约信息转换为字典格式
    return jsonify([appointment.to_dict() for appointment in appointments]), 200


@app.route('/api/list-questions', methods=['GET'])
def list_questions():
    # 获取查询参数
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    # 获取所有以 filter_ 开头的参数，用于多字段过滤
    filter_params = {key.replace('filter_', ''): value for key, value in request.args.items() if
                     key.startswith('filter_')}
    query = ConfigDataModel.query.filter_by(data_type='1')

    # 构建查询对象
    # query = Item.query

    # 搜索功能
    if search:
        query = query.filter(
            (ConfigDataModel.key.ilike(f'%{search}%')) | (ConfigDataModel.value.ilike(f'%{search}%'))
        )

    # 多字段过滤功能
    for field, value in filter_params.items():
        if hasattr(Price, field):
            query = query.filter(getattr(Price, field) == value)

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


@app.route('/message/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name')
    contact_info = data.get('contact_info')
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
                        '15:00-17:00', '17:00-19:00', '19:00-21:00']
    if data.get('time_slot') not in valid_time_slots:
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


# API接口
@app.route('/api/v1/pre-book', methods=['POST'])
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
            time_slot=data['time_slot'],
            address=data['address'],
            name=data['name'],
            phone=data['phone'],
            notes=data.get('notes')
        )

        db.session.add(new_booking)
        db.session.commit()

        # 提交异步邮件任务
        executor.submit(send_email_async, '2593910366@qq.com', 'Jozu预约消息，请及时处理',
                        data['name'] + '联系电话：' + data['phone'] + '地址：' + data['address'] + '预约时间：' + data[
                            'date'] + data['time_slot'])
        executor.submit(send_email_async, '973104082@qq.com', 'Jozu预约消息，请及时处理',
                        data['name'] + '联系电话：' + data['phone'] + '地址：' + data['address'] + '预约时间：' + data[
                            'date'] + data['time_slot'])

        # 返回成功响应
        return jsonify({
            'message': '预约成功',
            'order_number': f"HS{datetime.now().strftime('%Y%m%d')}{new_booking.id:04d}",
            'code': 200
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'code': 500}), 500


class ConfigDataController:
    """配置数据的CRUD操作控制器"""

    @staticmethod
    def create_config():
        """创建新配置"""
        data = request.get_json()

        if not data or 'key' not in data or 'value' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        new_config = ConfigDataModel(
            data_type=data.get('data_type', 'string'),
            key=data['key'],
            value=data['value']
        )

        try:
            db.session.add(new_config)
            db.session.commit()
            return jsonify({
                "message": "Config created successfully",
                "config": {
                    "id": new_config.id,
                    "data_type": new_config.data_type,
                    "key": new_config.key,
                    "value": new_config.value
                }
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Key already exists"}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_all_configs():
        """获取所有配置"""
        try:
            configs = ConfigDataModel.query.all()
            return jsonify([{
                "id": config.id,
                "data_type": config.data_type,
                "key": config.key,
                "value": config.value
            } for config in configs]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_config_by_key(key):
        """根据key获取配置"""
        config = ConfigDataModel.query.filter_by(key=key).first()

        if not config:
            return jsonify({"error": "Config not found"}), 404

        return jsonify({
            "id": config.id,
            "data_type": config.data_type,
            "key": config.key,
            "value": config.value
        }), 200

    @staticmethod
    def update_config(key):
        """更新配置"""
        config = ConfigDataModel.query.filter_by(key=key).first()

        if not config:
            return jsonify({"error": "Config not found"}), 404

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if 'data_type' in data:
            config.data_type = data['data_type']
        if 'value' in data:
            config.value = data['value']

        try:
            db.session.commit()
            return jsonify({
                "message": "Config updated successfully",
                "config": {
                    "id": config.id,
                    "data_type": config.data_type,
                    "key": config.key,
                    "value": config.value
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def delete_config(key):
        """删除配置"""
        config = ConfigDataModel.query.filter_by(key=key).first()

        if not config:
            return jsonify({"error": "Config not found"}), 404

        try:
            db.session.delete(config)
            db.session.commit()
            return jsonify({"message": "Config deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


# 注册路由
@app.route('/api/configs', methods=['POST'])
def create_config():
    return ConfigDataController.create_config()


@app.route('/api/configs', methods=['GET'])
def get_all_configs():
    return ConfigDataController.get_all_configs()


@app.route('/api/configs/<key>', methods=['GET'])
def get_config(key):
    return ConfigDataController.get_config_by_key(key)


@app.route('/api/configs/<key>', methods=['PUT'])
def update_config(key):
    return ConfigDataController.update_config(key)


@app.route('/api/configs/<key>', methods=['DELETE'])
def delete_config(key):
    return ConfigDataController.delete_config(key)


# 快递单号格式校验函数
def validate_tracking_number(company, tracking_number):
    """
    验证快递单号格式是否符合常见快递公司的规则

    参数:
        company: 快递公司名称
        tracking_number: 快递单号

    返回:
        (is_valid, message): 是否有效和错误信息
    """
    # 去除空格和特殊字符
    cleaned_number = re.sub(r'[^a-zA-Z0-9]', '', tracking_number.upper())

    # 常见快递公司单号格式规则
    rules = {
        "顺丰速运": {
            "pattern": r'^SF\d{12}$|^\d{12}$',
            "message": "顺丰单号应为12位数字或以SF开头的14位字符"
        },
        "中通快递": {
            "pattern": r'^\d{10}$|^ZTO\d{10}$',
            "message": "中通单号应为10位数字或以ZTO开头的13位字符"
        },
        "圆通速递": {
            "pattern": r'^\d{10}$|^YT\d{10}$',
            "message": "圆通单号应为10位数字或以YT开头的12位字符"
        },
        "韵达快递": {
            "pattern": r'^\d{13}$|^YD\d{10}$',
            "message": "韵达单号应为13位数字或以YD开头的12位字符"
        },
        "申通快递": {
            "pattern": r'^\d{12}$|^STO\d{10}$',
            "message": "申通单号应为12位数字或以STO开头的13位字符"
        },
        "京东物流": {
            "pattern": r'^JD[A-Z0-9]{15}$|^\d{15}$',
            "message": "京东单号应为15位数字或以JD开头的17位字符"
        },
        "其他": {
            "pattern": r'^[A-Z0-9]{8,20}$',
            "message": "单号应为8-20位字母数字组合"
        }
    }

    # 获取对应公司的规则
    rule = rules.get(company, rules["其他"])

    # 验证单号格式
    if re.match(rule["pattern"], cleaned_number):
        return True, "单号格式正确"
    else:
        return False, rule["message"]


# 快递单号回填接口
@app.route('/api/v1/backfill', methods=['POST'])
def backfill_order():
    try:
        # 获取请求数据
        data = request.json

        # 验证必要字段
        required_fields = ['tracking_number', 'express_company']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"缺少必要字段: {field}"
                }), 400

        # 验证快递单号格式
        is_valid, error_msg = validate_tracking_number(
            data['express_company'],
            data['tracking_number']
        )

        if not is_valid:
            return jsonify({
                "success": False,
                "message": f"快递单号格式错误: {error_msg}"
            }), 400

        # 检查快递单号是否已存在
        existing_order = ExpressOrder.query.filter_by(
            tracking_number=data['tracking_number']
        ).first()

        if existing_order:
            return jsonify({
                "success": False,
                "message": "该快递单号已存在，请勿重复提交"
            }), 400

        # 创建新订单
        new_order = ExpressOrder(
            tracking_number=data['tracking_number'],
            express_company=data['express_company'],
            is_estimated=data.get('is_estimated', False),
            is_know_rules=data.get('is_know_rules', False),
            note=data.get('note', '')
        )

        # 保存到数据库
        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "快递单号提交成功",
            "data": {
                "id": new_order.id,
                "tracking_number": new_order.tracking_number,
                "created_at": new_order.created_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500


# 获取所有订单接口（用于测试）
@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    orders = ExpressOrder.query.all()
    return jsonify({
        "success": True,
        "count": len(orders),
        "orders": [
            {
                "id": order.id,
                "tracking_number": order.tracking_number,
                "express_company": order.express_company,
                "is_estimated": order.is_estimated,
                "is_know_rules": order.is_know_rules,
                "note": order.note,
                "created_at": order.created_at.isoformat()
            } for order in orders
        ]
    })


@app.route('/api/v1/prices', methods=['GET'])
@role_required(ROLE_ADMIN)
def get_price_list():
    """
    获取价格记录列表
    支持分页、用户筛选、时间范围筛选、排序等功能
    """
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        # 限制最大每页数量
        per_page = min(per_page, 100)

        # 查询条件构建 - 只查询未删除的记录
        query = Price.query.filter_by(is_delete=False)

        # 用户筛选
        user_id = request.args.get('user_id')
        if user_id:
            query = query.filter_by(user_id=user_id)

        # 是否染色筛选
        is_dyed = request.args.get('is_dyed')
        if is_dyed is not None:
            # 处理字符串形式的布尔值参数
            query = query.filter_by(is_dyed=is_dyed.lower() == 'true')

        # 切割方法筛选
        method = request.args.get('method')
        if method:
            query = query.filter_by(method=method)

        # 价格范围筛选
        min_price = request.args.get('min_price', type=float)
        if min_price is not None:
            query = query.filter(Price.price >= min_price)

        max_price = request.args.get('max_price', type=float)
        if max_price is not None:
            query = query.filter(Price.price <= max_price)

        # 长度范围筛选
        min_length = request.args.get('min_length', type=int)
        if min_length is not None:
            query = query.filter(Price.length >= min_length)

        max_length = request.args.get('max_length', type=int)
        if max_length is not None:
            query = query.filter(Price.length <= max_length)

        # 时间范围筛选
        start_time = request.args.get('start_time')
        if start_time:
            try:
                start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                query = query.filter(Price.created_at >= start)
            except ValueError:
                return jsonify({'code': 400, 'message': '无效的开始时间格式，应为YYYY-MM-DD HH:MM:SS'}), 400

        end_time = request.args.get('end_time')
        if end_time:
            try:
                end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                query = query.filter(Price.created_at <= end)
            except ValueError:
                return jsonify({'code': 400, 'message': '无效的结束时间格式，应为YYYY-MM-DD HH:MM:SS'}), 400

        # 排序处理
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 验证排序字段是否存在
        valid_fields = ['id', 'length', 'girth', 'price', 'weight', 'created_at', 'updated_at']
        if sort_by not in valid_fields:
            sort_by = 'created_at'

        # 应用排序
        if sort_order.lower() == 'asc':
            query = query.order_by(getattr(Price, sort_by).asc())
        else:
            query = query.order_by(getattr(Price, sort_by).desc())

        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page)
        prices = pagination.items

        # 构建响应数据
        result = {
            'code': 200,
            'message': '查询成功',
            'data': {
                'items': [price.to_dict() for price in prices],
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }

        return jsonify(result)

    except Exception as e:
        # 异常处理
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500