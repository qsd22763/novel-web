import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default request
