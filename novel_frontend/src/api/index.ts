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
  recommend?: number
  latest_chapter?: string
  favorite_count?: number
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
  list: (params?: { page?: number; page_size?: number; category?: string; ordering?: string; search?: string; status?: string }) =>
    request.get('/novels/', { params }),

  detail: (id: number) =>
    request.get(`/novels/${id}/`),

  chapters: (id: number) =>
    request.get(`/novels/${id}/chapters/`),

  search: (q: string, page?: number) =>
    request.get('/novels/search/', { params: { q, page } }),

  recommend: (limit?: number) =>
    request.get('/novels/recommend/', { params: { limit } }),

  category_stats: () =>
    request.get('/novels/category_stats/'),
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

  logout: () =>
    request.post('/auth/logout/'),

  getUserInfo: () =>
    request.get('/auth/me/'),

  updateProfile: (data: Record<string, any>) =>
    request.put('/auth/update_profile/', data),
}

export const favoriteApi = {
  list: () =>
    request.get('/favorites/'),

  add: (novelId: number) =>
    request.post('/favorites/', { novel: novelId }),

  remove: (novelId: number) =>
    request.post('/favorites/delete_by_novel/', { novel_id: novelId }),

  check: (novelId: number) =>
    request.get('/favorites/check/', { params: { novel_id: novelId } }),
}

export const progressApi = {
  list: () =>
    request.get('/reading-progress/'),

  get: (novelId: number) =>
    request.get('/reading-progress/get_progress/', { params: { novel_id: novelId } }),

  update: (data: { novel_id: number; chapter_id: number; position: number }) =>
    request.post('/reading-progress/update_progress/', data),
}

export const bookmarkApi = {
  list: () =>
    request.get('/bookmarks/'),

  add: (data: { novel_id: number; chapter_id: number; position: number; note?: string }) =>
    request.post('/bookmarks/', data),

  remove: (id: number) =>
    request.delete(`/bookmarks/${id}/`),

  byChapter: (chapterId: number) =>
    request.get('/bookmarks/by_chapter/', { params: { chapter_id: chapterId } }),
}

export interface AuthorNovel {
  id: number
  title: string
  author: string
  cover: string
  description: string
  category: string
  tags: string
  status: number
  status_display: string
  audit_status: number
  audit_status_display: string
  word_count: number
  view_count: number
  chapter_count: number
  created_at: string
  updated_at: string
}

export interface AuthorChapter {
  id: number
  novel: number
  title: string
  content?: string
  chapter_order: number
  word_count: number
  publish_status: number
  publish_status_display: string
  created_at: string
  updated_at: string
}

export const authorApi = {
  novelList: () =>
    request.get('/author/novels/'),

  novelDetail: (id: number) =>
    request.get(`/author/novels/${id}/`),

  createNovel: (data: Partial<AuthorNovel>) =>
    request.post('/author/novels/', data),

  updateNovel: (id: number, data: Partial<AuthorNovel>) =>
    request.patch(`/author/novels/${id}/`, data),

  deleteNovel: (id: number) =>
    request.delete(`/author/novels/${id}/`),

  publishNovel: (id: number) =>
    request.post(`/author/novels/${id}/publish/`),

  takeDownNovel: (id: number) =>
    request.post(`/author/novels/${id}/take_down/`),

  stats: () =>
    request.get('/author/novels/stats/'),

  chapterList: (novelId: number) =>
    request.get('/author/chapters/', { params: { novel: novelId } }),

  chapterDetail: (id: number) =>
    request.get(`/author/chapters/${id}/`),

  createChapter: (data: { novel: number; title: string; content: string; chapter_order?: number; publish_status?: number }) =>
    request.post('/author/chapters/', data),

  updateChapter: (id: number, data: Partial<AuthorChapter>) =>
    request.patch(`/author/chapters/${id}/`, data),

  deleteChapter: (id: number) =>
    request.delete(`/author/chapters/${id}/`),

  publishChapter: (id: number) =>
    request.post(`/author/chapters/${id}/publish/`),

  uploadCover: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/author/novels/upload_cover/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export interface NovelComment {
  id: number
  novel: number
  user: number
  username: string
  user_avatar: string
  content: string
  rating: number
  created_at: string
}

export const commentApi = {
  list: (novelId: number, page = 1) =>
    request.get('/comments/', { params: { novel: novelId, page } }),

  add: (data: { novel: number; content: string; rating?: number }) =>
    request.post('/comments/', data),

  remove: (id: number) =>
    request.delete(`/comments/${id}/`),

  stats: (novelId: number) =>
    request.get('/comments/stats/', { params: { novel: novelId } }),
}
