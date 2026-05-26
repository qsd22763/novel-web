import axios, { AxiosRequestConfig, AxiosResponse, AxiosInstance } from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
})

request.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

type RequestMethod = 'get' | 'post' | 'put' | 'delete' | 'patch'

function createTypedRequest() {
  const methods = ['get', 'post', 'put', 'delete', 'patch'] as const

  const api: Record<typeof methods[number], <T>(url: string, config?: AxiosRequestConfig) => Promise<T>> = {
    get: <T>(url: string, config?: AxiosRequestConfig) => request.get<T>(url, config) as Promise<T>,
    post: <T>(url: string, config?: AxiosRequestConfig) => request.post<T>(url, config?.data, { params: config?.params }) as Promise<T>,
    put: <T>(url: string, config?: AxiosRequestConfig) => request.put<T>(url, config?.data, { params: config?.params }) as Promise<T>,
    delete: <T>(url: string, config?: AxiosRequestConfig) => request.delete<T>(url, { params: config?.params }) as Promise<T>,
    patch: <T>(url: string, config?: AxiosRequestConfig) => request.patch<T>(url, config?.data, { params: config?.params }) as Promise<T>,
  }

  return api
}

export default createTypedRequest()
