<template>
  <div class="not-found">
    <div class="nf-container">
      <div class="nf-art">
        <span class="nf-num">4</span>
        <svg class="nf-book" viewBox="0 0 80 100" width="60" height="75" fill="none">
          <path d="M10 5 L40 15 L70 5 L70 90 L40 100 L10 90 Z" stroke="#CA8A04" stroke-width="2" fill="#FDFBF7"/>
          <line x1="40" y1="15" x2="40" y2="100" stroke="#CA8A04" stroke-width="1.5"/>
          <path d="M18 30 L34 36 M18 42 L34 48 M18 54 L34 60" stroke="#D8D2C4" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M46 30 L62 36 M46 42 L62 48 M46 54 L62 60" stroke="#D8D2C4" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span class="nf-num">4</span>
      </div>
      <h1 class="nf-title">页面走丢了</h1>
      <p class="nf-desc">你访问的页面不存在或已被移除</p>
      <div class="nf-actions">
        <router-link to="/" class="nf-btn nf-btn-primary">返回首页</router-link>
        <router-link to="/search" class="nf-btn nf-btn-outline">搜索小说</router-link>
      </div>
      <div class="nf-suggest">
        <p>或许你想找：</p>
        <div class="nf-links">
          <router-link to="/novels?category=玄幻">玄幻</router-link>
          <router-link to="/novels?category=都市">都市</router-link>
          <router-link to="/novels?category=科幻">科幻</router-link>
          <router-link to="/rankings">排行榜</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  background: #FDFBF7;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.nf-container {
  text-align: center;
  max-width: 480px;
}
.nf-art {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 24px;
}
.nf-num {
  font-family: 'Cormorant Garamond', 'Noto Serif SC', serif;
  font-size: 72px;
  font-weight: 700;
  color: #CA8A04;
  line-height: 1;
}
.nf-book {
  animation: floatBook 3s ease-in-out infinite;
}
@keyframes floatBook {
  0%, 100% { transform: translateY(0) rotate(-3deg); }
  50% { transform: translateY(-12px) rotate(3deg); }
}
.nf-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 3px;
  margin: 0 0 12px;
}
.nf-desc {
  color: #888;
  font-size: 15px;
  margin: 0 0 32px;
  font-family: 'Noto Sans SC', sans-serif;
}
.nf-actions {
  display: flex;
  gap: 14px;
  justify-content: center;
  margin-bottom: 40px;
}
.nf-btn {
  padding: 10px 28px;
  border-radius: 3px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  font-family: 'Noto Sans SC', sans-serif;
  transition: all 0.2s;
}
.nf-btn-primary {
  background: #CA8A04;
  color: #fff;
}
.nf-btn-primary:hover { background: #A87403; }
.nf-btn-outline {
  border: 1.5px solid #D8D2C4;
  color: #555;
  background: transparent;
}
.nf-btn-outline:hover { border-color: #CA8A04; color: #CA8A04; }
.nf-suggest {
  padding-top: 28px;
  border-top: 1px solid #ECE7DC;
}
.nf-suggest p {
  color: #999;
  font-size: 13px;
  margin: 0 0 12px;
  font-family: 'Noto Sans SC', sans-serif;
}
.nf-links {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
.nf-links a {
  color: #CA8A04;
  text-decoration: none;
  font-size: 14px;
  font-family: 'Noto Serif SC', serif;
  padding: 4px 12px;
  border-radius: 2px;
  transition: background 0.2s;
}
.nf-links a:hover { background: rgba(202,138,4,0.08); }

@media (max-width: 480px) {
  .nf-num { font-size: 52px; }
  .nf-book { width: 44px; height: 56px; }
  .nf-title { font-size: 22px; }
  .nf-actions { flex-direction: column; }
  .nf-btn { width: 100%; text-align: center; }
}
</style>
