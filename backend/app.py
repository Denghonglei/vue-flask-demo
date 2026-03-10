# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 全局跨域

# 定义所有接口
@app.route('/api/hair/estimate', methods=['GET', 'POST'])
def hair_estimate():
    return jsonify({
        "code": 200,
        "message": "hair_estimate 接口调用成功",
        "data": {"estimate": "1000-2000 元"}
    })

@app.route('/api/message/submit', methods=['POST'])
def message_submit():
    return jsonify({
        "code": 200,
        "message": "留言提交成功",
        "data": {}
    })

@app.route('/api/list-questions', methods=['GET'])
def list_questions():
    return jsonify({
        "code": 200,
        "message": "问题列表获取成功",
        "data": ["问题1", "问题2", "问题3"]
    })

@app.route('/api/pre-book', methods=['POST'])
def pre_book():
    return jsonify({
        "code": 200,
        "message": "预约成功",
        "data": {}
    })

# 本地运行入口
if __name__ == '__main__':
    app.run(debug=True)