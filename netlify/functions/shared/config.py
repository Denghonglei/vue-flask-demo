class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WECHAT_APPID = "wx8a55523609914d0c"
    WECHAT_APPSECRET = "70d71c23e49b63b77605c631848bd083"

    # 邮件相关
    MAIL_SERVER = 'smtp.163.com'  # 例如: 'smtp.gmail.com'
    MAIL_PORT = 587  # 通常为465或587
    MAIL_USE_TLS = True  # 使用TLS
    MAIL_USE_SSL = False  # 使用SSL（根据需要选择）
    MAIL_USERNAME = 'ln80656155@163.com'
    MAIL_PASSWORD = '1234567890x'  # 你的邮箱密码或应用专用密码
    MAIL_DEFAULT_SENDER = 'ln80656155@163.com'
