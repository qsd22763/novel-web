import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import GoodsDetail from '../views/GoodsDetail.vue'
import Cart from '../views/Cart.vue'
import OrderCreate from '../views/OrderCreate.vue'
import Order from '../views/Order.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/goods/:id', component: GoodsDetail },
  { path: '/cart', component: Cart },
  { path: '/order/create', component: OrderCreate },
  { path: '/order', component: Order },
]

export default createRouter({
  history: createWebHistory(),
  routes
})