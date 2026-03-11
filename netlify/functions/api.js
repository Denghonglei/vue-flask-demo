import { spawn } from 'child_process';
import path from 'path';

// Python执行路径适配：线上Netlify环境用python3，本地用python
const pythonExec = process.env.NETLIFY ? 'python3' : 'python';

// 路径拼接：使用 __dirname 确保本地和线上环境路径一致
// 固定规则：Python 脚本都放在 functions/python_scripts 下
const getPythonScriptPath = (relativePath) => {
  // 拼接路径：当前api.js所在目录 → 传入的相对路径
  return path.join(__dirname, relativePath);
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
  // 调试日志：打印所有请求信息
  console.log('=== 收到请求 ===');
  console.log('请求方法:', event.httpMethod);
  console.log('event.path:', event.path);
  console.log('x-nf-original-url:', event.headers['x-nf-original-url']);
  console.log('所有headers:', JSON.stringify(event.headers, null, 2));

  // 1. 处理 OPTIONS 预检请求
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: getHeaders(),
      body: JSON.stringify({ success: true })
    };
  }

  try {
    // 2. 获取请求路径（兼容本地和线上环境）
    console.log('所有headers的键:', Object.keys(event.headers).map(k => `${k}: ${event.headers[k]}`));

    // 尝试从各种可能的头获取原始路径（Netlify的头大小写不固定）
    let requestPath = event.path;
    const possibleHeaders = [
      'x-nf-original-url',
      'X-Nf-Original-Url',
      'X-NF-ORIGINAL-URL',
      'referer',
      'Referer'
    ];

    for (const header of possibleHeaders) {
      if (event.headers[header]) {
        console.log(`找到头 ${header}: ${event.headers[header]}`);
        requestPath = event.headers[header];
        break;
      }
    }

    // 如果有rawUrl字段也尝试使用
    if (event.rawUrl) {
      console.log('找到rawUrl:', event.rawUrl);
      requestPath = event.rawUrl;
    }

    console.log('原始requestPath:', requestPath);

    // 提取/api/开头的路径部分
    const apiPathMatch = requestPath.match(/\/api\/[^?#]+/);
    if (apiPathMatch) {
      requestPath = apiPathMatch[0];
    } else {
      // 备用方案：如果还是找不到，尝试从请求中提取路径
      console.log('未找到/api/路径，使用备用方案');
      // 如果直接访问函数，尝试从query或者其他地方获取
      if (event.queryStringParameters?.path) {
        requestPath = event.queryStringParameters.path;
      }
    }
    console.log('处理后requestPath:', requestPath);

    // 3. 匹配对应的 Python 脚本相对路径
    const pythonScriptRelativePath = routeMap[requestPath];
    console.log('匹配到的脚本相对路径:', pythonScriptRelativePath);

    if (!pythonScriptRelativePath) {
      console.log('接口不存在，可用路由:', Object.keys(routeMap));
      return {
        statusCode: 404,
        headers: getHeaders(),
        body: JSON.stringify({
          success: false,
          message: `接口不存在: ${requestPath}`,
          availableRoutes: Object.keys(routeMap),
          debug: {
            originalPath: event.headers['x-nf-original-url'] || event.path,
            processedPath: requestPath
          }
        })
      };
    }

    // 4. 拼接 Python 脚本完整路径
    const pythonScriptPath = getPythonScriptPath(pythonScriptRelativePath);
    console.log('脚本完整路径:', pythonScriptPath);

    // 调试：检查文件是否存在
    const fs = await import('fs');
    const scriptExists = fs.existsSync(pythonScriptPath);
    console.log('脚本文件是否存在:', scriptExists);

    // 调试：列出当前目录结构
    const currentDir = __dirname;
    console.log('当前目录:', currentDir);
    const filesInDir = fs.readdirSync(currentDir);
    console.log('当前目录下的文件:', JSON.stringify(filesInDir, null, 2));

    // 检查python_scripts目录是否存在（尝试多个可能路径）
    const possiblePythonDirs = [
      path.join(__dirname, 'python_scripts'),
      path.join(process.cwd(), 'python_scripts'),
      path.join(__dirname, '..', 'python_scripts'),
      '/opt/python_scripts'
    ];

    let pythonScriptsDir = null;
    for (const dir of possiblePythonDirs) {
      if (fs.existsSync(dir)) {
        pythonScriptsDir = dir;
        console.log('找到python_scripts目录:', dir);
        const pythonScriptsFiles = fs.readdirSync(dir);
        console.log('python_scripts目录下的文件:', JSON.stringify(pythonScriptsFiles, null, 2));
        break;
      } else {
        console.log('目录不存在:', dir);
      }
    }

    if (!pythonScriptsDir) {
      console.error('未找到python_scripts目录！');
      return {
        statusCode: 500,
        headers: getHeaders(),
        body: JSON.stringify({
          success: false,
          message: '服务器配置错误：Python脚本目录不存在',
          debug: {
            possibleDirs: possiblePythonDirs,
            cwd: process.cwd(),
            dirname: __dirname
          }
        })
      };
    }

    // 5. 解析请求参数
    let params = {};
    if (event.httpMethod === 'GET') {
      params = event.queryStringParameters || {};
    } else if (event.httpMethod === 'POST') {
      params = JSON.parse(event.body || '{}');
    }

    // 6. 执行 Python 脚本（使用spawn传递参数数组，彻底解决转义问题）
    const paramsStr = JSON.stringify(params);
    console.log('Python执行路径:', pythonExec);
    console.log('传递的参数:', paramsStr);

    const pythonResult = await new Promise((resolve, reject) => {
      const pythonProcess = spawn(pythonExec, [pythonScriptPath, paramsStr]);
      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        const str = data.toString();
        console.log('Python stdout:', str);
        stdout += str;
      });

      pythonProcess.stderr.on('data', (data) => {
        const str = data.toString();
        console.error('Python stderr:', str);
        stderr += str;
      });

      pythonProcess.on('close', (code) => {
        console.log('Python进程退出码:', code);
        if (code !== 0) {
          const errorMsg = `Python 执行失败: ${stderr} | 脚本路径: ${pythonScriptPath} | 退出码: ${code}`;
          console.error(errorMsg);
          reject(errorMsg);
        } else {
          console.log('Python执行成功，输出:', stdout.trim());
          resolve(stdout.trim());
        }
      });

      pythonProcess.on('error', (error) => {
        const errorMsg = `Python 启动失败: ${error.message}`;
        console.error(errorMsg);
        reject(errorMsg);
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
    console.error('全局错误:', error.toString());
    console.error('错误堆栈:', error.stack);
    return handleError(error.toString());
  }
};