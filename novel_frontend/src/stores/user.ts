import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const username = ref('')

  function login(name: string) {
    isLoggedIn.value = true
    username.value = name
  }

  function logout() {
    isLoggedIn.value = false
    username.value = ''
  }

  return {
    isLoggedIn,
    username,
    login,
    logout,
  }
})
