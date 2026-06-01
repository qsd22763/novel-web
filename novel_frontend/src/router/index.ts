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
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue'),
    },
  ],
})

router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('user')) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
