import axios, { type AxiosRequestConfig, type AxiosError } from 'axios'
import router from '../router'

interface RequestInstance {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
}

// === 配置 ===
const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const REQUEST_TIMEOUT = 60000 // 60秒，适配 Vercel 冷启动
const MAX_RETRIES = 2 // 最大重试次数
const RETRY_DELAY = 2000 // 重试间隔(ms)

const instance = axios.create({
  baseURL: API_BASE,
  timeout: REQUEST_TIMEOUT,
  withCredentials: true,
})

// === 判断是否可重试的错误 ===
function isRetryableError(error: AxiosError): boolean {
  const code = error.code
  // 网络错误、超时、连接重置等可重试
  if (!error.response) return true // 无响应（网络层错误）
  if (code === 'ECONNABORTED') return true // 超时
  if (code === 'ERR_NETWORK' || code === 'ECONNRESET' || code === 'ETIMEDOUT') return true
  // 5xx 服务器错误可重试
  if (error.response.status >= 500) return true
  return false
}

// === 延迟函数 ===
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// === 请求拦截器 ===
instance.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`)
    return config
  },
  (error) => {
    console.error('[API] Request Error:', error.message)
    return Promise.reject(error)
  }
)

// === 响应拦截器（含自动重试）===
instance.interceptors.response.use(
  (response) => response.data,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { __retryCount?: number }
    const url = config?.url || ''
    const method = config?.method?.toUpperCase() || ''
    const fullUrl = `${API_BASE}${url}`

    // 初始化重试计数
    if (config.__retryCount === undefined) {
      config.__retryCount = 0
    }

    // 详细错误日志
    const status = error.response?.status
    const code = error.code
    console.error(
      `[API Error] ${method} ${fullUrl}`,
      `| status: ${status || 'N/A'}`,
      `| code: ${code || 'N/A'}`,
      `| message: ${error.message}`
    )

    // 自动重试逻辑
    if (isRetryableError(error) && config.__retryCount! < MAX_RETRIES) {
      config.__retryCount!++
      console.warn(
        `[API Retry] ${method} ${fullUrl} | 第 ${config.__retryCount}/${MAX_RETRIES} 次重试...`
      )
      await delay(RETRY_DELAY)
      return instance(config)
    }

    // 重试耗尽后的处理
    if (config.__retryCount! >= MAX_RETRIES && isRetryableError(error)) {
      console.error(
        `[API Failed] ${method} ${fullUrl} | 已重试 ${MAX_RETRIES} 次仍失败`
      )
    }

    // 认证错误处理
    if (status === 401 || status === 403) {
      const isAuthApi = /favorites|reading-progress|bookmarks|author|auth\/me|comments/.test(url)
      if (isAuthApi) {
        localStorage.removeItem('user')
        const currentPath = router.currentRoute.value.path
        if (currentPath !== '/login') {
          router.push('/login')
        }
      }
    }

    return Promise.reject(error)
  }
)

const request = instance as unknown as RequestInstance
export default request
