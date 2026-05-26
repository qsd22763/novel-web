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
    },
    {
      path: '/rankings',
      name: 'Rankings',
      component: () => import('../views/Rankings.vue'),
    },
  ],
})

export default router
