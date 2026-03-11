import { spawn } from 'child_process';
import path from 'path';

// 🔥 核心修复：直接基于当前工作目录拼接路径（无需 __dirname）
// 固定规则：Python 脚本都放在 functions/python_scripts 下
const getPythonScriptPath = (relativePath) => {
  // 拼接路径：当前工作目录 → netlify → functions → 传入的相对路径
  return path.join(process.cwd(), 'netlify', 'functions', relativePath);
};

// 路由映射表（请求路径 → Python 脚本相对路径）
const routeMap = {
  '/api/user/info': 'python_scripts/user_info.py',
  '/api/hair/estimate': 'python_scripts/hair_estimate.py',
  '/api/message/submit': 'python_scripts/message_submit.py',
  '/api/list-questions': 'python_scripts/list_questions.py',
  '/api/pre-book': 'python_scripts/pre_book.py'
};

// 统一响应头
const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
});

// 统一错误处理
const handleError = (message) => ({
  statusCode: 500,
  headers: getHeaders(),
  body: JSON.stringify({ success: false, message })
});

// 统一入口函数
export const handler = async (event, context) => {
  // 1. 处理 OPTIONS 预检请求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: getHeaders(),
      body: JSON.stringify({ success: true })
    };
  }

  try {
    // 2. 获取请求路径
    const requestPath = event.path;

    // 3. 匹配对应的 Python 脚本相对路径
    const pythonScriptRelativePath = routeMap[requestPath];
    if (!pythonScriptRelativePath) {
      return {
        statusCode: 404,
        headers: getHeaders(),
        body: JSON.stringify({
          success: false,
          message: `接口不存在: ${requestPath}`,
          availableRoutes: Object.keys(routeMap)
        })
      };
    }

    // 4. 拼接 Python 脚本完整路径（核心：用 process.cwd() 替代 __dirname）
    const pythonScriptPath = getPythonScriptPath(pythonScriptRelativePath);

    // 5. 解析请求参数
    let params = {};
    if (event.httpMethod === 'GET') {
      params = event.queryStringParameters || {};
    } else if (event.httpMethod === 'POST') {
      params = JSON.parse(event.body || '{}');
    }

    // 6. 执行 Python 脚本（使用spawn传递参数数组，彻底解决转义问题）
    const paramsStr = JSON.stringify(params);
    const pythonResult = await new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [pythonScriptPath, paramsStr]);
      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(`Python 执行失败: ${stderr} | 脚本路径: ${pythonScriptPath}`);
        } else {
          resolve(stdout.trim());
        }
      });

      pythonProcess.on('error', (error) => {
        reject(`Python 启动失败: ${error.message}`);
      });
    });

    // 7. 解析并返回结果
    const result = JSON.parse(pythonResult);
    return {
      statusCode: 200,
      headers: getHeaders(),
      body: JSON.stringify({
        success: true,
        data: result,
        requestPath,
        requestParams: params,
        scriptPath: pythonScriptPath // 调试用：返回脚本路径，方便排查
      })
    };

  } catch (error) {
    return handleError(error.toString());
  }
};