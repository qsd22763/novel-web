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

  homeData: () =>
    request.get('/novels/home_data/'),
}

export const chapterApi = {
  detail: (id: number) =>
    request.get(`/chapters/${id}/`),
}

export const authApi = {
  login: (data: { username: string; password: string }) =>
    request.post('/auth/login/', data),

  adminLogin: (data: { username: string; password: string }) =>
    request.post('/auth/admin_login/', data),

  register: (data: { username: string; email: string; password: string; password_confirm: string; verification_code?: string }) =>
    request.post('/auth/register/', data),

  sendVerificationCode: (email: string) =>
    request.post('/auth/send_verification_code/', { email }),

  logout: () =>
    request.post('/auth/logout/'),

  getUserInfo: () =>
    request.get('/auth/me/'),

  updateProfile: (data: Record<string, any>) =>
    request.put('/auth/update_profile/', data),

  changePassword: (data: { old_password: string; new_password: string }) =>
    request.post('/auth/change_password/', data),

  // 第三方OAuth登录
  getQQAuthUrl: () =>
    request.get('/auth/qq_login/', { params: {} }),

  qqCallback: (code: string, state?: string) =>
    request.get('/auth/qq_login/', { params: { code, state } }),

  wechatLogin: (code: string, state?: string) =>
    request.get('/auth/wechat_login/', { params: { code, state } }),

  oauthCallback: (provider: 'qq' | 'wechat', code: string, state?: string) =>
    request.get('/auth/oauth_callback/', { params: { provider, code, state } }),
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

  add: (data: { novel: number; chapter: number; position: number; note?: string }) =>
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

export interface DashboardStats {
  total_books: number
  total_users: number
  today_reads: number
  new_comments: number
  books_change: number
  users_change: number
  reads_change: number
  comments_change: number
}

export interface AdminAdvertisement {
  id: number
  title: string
  image_url: string
  link_url: string
  position: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface AdminAnnouncement {
  id: number
  title: string
  content: string
  announcement_type: 'notice' | 'maintenance' | 'activity'
  is_pinned: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  announcement_type_display: string
}

export interface AdminBook {
  id: number
  title: string
  author: string
  cover: string
  category: string
  status: number
  status_display: string
  word_count: number
  view_count: number
  chapter_count: number
  favorite_count: number
  audit_status: number
  audit_status_display: string
  created_at: string
  updated_at: string
}

export const adminApi = {
  dashboardStats: () =>
    request.get<DashboardStats>('/admin/books/dashboard_stats/'),

  advertisementList: (params?: { page?: number; page_size?: number; is_active?: boolean }) =>
    request.get<PaginatedResponse<AdminAdvertisement>>('/admin/advertisements/', { params }),

  advertisementDetail: (id: number) =>
    request.get<AdminAdvertisement>(`/admin/advertisements/${id}/`),

  createAdvertisement: (data: Partial<AdminAdvertisement>) =>
    request.post<AdminAdvertisement>('/admin/advertisements/', data),

  updateAdvertisement: (id: number, data: Partial<AdminAdvertisement>) =>
    request.patch<AdminAdvertisement>(`/admin/advertisements/${id}/`, data),

  deleteAdvertisement: (id: number) =>
    request.delete(`/admin/advertisements/${id}/`),

  toggleAdvertisementActive: (id: number) =>
    request.post(`/admin/advertisements/${id}/toggle_active/`),

  announcement: {
    list: (params?: { page?: number; page_size?: number; announcement_type?: string; is_active?: boolean | null }) =>
      request.get<PaginatedResponse<AdminAnnouncement>>('/admin/announcements/', { params }),

    create: (data: Partial<AdminAnnouncement>) =>
      request.post<AdminAnnouncement>('/admin/announcements/', data),

    update: (id: number, data: Partial<AdminAnnouncement>) =>
      request.patch<AdminAnnouncement>(`/admin/announcements/${id}/`, data),

    delete: (id: number) =>
      request.delete(`/admin/announcements/${id}/`),

    togglePin: (id: number) =>
      request.post(`/admin/announcements/${id}/toggle_pin/`),

    publish: (id: number) =>
      request.post(`/admin/announcements/${id}/publish/`),

    withdraw: (id: number) =>
      request.post(`/admin/announcements/${id}/withdraw/`),
  },

  bookList: (params?: { page?: number; page_size?: number; category?: string; search?: string; status?: string }) =>
    request.get<PaginatedResponse<AdminBook>>('/admin/books/', { params }),

  bookDetail: (id: number) =>
    request.get<AdminBook>(`/admin/books/${id}/`),

  updateBookStatus: (id: number, data: { status: number }) =>
    request.patch(`/admin/books/${id}/`, data),

  batchUpdateBooks: (ids: number[], action: 'approve' | 'reject' | 'delete') =>
    request.post('/admin/books/batch_action/', { ids, action }),

  exportBooks: (params?: { category?: string; status?: string; audit_status?: string; search?: string; word_count_min?: string; word_count_max?: string }) =>
    request.get('/admin/books/export_excel/', { params, responseType: 'blob' }),

  // ── 新书审核 ──
  reviewList: (params?: { page?: number; page_size?: number; audit_status?: string; search?: string }) =>
    request.get<PaginatedResponse<AdminBook>>('/admin/books/', { params: { ...params, audit_status: params?.audit_status || '1' } }),

  approveBook: (id: number) =>
    request.post(`/admin/books/${id}/review_approve/`),

  rejectBook: (id: number, reason: string) =>
    request.post(`/admin/books/${id}/review_reject/`, { reject_reason: reason }),

  category: {
    list: (params?: any) =>
      request.get('/admin/categories/', { params }),

    tree: () =>
      request.get('/admin/categories/tree/'),

    create: (data: any) =>
      request.post('/admin/categories/', data),

    update: (id: number, data: any) =>
      request.patch(`/admin/categories/${id}/`, data),

    delete: (id: number) =>
      request.delete(`/admin/categories/${id}/`),

    toggle: (id: number) =>
      request.post(`/admin/categories/${id}/toggle/`),
  },

  dashboard: {
    fullStats: () =>
      request.get('/admin/books/full_stats/'),
  },
}

// 签到相关
export const signinApi = {
  doSignin: () =>
    request.post('/signin/do_signin/'),

  getStatus: () =>
    request.get('/signin/status/'),
}

// 充值相关
export const rechargeApi = {
  getPlans: () =>
    request.get('/recharge/'),

  createOrder: (planId: number) =>
    request.post('/recharge/create_order/', { plan_id: planId }),

  myOrders: () =>
    request.get('/recharge/my_orders/'),

  vipStatus: () =>
    request.get('/recharge/vip_status/'),
}
