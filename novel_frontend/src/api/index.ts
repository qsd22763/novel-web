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
    request.get<PaginatedResponse<Novel>>('/novels/', { params }),

  detail: (id: number) =>
    request.get<Novel>(`/novels/${id}/`),

  chapters: (id: number) =>
    request.get(`/novels/${id}/chapters/`),

  search: (q: string, page?: number) =>
    request.get<PaginatedResponse<Novel>>('/novels/search/', { params: { q, page } }),

  recommend: (limit?: number) =>
    request.get<Novel[]>('/novels/recommend/', { params: { limit } }),
}

export const chapterApi = {
  detail: (id: number) =>
    request.get<Chapter>(`/chapters/${id}/`),
}

interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    email: string
  }
}

interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
}

export const authApi = {
  login: (data: { username: string; password: string }) =>
    request.post<LoginResponse>('/auth/login/', data),

  register: (data: RegisterData) =>
    request.post<any>('/auth/register/', data),

  getUserInfo: () =>
    request.get<any>('/auth/user/'),

  updateUserInfo: (data: any) =>
    request.put<any>('/auth/user/', data),
}

interface FavoriteNovel {
  id: number
  novel: Novel
  created_at: string
}

export const favoriteApi = {
  list: () =>
    request.get<FavoriteNovel[]>('/favorites/'),

  add: (novelId: number) =>
    request.post<any>('/favorites/', { novel_id: novelId }),

  remove: (novelId: number) =>
    request.delete<any>(`/favorites/${novelId}/`),
}

interface ReadingProgress {
  id: number
  novel_id: number
  chapter_id: number
  position: number
  updated_at: string
}

export const progressApi = {
  get: (novelId: number) =>
    request.get<ReadingProgress>(`/progress/${novelId}/`),

  update: (novelId: number, data: { chapter_id: number; position: number }) =>
    request.put<ReadingProgress>(`/progress/${novelId}/`, data),
}
