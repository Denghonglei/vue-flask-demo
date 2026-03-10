import os
import sys

# 测试路径
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"当前目录: {current_dir}")

backend_path = os.path.join(current_dir, 'backend')
print(f"backend路径: {backend_path}")
print(f"backend是否存在: {os.path.exists(backend_path)}")

sys.path.insert(0, current_dir)
print(f"sys.path: {sys.path[:3]}")

from backend.app import app
print("导入成功！")
