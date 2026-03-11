import { spawn } from 'child_process';
import path from 'path';

// Python执行路径适配
const getPythonExec = () => {
  // 线上Netlify环境用python3
  if (process.env.NETLIFY) return 'python3';
  // 本地Windows环境优先用python，不行再用py
  return process.platform === 'win32' ? 'python' : 'python3';
};

// 路径拼接：优先使用process.cwd()（项目根目录），兼容Netlify Dev临时目录问题
// 固定规则：Python 脚本都放在 netlify/functions/python_scripts 下
const getPythonScriptPath = (relativePath) => {
  // 线上环境：__dirname是函数实际目录
  // 本地Netlify Dev：__dirname是临时打包目录，process.cwd()是项目根目录
  if (process.env.NETLIFY) {
    // 线上环境直接使用__dirname
    return path.join(__dirname, relativePath);
  } else {
    // 本地开发环境：从项目根目录拼接路径
    return path.join(process.cwd(), 'netlify', 'functions', relativePath);
  }
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
    // 2. 获取请求路径（支持多种访问方式）
    let requestPath = null;

    // 方式1：从redirect传递的查询参数获取原始路径（推荐方式）
    if (event.queryStringParameters?.path) {
      requestPath = event.queryStringParameters.path;
    } else {
      // 方式2：直接从event.path提取（当直接访问函数路径时）
      const pathMatch = event.path.match(/\/api\/[^?#]+/);
      if (pathMatch) {
        requestPath = pathMatch[0];
      } else {
        // 方式3：尝试从各种头获取
        requestPath = event.path;
        const possibleHeaders = [
          'x-nf-original-url',
          'X-Nf-Original-Url',
          'X-NF-ORIGINAL-URL',
          'referer',
          'Referer'
        ];

        for (const header of possibleHeaders) {
          if (event.headers[header]) {
            const headerMatch = event.headers[header].match(/\/api\/[^?#]+/);
            if (headerMatch) {
              requestPath = headerMatch[0];
              break;
            }
          }
        }

        // 方式4：从rawUrl提取
        if (event.rawUrl) {
          const rawMatch = event.rawUrl.match(/\/api\/[^?#]+/);
          if (rawMatch) {
            requestPath = rawMatch[0];
          }
        }
      }
    }

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

    // 4. 拼接 Python 脚本完整路径
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
    const pythonExec = getPythonExec();
    const pythonResult = await new Promise((resolve, reject) => {
      const pythonProcess = spawn(pythonExec, [pythonScriptPath, paramsStr]);
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
        data: result
      })
    };

  } catch (error) {
    return handleError(error.toString());
  }
};
