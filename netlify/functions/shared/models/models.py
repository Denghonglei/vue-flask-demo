import json
from datetime import datetime

import inspect

from flask_app import db


class User(db.Model):

    __tablename__ = 'user'

    '''
    role:判断 user--普通用户  admin--管理员  member--会员
    '''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    membership_expiry = db.Column(db.DateTime, nullable=True)
    date_joined = db.Column(db.DateTime, nullable=True)

    openid = db.Column(db.String(80), unique=True, nullable=True)
    session_key = db.Column(db.String(50), nullable=True)
    unionid = db.Column(db.String(80), nullable=True)

    def to_dict(self, include_sensitive=False):
        user_dict = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'membership_expiry': self.membership_expiry.isoformat() if self.membership_expiry else None,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
        }
        if include_sensitive:
            user_dict['openid'] = self.openid
            user_dict['session_key'] = self.session_key
        return user_dict


class Hair(db.Model):

    __tablename__ = 'hair'

    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    girth = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.openid'), nullable=False)
    is_permed = db.Column(db.Boolean, default=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('hairs', lazy=True))
    is_delete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'length': self.length,
            'girth': self.girth,
            'user_id': self.user_id,
            'is_permed': self.is_permed,
            'details': self.details,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字段[1](@ref)
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间字段[1](@ref)
        }


class Price(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, nullable=False)
    girth = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.openid'), nullable=False)
    is_dyed = db.Column(db.Boolean, default=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('prices', lazy=True))
    method = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_delete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'length': self.length,
            'girth': self.girth,
            'user_id': self.user_id,
            'is_dyed': self.is_dyed,
            'details': json.loads(self.details),
            'weight': self.weight,
            'price': self.price,
            'cut_method': self.method,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间字段[1](@ref)
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间字段[1](@ref)
        }


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('user.openid'), nullable=False)
    expected_time = db.Column(db.DateTime, nullable=False)
    expected_location = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='initial')  # initial, in_progress, completed
    actual_price = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    hair_id = db.Column(db.Integer, db.ForeignKey('hair.id'), nullable=True)  # 关联Hair信息
    price_id = db.Column(db.Integer, db.ForeignKey('price.id'), nullable=True)  # 关联Price信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    hair = db.relationship('Hair', backref=db.backref('appointments', lazy=True))
    price = db.relationship('Price', backref=db.backref('appointments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expected_time': self.expected_time.isoformat(),
            'expected_location': self.expected_location,
            'contact_number': self.contact_number,
            'status': self.status,
            'actual_price': self.actual_price,
            'weight': self.weight,
            'hair_id': self.hair_id,
            'price_id': self.price_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }



class ConfigDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 类型字段，存储数据的类型，比如 'string'、'number' 等
    data_type = db.Column(db.String(50))
    # key 字段，唯一标识一条记录
    key = db.Column(db.String(100), unique=True, nullable=False)
    # value 字段，存储具体的数据值
    value = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'data_type': self.data_type,
            'key': self.key,
            'value': self.value
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# 数据模型、增加预约表
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_order_number(self):
        return f"HS{self.date.strftime('%Y%m%d')}{self.id:04d}"


# 定义数据模型
class ExpressOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)  # 唯一快递单号
    express_company = db.Column(db.String(50), nullable=False)
    is_estimated = db.Column(db.Boolean, default=False)
    is_know_rules = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExpressOrder {self.tracking_number}>'


# 修改后（正确示例）
from flask_app import app  # 导入应用实例

with app.app_context():  # 手动创建应用上下文
    db.create_all()