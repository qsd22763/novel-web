import axios, { type AxiosRequestConfig } from 'axios'
import router from '../router'

interface RequestInstance {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
}

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true,
})

instance.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      const url = error.config?.url || ''
      const isAuthApi = /favorites|reading-progress|bookmarks|author|auth\/me|comments/.test(url)
      if (isAuthApi) {
        localStorage.removeItem('user')
        const currentPath = router.currentRoute.value.path
        if (currentPath !== '/login') {
          router.push('/login')
        }
      }
    }
    if (!error.response || status >= 500) {
      console.error('API Error:', error)
    }
    return Promise.reject(error)
  }
)

const request = instance as unknown as RequestInstance

export default request
