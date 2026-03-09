# Vue + Flask Netlify Demo

这是一个部署在 Netlify 平台的 Vue 3 + Flask 全栈项目模板。

## 技术栈

- **前端**: Vue 3 + Vite + Axios
- **后端**: Flask + Netlify Functions (无服务器架构)
- **部署**: Netlify

## 项目结构

```
├── netlify/
│   └── functions/
│       └── api.py          # Flask 后端 API
├── src/
│   ├── App.vue             # 主组件
│   └── main.js             # Vue 入口文件
├── public/                 # 静态资源目录
├── index.html              # HTML 入口
├── vite.config.js          # Vite 配置
├── netlify.toml            # Netlify 部署配置
├── package.json            # Node 依赖
├── requirements.txt        # Python 依赖
└── runtime.txt             # Python 版本指定
```

## 本地开发

### 前置要求
- Node.js 18+
- Python 3.11+
- Netlify CLI

### 安装依赖

```bash
# 安装前端依赖
npm install

# 安装 Python 依赖
pip install -r requirements.txt
```

### 本地运行

```bash
# 使用 Netlify CLI 启动开发服务器（同时运行前端和后端函数）
npm run netlify:dev

# 或单独运行前端开发服务器
npm run dev
```

访问地址：
- 前端: http://localhost:8888
- 后端API: http://localhost:8888/.netlify/functions/api

## 部署到 Netlify

### 方法1：一键部署

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=你的仓库地址)

### 方法2：手动部署

1. 将代码推送到 GitHub/GitLab/Bitbucket 仓库
2. 在 Netlify 中导入仓库
3. 配置会自动识别 `netlify.toml` 文件，无需额外配置
4. 点击部署即可

## API 示例

### 基础接口
- `GET /.netlify/functions/api` - 基础测试接口
- `GET /.netlify/functions/api/api/data` - 获取示例数据

### 重定向便捷访问
配置了重定向规则，你也可以使用更简洁的路径：
- `GET /api` - 等价于 `/.netlify/functions/api`
- `GET /api/data` - 等价于 `/.netlify/functions/api/api/data`

## 自定义配置

### 修改前端端口
编辑 `vite.config.js` 中的 `server.port` 配置。

### 添加新的 API 路由
在 `netlify/functions/api.py` 中添加新的 Flask 路由即可。

### 配置环境变量
在 Netlify 控制台的 "Site settings" -> "Environment variables" 中添加，后端可以通过 `os.environ.get()` 获取。

## 注意事项

1. Netlify Functions 有执行时间限制（免费版最多 10 秒）
2. 无状态后端，不要在内存中存储数据
3. 数据库建议使用第三方云数据库服务
