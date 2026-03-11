# netlify/functions/api_logic.py
import sys
import json

def main(params):
    """
    业务逻辑处理函数
    :param params: 前端传递的参数（字典）
    :return: 处理后的结果（字典）
    """
    # 示例：处理参数并返回数据
    user_id = params.get('user_id', 'unknown')
    action = params.get('action', 'query')
    
    # 模拟业务逻辑
    result = {
        'user_id': user_id,
        'action': action,
        'message': f'{action} 操作成功',
        'status': 'success'
    }
    return result

if __name__ == '__main__':
    # 接收 Node.js 传递的参数（命令行参数）
    if len(sys.argv) > 1:
        params_str = sys.argv[1]
        params = json.loads(params_str)
    else:
        params = {}
    
    # 执行业务逻辑
    result = main(params)
    
    # 将结果转为 JSON 输出（供 Node.js 读取）
    print(json.dumps(result, ensure_ascii=False))