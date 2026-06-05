import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
    },
    {
      path: '/novels',
      name: 'NovelList',
      component: () => import('../views/NovelList.vue'),
    },
    {
      path: '/novels/:id',
      name: 'NovelDetail',
      component: () => import('../views/NovelDetail.vue'),
    },
    {
      path: '/read/:id',
      name: 'Reader',
      component: () => import('../views/Reader.vue'),
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('../views/Search.vue'),
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/user',
      name: 'UserCenter',
      component: () => import('../views/UserCenter.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/user/signin',
      name: 'SignIn',
      component: () => import('../views/SignIn.vue'),
      meta: { title: '每日签到', requiresAuth: true },
    },
    {
      path: '/user/recharge',
      name: 'Recharge',
      component: () => import('../views/Recharge.vue'),
      meta: { title: '会员充值', requiresAuth: true },
    },
    {
      path: '/rankings',
      name: 'Rankings',
      component: () => import('../views/Rankings.vue'),
    },
    {
      path: '/author',
      name: 'AuthorCenter',
      component: () => import('../views/AuthorCenter.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/author/novel/new',
      name: 'AuthorNovelCreate',
      component: () => import('../views/AuthorNovelEdit.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/author/novel/:id/edit',
      name: 'AuthorNovelEdit',
      component: () => import('../views/AuthorNovelEdit.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/author/novel/:novelId/chapters',
      name: 'AuthorChapterList',
      component: () => import('../views/AuthorChapterList.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/author/novel/:novelId/chapter/new',
      name: 'AuthorChapterCreate',
      component: () => import('../views/AuthorChapterEdit.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/author/novel/:novelId/chapter/:id/edit',
      name: 'AuthorChapterEdit',
      component: () => import('../views/AuthorChapterEdit.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('../views/admin/Dashboard.vue'),
          meta: { title: '仪表盘' },
        },
        {
          path: 'advertisements',
          name: 'AdminAdvertisements',
          component: () => import('../views/admin/Advertisements.vue'),
          meta: { title: '广告管理' },
        },
        {
          path: 'announcements',
          name: 'AdminAnnouncements',
          component: () => import('../views/admin/Announcements.vue'),
          meta: { title: '公告管理' },
        },
        {
          path: 'books',
          name: 'AdminBooks',
          component: () => import('../views/admin/Books.vue'),
          meta: { title: '书籍管理' },
        },
        {
          path: 'review',
          name: 'AdminReview',
          component: () => import('../views/admin/ReviewList.vue'),
          meta: { title: '新书审核' },
        },
        {
          path: 'categories',
          name: 'AdminCategories',
          component: () => import('../views/admin/Categories.vue'),
          meta: { title: '分类管理' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue'),
    },
  ],
})

router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('user')) {
    next({ name: 'Login' })
  } else if (to.meta.requiresAdmin) {
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      next({ name: 'Login' })
      return
    }
    try {
      const user = JSON.parse(userStr)
      if (!user.is_staff) {
        next({ name: 'Home' })
        return
      }
    } catch {
      next({ name: 'Login' })
      return
    }
    next()
  } else {
    next()
  }
})

export default router
