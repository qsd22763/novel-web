import request from '../utils/request'

export interface Novel {
  id: number
  title: string
  author: string
  cover: string
  category: string
  status: number
  word_count: number
  view_count: number
  description?: string
  chapter_count?: number
  updated_at?: string
}

export interface Chapter {
  id: number
  novel_id?: number
  novel_title?: string
  title: string
  content?: string
  chapter_order: number
  word_count: number
  created_at: string
  prev_chapter?: { id: number; title: string }
  next_chapter?: { id: number; title: string }
}

export interface PaginatedResponse<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

export const novelApi = {
  list: (params?: { page?: number; page_size?: number; category?: string; ordering?: string }) =>
    request.get('/novels/', { params }),

  detail: (id: number) =>
    request.get(`/novels/${id}/`),

  chapters: (id: number) =>
    request.get(`/novels/${id}/chapters/`),

  search: (q: string, page?: number) =>
    request.get('/novels/search/', { params: { q, page } }),

  recommend: (limit?: number) =>
    request.get('/novels/recommend/', { params: { limit } }),
}

export const chapterApi = {
  detail: (id: number) =>
    request.get(`/chapters/${id}/`),
}

export const authApi = {
  login: (data: { username: string; password: string }) =>
    request.post('/auth/login/', data),

  register: (data: { username: string; email: string; password: string; password_confirm: string }) =>
    request.post('/auth/register/', data),

  getUserInfo: () =>
    request.get('/auth/user/'),

  updateUserInfo: (data: any) =>
    request.put('/auth/user/', data),
}

export const favoriteApi = {
  list: () =>
    request.get('/favorites/'),

  add: (novelId: number) =>
    request.post('/favorites/', { novel_id: novelId }),

  remove: (novelId: number) =>
    request.delete(`/favorites/${novelId}/`),
}

export const progressApi = {
  get: (novelId: number) =>
    request.get(`/progress/${novelId}/`),

  update: (novelId: number, data: { chapter_id: number; position: number }) =>
    request.put(`/progress/${novelId}/`, data),
}
