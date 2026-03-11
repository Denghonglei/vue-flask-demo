import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 这里可以添加token等全局请求头
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const res = response.data
    // 业务错误处理
    if (res.code !== 200 && res.code !== 0) {
      alert(res.message || res.errorMsg || '请求失败')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res
  },
  (error) => {
    console.error('API Error:', error)
    let message = '网络连接失败，请检查网络'
    if (error.response) {
      switch (error.response.status) {
        case 404:
          message = '请求的接口不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || error.response.data?.errorMsg || `请求失败(${error.response.status})`
      }
    }
    alert(message)
    return Promise.reject(error)
  }
)

// 基础请求方法
export const get = (url, params = {}, config = {}) => {
  return api.get(url, { params, ...config })
}

export const post = (url, data = {}, config = {}) => {
  return api.post(url, data, config)
}

// 业务API接口
export const hairEstimate = (data) => post('/hair/estimate', data)
export const messageSubmit = (data) => post('/message/submit', data)
export const getQuestions = (params) => get('/list-questions', params)
export const preBook = (data) => post('/pre-book', data)

export default api
