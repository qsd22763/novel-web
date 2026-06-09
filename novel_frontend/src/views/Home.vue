<template>
  <div class="home-page">

    <!-- ===== HEADER ===== -->
    <header class="site-header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <span class="logo-text">墨香书阁</span>
        </router-link>

        <nav class="main-nav">
          <router-link to="/" class="nav-link" :class="{ active: currentRoute === '/' }">首页</router-link>
          <router-link to="/novels" class="nav-link" :class="{ active: currentRoute === '/novels' }">书库</router-link>
          <router-link to="/rankings" class="nav-link" :class="{ active: currentRoute === '/rankings' }">排行榜</router-link>
          <router-link to="/author" class="nav-link" :class="{ active: currentRoute.startsWith('/author') }">创作</router-link>
        </nav>

        <div class="header-actions">
          <div class="search-box" @click="focusSearch">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              ref="searchInput"
              v-model="searchKeyword"
              class="search-input"
              placeholder="搜索书名或作者…"
              @keyup.enter="handleSearch"
            />
          </div>

          <template v-if="!isLoggedIn">
            <router-link to="/login" class="action-btn action-btn--text">登录</router-link>
            <router-link to="/login" class="action-btn action-btn--primary">注册</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="user-menu">
              <img v-if="userAvatar" :src="userAvatar" alt="头像" class="user-avatar" />
              <svg v-else class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="12" cy="8" r="4"/>
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">

      <!-- ===== API 错误提示 ===== -->
      <div v-if="apiError" class="api-error-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="error-icon"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span class="error-text">{{ apiError }}</span>
        <button class="error-retry" @click="retryAllData">重试</button>
      </div>

      <!-- ===== 全局加载状态 ===== -->
      <div v-if="isLoading && !apiError" class="global-loading">
        <div class="loading-spinner"></div>
        <span>正在加载数据...</span>
      </div>

      <!-- ===== HERO ===== -->
      <section class="hero-section">
        <div class="hero-bg"></div>
        <div class="hero-inner">
          <div class="hero-content">
            <p class="hero-badge">精选文学 · 沉浸阅读</p>
            <h1 class="hero-title">在文字间<br/>发现新世界</h1>
            <p class="hero-desc">海量免费小说，让阅读成为一种享受</p>
            <div class="hero-actions">
              <router-link to="/novels" class="btn btn-primary">开始探索</router-link>
              <router-link to="/rankings" class="btn btn-secondary">热门排行</router-link>
            </div>
          </div>
          <div class="hero-book-showcase">
            <div
              v-for="(novel, i) in featuredNovels.slice(0, 5)"
              :key="novel.id"
              class="book-item"
              :class="`book-${i + 1}`"
              @click="goToDetail(novel.id)"
            >
              <img
                v-lazy="novel.cover"
                :alt="novel.title"
                class="book-cover"
                @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
              />
              <div class="book-overlay">
                <span class="book-title">{{ novel.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 悬浮弹窗广告 -->
      <Teleport to="body">
        <Transition name="ad-popup-fade">
          <div
            v-if="showPopupAd && currentPopupAd"
            class="ad-popup-overlay"
            @click.self="closePopupAd"
          >
            <div class="ad-popup-card" :class="{ 'ad-popup-visible': popupVisible }">
              <button class="ad-popup-close" @click.stop="closePopupAd" title="关闭广告">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
              <span class="ad-popup-counter">{{ currentAdIndex + 1 }} / {{ allPopupAds.length }}</span>
              <div class="ad-popup-content" @click="handleAdClick(currentPopupAd)">
                <img :src="currentPopupAd.image_url" :alt="currentPopupAd.title" class="ad-popup-img" />
                <div class="ad-popup-info">
                  <h3 class="ad-popup-title">{{ currentPopupAd.title }}</h3>
                  <p v-if="currentPopupAd.link_url" class="ad-popup-link">点击查看详情 →</p>
                </div>
              </div>
              <span class="ad-popup-badge">广告</span>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- ===== QUICK STATS ===== -->
      <section class="quick-stats">
        <div class="stats-container">
          <div class="stat-item">
            <span class="stat-value">10K+</span>
            <span class="stat-label">精选小说</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">500万+</span>
            <span class="stat-label">阅读次数</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">100%</span>
            <span class="stat-label">免费阅读</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">每日更新</span>
            <span class="stat-label">持续更新</span>
          </div>
        </div>
      </section>

      <!-- ===== 公告通知栏 ===== -->
      <section v-if="publicAnnouncements.length" class="announcement-bar">
        <div class="announcement-container">
          <div class="announcement-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <div class="announcement-scroll">
            <div
              v-for="(ann, idx) in publicAnnouncements"
              :key="ann.id"
              class="announcement-item"
              :class="{ 'announcement-pinned': ann.is_pinned }"
            >
              <span v-if="ann.is_pinned" class="pin-tag">置顶</span>
              <span class="type-tag" :class="'type-' + ann.announcement_type">{{ typeLabel(ann.announcement_type) }}</span>
              <span class="announcement-title">{{ ann.title }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== FEATURED NOVELS ===== -->
      <section class="featured-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">精选推荐</span>
              <h2 class="section-title">编辑精选</h2>
            </div>
            <router-link to="/novels" class="see-all">查看全部</router-link>
          </div>

          <div class="featured-grid">
            <article
              v-for="(novel, index) in featuredNovels.slice(0, 6)"
              :key="novel.id"
              class="novel-card"
              @click="goToDetail(novel.id)"
            >
              <div class="card-cover-wrap">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  class="card-cover"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
                <span class="card-category">{{ novel.category }}</span>
                <div class="card-hover-overlay">
                  <span class="hover-text">开始阅读</span>
                </div>
              </div>
              <div class="card-content">
                <h3 class="card-title">{{ novel.title }}</h3>
                <p class="card-author">{{ novel.author }}</p>
                <div v-if="novel.tags" class="card-tags">
                  <span v-for="tag in novel.tags.split(',').map(t=>t.trim()).filter(Boolean)" :key="tag" class="card-tag">{{ tag }}</span>
                </div>
                <p class="card-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                    {{ formatWordCount(novel.word_count) }}
                  </span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ===== 新书上架 · 横向滚动 ===== -->
      <section class="newbooks-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">NEW ARRIVALS</span>
              <h2 class="section-title">新书上架</h2>
            </div>
            <div class="scroll-controls">
              <button class="scroll-btn" @click="scrollNewBooks('left')" :disabled="newScrollAtStart">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
              </button>
              <button class="scroll-btn" @click="scrollNewBooks('right')" :disabled="newScrollAtEnd">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
            </div>
          </div>

          <div
            ref="newBooksTrack"
            class="newbooks-track"
            @mousedown="onDragStart"
            @mousemove="onDragMove"
            @mouseup="onDragEnd"
            @mouseleave="onDragEnd"
            @scroll="onNewBooksScroll"
          >
            <article
              v-for="novel in newBooks"
              :key="'nb-' + novel.id"
              class="newbook-card"
              @click="goToDetail(novel.id)"
            >
              <div class="newbook-cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
                <span class="newbook-tag">新</span>
              </div>
              <div class="newbook-info">
                <h3 class="newbook-title">{{ novel.title }}</h3>
                <p class="newbook-author">{{ novel.author }}</p>
                <span class="newbook-cat">{{ novel.category }}</span>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ===== 热门榜单 · Tab切换 ===== -->
      <section class="ranking-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">HOT RANKING</span>
              <h2 class="section-title">热门榜单</h2>
            </div>
            <router-link to="/rankings" class="see-all">完整榜单 &rarr;</router-link>
          </div>

          <div class="rank-tabs">
            <button
              v-for="tab in rankTabs"
              :key="tab.key"
              class="rank-tab"
              :class="{ active: activeRankTab === tab.key }"
              @click="switchRankTab(tab.key)"
            >{{ tab.label }}</button>
          </div>

          <div class="rank-list">
            <div
              v-for="(novel, idx) in rankList"
              :key="'rk-' + novel.id + '-' + activeRankTab"
              class="rank-item"
              @click="goToDetail(novel.id)"
            >
              <span class="rank-num" :class="{ top3: idx < 3 }">{{ idx + 1 }}</span>
              <div class="rank-cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
              </div>
              <div class="rank-info">
                <h4 class="rank-name">{{ novel.title }}</h4>
                <p class="rank-meta">{{ novel.author }} · {{ novel.category }}</p>
              </div>
              <span class="rank-hot">{{ formatCount(novel.view_count || 0) }}热度</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 书单推荐 · 编辑精选合集 ===== -->
      <section class="booklist-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">EDITOR'S PICKS</span>
              <h2 class="section-title">书单推荐</h2>
            </div>
          </div>

          <!-- 主推大卡片 -->
          <div
            v-if="featuredBookList"
            class="bl-featured"
            @click="goToBookList(featuredBookList.id)"
          >
            <div class="bl-featured-bg" :style="{ background: featuredBookList.gradient }"></div>
            <div class="bl-featured-inner">
              <div class="bl-featured-info">
                <span class="bl-badge bl-badge--lg">{{ featuredBookList.badge }}</span>
                <h3 class="bl-title--lg">{{ featuredBookList.name }}</h3>
                <p class="bl-desc--lg">{{ featuredBookList.desc }}</p>
                <div class="bl-tags">
                  <span v-for="(tag, ti) in featuredBookList.tags" :key="ti" class="bl-tag">{{ tag }}</span>
                </div>
                <span class="bl-action">查看全部 {{ featuredBookList.bookIds.length }} 本 &rarr;</span>
              </div>
              <div class="bl-featured-covers">
                <div
                  v-for="(nid, bi) in featuredBookList.bookIds.slice(0, 5)"
                  :key="'fc-' + bi"
                  class="bl-cover-lg"
                  :style="{ '--delay': bi * 0.08 + 's' }"
                  @click.stop="goToDetail(nid)"
                  :title="getBookTitle(nid)"
                >
                  <img
                    v-lazy="getBookCover(nid)"
                    alt=""
                    @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 普通书单网格 -->
          <div class="booklist-grid">
            <div
              v-for="bl in normalBookLists"
              :key="bl.id"
              class="booklist-card"
              @click="goToBookList(bl.id)"
            >
              <div class="booklist-header" :style="{ background: bl.gradient }">
                <span class="booklist-badge">{{ bl.badge }}</span>
                <h3 class="booklist-name">{{ bl.name }}</h3>
                <p class="booklist-desc">{{ bl.desc }}</p>
                <div v-if="bl.tags && bl.tags.length" class="bl-mini-tags">
                  <span v-for="(tag, ti) in bl.tags.slice(0, 3)" :key="ti" class="bl-mini-tag">{{ tag }}</span>
                </div>
              </div>
              <div class="booklist-books">
                <div
                  v-for="(nid, bi) in bl.bookIds.slice(0, 4)"
                  :key="bi"
                  class="bl-mini-cover"
                  @click.stop="goToDetail(nid)"
                  :title="getBookTitle(nid)"
                >
                  <img
                    v-lazy="getBookCover(nid)"
                    alt=""
                    @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                  />
                </div>
                <span class="bl-more">{{ bl.bookIds.length }}本</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== CATEGORIES ===== -->
      <section class="categories-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">分类浏览</span>
              <h2 class="section-title">探索分类</h2>
            </div>
          </div>

          <div class="categories-grid">
            <div
              v-for="cat in categories"
              :key="cat.name"
              class="category-card"
              :style="{ '--category-color': cat.color }"
              @click="goToCategory(cat.name)"
            >
              <div class="cat-icon">
                <svg v-if="cat.name === '玄幻'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                <svg v-else-if="cat.name === '都市'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                <svg v-else-if="cat.name === '穿越'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <svg v-else-if="cat.name === '科幻'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 2v4M12 18v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M2 12h4M18 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
                </svg>
                <svg v-else-if="cat.name === '游戏'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="6" width="20" height="12" rx="2"/>
                  <path d="M6 12h4M8 10v4"/>
                  <circle cx="16" cy="11" r="1" fill="currentColor"/>
                  <circle cx="18" cy="13" r="1" fill="currentColor"/>
                </svg>
                <svg v-else-if="cat.name === '悬疑'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                  <path d="M11 8v3l2 2"/>
                </svg>
                <svg v-else-if="cat.name === '武侠'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14.5 17.5L3 6V3h3l11.5 11.5"/>
                  <path d="M13 19l6-6"/>
                  <path d="M16 16l4 4"/>
                  <path d="M19 21l2-2"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count">{{ cat.count }} 本</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== LATEST UPDATES ===== -->
      <section class="latest-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">最新更新</span>
              <h2 class="section-title">今日更新</h2>
            </div>
            <router-link to="/novels" class="see-all">更多更新</router-link>
          </div>

          <div class="latest-list">
            <article
              v-for="novel in recentNovels"
              :key="novel.id"
              class="latest-item"
              @click="goToDetail(novel.id)"
            >
              <div class="item-cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
              </div>
              <div class="item-info">
                <h3 class="item-title">{{ novel.title }}</h3>
                <p class="item-author">{{ novel.author }}</p>
                <p class="item-chapter">更新至第 {{ novel.chapter_count }} 章</p>
              </div>
              <div class="item-meta">
                <span class="item-category">{{ novel.category }}</span>
                <span class="item-time">{{ formatTime(novel.updated_at) }}</span>
              </div>
            </article>
          </div>
        </div>
      </section>

    </main>

    <!-- ===== FOOTER ===== -->
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-brand">
            <div class="footer-logo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
              <span>墨香书阁</span>
            </div>
            <p class="footer-desc">为阅读而生，为故事而活</p>
            <div class="social-links">
              <a href="#" class="social-link" aria-label="微博">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="GitHub">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
              </a>
            </div>
          </div>

          <div class="footer-links">
            <div class="link-group">
              <h4>产品</h4>
              <a href="/novels">书库</a>
              <a href="/rankings">排行榜</a>
              <a href="/search">搜索</a>
            </div>
            <div class="link-group">
              <h4>支持</h4>
              <a href="#">帮助中心</a>
              <a href="#">联系我们</a>
              <a href="#">用户反馈</a>
            </div>
            <div class="link-group">
              <h4>法律</h4>
              <a href="#">用户协议</a>
              <a href="#">隐私政策</a>
              <a href="#">版权声明</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 墨香书阁. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onMounted as onMountedVue, onUnmounted, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { novelApi, type Novel } from '../api'
import request from '../utils/request'

const router = useRouter()
const route = useRoute()

const searchKeyword = ref('')
const searchInput = ref<HTMLInputElement>()
const featuredNovels = ref<Novel[]>([])
const recentNovels = ref<Novel[]>([])
const isScrolled = ref(false)
const isLoading = ref(true)
const apiError = ref<string | null>(null)
const allPopupAds = ref<any[]>([])
const showPopupAd = ref(false)
const popupVisible = ref(false)
const currentAdIndex = ref(0)
const currentPopupAd = computed(() => allPopupAds.value[currentAdIndex.value] || null)
const publicAnnouncements = ref<any[]>([])

const currentRoute = computed(() => route.path)
const isLoggedIn = computed(() => !!localStorage.getItem('user'))
const userAvatar = ref('')

// 预设分类颜色映射（常用分类固定颜色，新分类自动分配）
const CATEGORY_COLORS: Record<string, string> = {
  '玄幻': '#8b5cf6', '都市': '#ec4899', '穿越': '#f59e0b', '科幻': '#3b82f6',
  '游戏': '#10b981', '悬疑': '#6366f1', '武侠': '#ef4444', '历史': '#84cc16',
  '文化': '#06b6d4',
}
const AUTO_COLORS = ['#f97316', '#14b8a6', '#a855f7', '#ec4899', '#64748b', '#0891b2']
let colorIndex = 0
function getCategoryColor(name: string): string {
  if (CATEGORY_COLORS[name]) return CATEGORY_COLORS[name]
  if (!CATEGORY_COLORS[name]) {
    CATEGORY_COLORS[name] = AUTO_COLORS[colorIndex % AUTO_COLORS.length]
    colorIndex++
  }
  return CATEGORY_COLORS[name]
}

const categories = ref<{ name: string; color: string; count: number }[]>([])

// ===== 新书上架（横向滚动） =====
const newBooks = ref<Novel[]>([])
const newBooksTrack = ref<HTMLElement>()
const newScrollAtStart = ref(true)
const newScrollAtEnd = ref(false)
let isDragging = false
let startX = 0
let scrollLeft = 0

// ===== 热门榜单（Tab切换） =====
const activeRankTab = ref('week')
const rankTabs = [
  { key: 'week', label: '周榜' },
  { key: 'month', label: '月榜' },
  { key: 'total', label: '总榜' },
]
const rankList = ref<Novel[]>([])
const rankCache = ref<Record<string, Novel[]>>({})

// ===== 分类快捷入口（已移除） =====

// ===== 书单推荐 =====
interface BookListItem {
  id: string
  name: string
  desc: string
  badge: string
  gradient: string
  bookIds: number[]
  tags?: string[]
}
const bookLists = ref<BookListItem[]>([])

// 主推书单（第一个）
const featuredBookList = computed(() => bookLists.value[0] || null)
// 其余普通书单
const normalBookLists = computed(() => bookLists.value.slice(1))

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const formatTime = (time?: string) => {
  if (!time) return '刚刚'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return '刚刚'
  if (hours < 24) return hours + '小时前'
  const days = Math.floor(hours / 24)
  if (days < 30) return days + '天前'
  return date.toLocaleDateString()
}

const loadFeaturedNovels = async () => {
  try {
    const res = await novelApi.recommend(8)
    featuredNovels.value = res
    initBookLists()
  } catch (error) {
    console.error('加载推荐小说失败:', error)
    throw error
  }
}

const loadRecentNovels = async () => {
  try {
    const res = await novelApi.list({ page_size: 8, ordering: '-updated_at' })
    recentNovels.value = res.results || []
  } catch (error) {
    console.error('加载最新小说失败:', error)
    throw error
  }
}

// 加载新上架书籍
const loadNewBooks = async () => {
  try {
    const res = await novelApi.list({ page_size: 15, ordering: '-created_at' })
    newBooks.value = res.results || []
  } catch (error) {
    console.error('加载新书上架失败:', error)
  }
}

// 初始化榜单（默认加载周榜）
const initRankings = async () => {
  await switchRankTab('week')
}

// 初始化书单推荐
const initBookLists = () => {
  const all = featuredNovels.value
  // 至少3本才能生成书单，避免空白
  if (all.length < 3) return

  // 安全取值辅助：避免越界
  const safeSlice = (start: number, end: number) => {
    const arr = all.slice(start, end)
    return arr.length > 0 ? arr : [all[0]]
  }

  bookLists.value = [
    {
      id: 'high-score',
      name: '高分完本神作',
      desc: '评分最高、口碑最好的完结作品，每一本都值得反复品读',
      badge: '编辑力荐',
      gradient: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%)',
      tags: ['完结', '高分', '口碑炸裂'],
      bookIds: safeSlice(0, Math.min(6, all.length)).map((n: Novel) => n.id),
    },
    {
      id: 'stay-up',
      name: '熬夜必追系列',
      desc: '一旦开始就停不下来的神作，通宵也要看完',
      badge: 'HOT',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      tags: ['热血', '爽文', '停不下来'],
      bookIds: safeSlice(2, Math.min(8, all.length)).map((n: Novel) => n.id),
    },
    {
      id: 'new-star',
      name: '新锐潜力佳作',
      desc: '潜力新人作品，未来可期，趁早收藏不亏',
      badge: 'NEW',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      tags: ['新书', '潜力', '黑马'],
      bookIds: safeSlice(4, Math.min(10, all.length)).map((n: Novel) => n.id),
    },
    {
      id: 'classic',
      name: '经典重温必读',
      desc: '百读不厌的经典之作，每次重读都有新感悟',
      badge: 'BEST',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      tags: ['经典', '耐看', '深度'],
      bookIds: safeSlice(1, Math.min(7, all.length)).map((n: Novel) => n.id),
    },
    {
      id: 'relax',
      name: '轻松治愈系',
      desc: '工作累了看看，暖心又解压的治愈故事',
      badge: 'WARM',
      gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
      tags: ['治愈', '轻松', '暖心'],
      bookIds: safeSlice(0, Math.min(5, all.length)).map((n: Novel) => n.id),
    },
    {
      id: 'brain-burn',
      name: '烧脑悬疑精选',
      desc: '反转不断、细思极恐的高智商推理小说',
      badge: 'MIND',
      gradient: 'linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)',
      tags: ['烧脑', '反转', '高智商'],
      bookIds: safeSlice(3, Math.min(9, all.length)).map((n: Novel) => n.id),
    },
  ]
}

const loadCategoryStats = async () => {
  try {
    const res: any = await (novelApi as any).category_stats()
    // 动态构建分类列表（后端返回 {分类名: 数量}）
    categories.value = Object.keys(res || {}).map(name => ({
      name,
      color: getCategoryColor(name),
      count: res[name] || 0,
    })).sort((a, b) => b.count - a.count)
  } catch (error) {
    console.error('加载分类统计失败:', error)
  }
}

const fetchPublicAds = async () => {
  try {
    const res = await request.get('/public/advertisements/')
    const allAds: any[] = Array.isArray(res) ? res : res.results || []
    console.log('[AdPopup] API returned:', allAds.length, 'ads', allAds.map((a: any) => a.title))
    const today = new Date().toDateString()
    const remaining = allAds.filter((ad: any) => {
      const closedVal = localStorage.getItem('ad_popup_closed_' + ad.id)
      return !closedVal || closedVal !== today
    })
    console.log('[AdPopup] After filter:', remaining.length, 'ads')
    allPopupAds.value = remaining.length > 0 ? remaining : allAds
    currentAdIndex.value = 0
    if (allPopupAds.value.length) {
      setTimeout(() => {
        showPopupAd.value = true
        requestAnimationFrame(() => { popupVisible.value = true })
        console.log('[AdPopup] Showing:', allPopupAds.value[0].title)
      }, 1200)
    }
  } catch (e) {
    console.warn('[AdPopup] Fetch failed:', e)
  }
}

const typeLabel = (type: string) => {
  const map: Record<string, string> = { notice: '通知', maintenance: '维护', activity: '活动' }
  return map[type] || type
}

const fetchPublicAnnouncements = async () => {
  try {
    const res = await request.get('/public/announcements/')
    const list: any[] = Array.isArray(res) ? res : res.results || []
    publicAnnouncements.value = list.filter((a: any) => a.is_active).sort((a: any, b: any) => {
      if (a.is_pinned && !b.is_pinned) return -1
      if (!a.is_pinned && b.is_pinned) return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  } catch (e) {
    console.warn('[Announcement] Fetch failed:', e)
  }
}

function closePopupAd() {
  if (currentPopupAd.value) {
    localStorage.setItem('ad_popup_closed_' + currentPopupAd.value.id, new Date().toDateString())
  }
  popupVisible.value = false
  setTimeout(() => {
    showPopupAd.value = false
    currentAdIndex.value++
    if (currentAdIndex.value < allPopupAds.value.length) {
      setTimeout(() => {
        showPopupAd.value = true
        requestAnimationFrame(() => { popupVisible.value = true })
      }, 400)
    }
  }, 300)
}

async function handleAdClick(ad: any) {
  try { await request.post(`/public/advertisements/${ad.id}/click/`) } catch {}
  if (ad.link_url) window.open(ad.link_url, '_blank')
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ name: 'Search', query: { q: searchKeyword.value } })
  }
}

const focusSearch = () => {
  searchInput.value?.focus()
}

const goToDetail = (id: number) => {
  router.push({ name: 'NovelDetail', params: { id } })
}

const goToCategory = (category: string) => {
  router.push({ name: 'NovelList', query: { category } })
}

// ===== 新上架：横向滚动 & 拖拽 =====
const scrollNewBooks = (dir: 'left' | 'right') => {
  const el = newBooksTrack.value
  if (!el) return
  const amount = el.clientWidth * 0.7
  el.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' })
}

const onNewBooksScroll = () => {
  const el = newBooksTrack.value
  if (!el) return
  newScrollAtStart.value = el.scrollLeft <= 5
  newScrollAtEnd.value = el.scrollLeft + el.clientWidth >= el.scrollWidth - 5
}

const onDragStart = (e: MouseEvent) => {
  isDragging = true
  startX = e.pageX - (newBooksTrack.value?.offsetLeft || 0)
  scrollLeft = newBooksTrack.value?.scrollLeft || 0
  if (newBooksTrack.value) newBooksTrack.value.style.cursor = 'grabbing'
}

const onDragMove = (e: MouseEvent) => {
  if (!isDragging || !newBooksTrack.value) return
  e.preventDefault()
  const x = e.pageX - newBooksTrack.value.offsetLeft
  const walk = (x - startX) * 1.5
  newBooksTrack.value.scrollLeft = scrollLeft - walk
}

const onDragEnd = () => {
  isDragging = false
  if (newBooksTrack.value) newBooksTrack.value.style.cursor = 'grab'
}

// ===== 热门榜单：Tab切换 =====
const switchRankTab = async (key: string) => {
  activeRankTab.value = key
  if (rankCache.value[key]) {
    rankList.value = rankCache.value[key]
    return
  }
  try {
    const orderingMap: Record<string, string> = { week: '-view_count', month: '-view_count', total: '-view_count' }
    const res = await novelApi.list({ page_size: 10, ordering: orderingMap[key] || '-view_count' })
    rankList.value = res.results || []
    rankCache.value[key] = rankList.value
  } catch (error) {
    console.error('加载榜单失败:', error)
  }
}

// ===== 书单推荐：跳转 & 初始化 =====
const goToBookList = (id: string) => {
  router.push({ name: 'NovelList', query: { booklist: id } })
}

const getBookCover = (id: number) => {
  const novel = featuredNovels.value.find(n => n.id === id)
  return novel?.cover || ''
}

const getBookTitle = (id: number) => {
  const novel = featuredNovels.value.find(n => n.id === id)
  return novel?.title || ''
}

// ===== 统一加载所有数据（含错误处理）=====
const retryAllData = async () => {
  isLoading.value = true
  apiError.value = null
  let errorCount = 0

  const loaders = [
    { fn: loadFeaturedNovels, name: '推荐小说' },
    { fn: loadRecentNovels, name: '最新小说' },
    { fn: loadNewBooks, name: '新书上架' },
    { fn: loadCategoryStats, name: '分类统计' },
    { fn: initRankings, name: '热门榜单' },
    { fn: fetchPublicAds, name: '广告' },
    { fn: fetchPublicAnnouncements, name: '公告' },
  ]

  for (const loader of loaders) {
    try {
      await loader.fn()
    } catch {
      errorCount++
    }
  }

  isLoading.value = false
  if (errorCount === loaders.length) {
    apiError.value = '后端服务连接失败，数据加载失败，请稍后重试'
  }
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMountedVue(() => {
  retryAllData()
  window.addEventListener('scroll', handleScroll)
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    userAvatar.value = user.avatar || ''
  } catch {}
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// keep-alive 激活时重新初始化（从其他页面返回首页时触发）
onActivated(() => {
  retryAllData()
  window.addEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

:root {
  --primary: #CA8A04;
  --primary-dark: #A67C00;
  --bg-paper: #FDFBF7;
  --bg-card: #FFFFFF;
  --text-primary: #1A1A1A;
  --text-muted: #6B7280;
  --border-color: #E5E7EB;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.home-page {
  min-height: 100vh;
  background: var(--bg-paper);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
  color: var(--text-primary);
}

/* ===== HEADER ===== */
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.header-scrolled {
  background: rgba(253, 251, 247, 0.98);
  box-shadow: var(--shadow-sm);
}

.header-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 70px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  width: 28px;
  height: 28px;
  color: var(--primary);
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.375rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.main-nav {
  display: flex;
  gap: 1.75rem;
}

.nav-link {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-decoration: none;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 1px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 220px;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 12px 0 36px;
  background: #F3F4F6;
  border: 1px solid transparent;
  border-radius: 20px;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: var(--shadow-sm);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.action-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.action-btn--text {
  color: var(--text-muted);
}

.action-btn--text:hover {
  color: var(--text-primary);
}

.action-btn--primary {
  background: var(--text-primary);
  color: #fff;
}

.action-btn--primary:hover {
  opacity: 0.9;
}

.user-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  transition: all 0.2s ease;
}

.user-menu:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.user-icon {
  width: 20px;
  height: 20px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid rgba(202, 138, 4, 0.5);
}

/* ===== MAIN CONTENT ===== */
.main-content {
  padding-top: 70px;
}

/* ===== API 错误提示横幅 ===== */
.api-error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
  border-bottom: 1px solid #FECACA;
  color: #DC2626;
}
.error-icon {
  width: 20px; height: 20px; flex-shrink: 0;
}
.error-text {
  flex: 1; font-size: 0.875rem; font-weight: 500;
}
.error-retry {
  padding: 0.3rem 1rem;
  background: #DC2626; color: #fff;
  border: none; border-radius: 6px;
  font-size: 0.8rem; font-weight: 500;
  cursor: pointer; transition: opacity 0.2s;
}
.error-retry:hover { opacity: 0.85; }

/* ===== 全局加载状态 ===== */
.global-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}
.loading-spinner {
  width: 28px; height: 28px;
  border: 3px solid #E5E7EB;
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== HERO ===== */
.hero-section {
  position: relative;
  min-height: 56vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 50%, #1A1A1A 100%);
}

.hero-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(202, 138, 4, 0.15) 0%, transparent 50%);
}

.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: center;
}

.hero-content {
  text-align: left;
}

.hero-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: rgba(202, 138, 4, 0.15);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 20px;
  margin-bottom: 1rem;
  letter-spacing: 0.05em;
}

.hero-title {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  color: #fff;
  line-height: 1.1;
  margin: 0 0 1rem;
}

.hero-desc {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1.5rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.875rem 2rem;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  border-radius: 30px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(202, 138, 4, 0.3);
}

.btn-secondary {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-book-showcase {
  position: relative;
  height: 340px;
}

.book-item {
  position: absolute;
  width: 140px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 60%);
  display: flex;
  align-items: flex-end;
  padding: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.book-item:hover .book-overlay {
  opacity: 1;
}

.book-title {
  font-size: 0.75rem;
  color: #fff;
  font-family: 'Noto Serif SC', serif;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-1 {
  top: 60px;
  left: 5%;
  transform: rotate(-8deg);
}

.book-2 {
  top: 40px;
  left: 28%;
  width: 160px;
  height: 220px;
  z-index: 2;
}

.book-3 {
  top: 70px;
  left: 52%;
  transform: rotate(5deg);
}

.book-4 {
  top: 50px;
  right: 15%;
  width: 150px;
  height: 210px;
  transform: rotate(8deg);
}

.book-5 {
  top: 80px;
  right: 2%;
  width: 130px;
  height: 185px;
  transform: rotate(-3deg);
}

.book-item:hover {
  transform: translateY(-8px) rotate(0deg) !important;
  z-index: 10;
}

/* ===== 悬浮弹窗广告 ===== */
.ad-popup-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
}
.ad-popup-card {
  position: relative;
  width: 420px;
  max-width: 90vw;
  border-radius: 16px;
  overflow: hidden;
  background: #1a1a2e;
  box-shadow:
    0 25px 60px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.08);
  transform: scale(0.85) translateY(20px);
  opacity: 0;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease;
}
.ad-popup-card.ad-popup-visible {
  transform: scale(1) translateY(0);
  opacity: 1;
}
.ad-popup-close {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.45);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}
.ad-popup-close svg {
  width: 14px;
  height: 14px;
}
.ad-popup-close:hover {
  background: rgba(239, 68, 68, 0.85);
  color: #fff;
  transform: rotate(90deg) scale(1.1);
}
.ad-popup-counter {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  font-size: 12px;
  font-family: 'Fira Code', monospace;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(0, 0, 0, 0.45);
  padding: 3px 14px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  letter-spacing: 0.5px;
}
.ad-popup-content {
  cursor: pointer;
  position: relative;
}
.ad-popup-img {
  width: 100%;
  height: 260px;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.ad-popup-card:hover .ad-popup-img {
  transform: scale(1.03);
}
.ad-popup-info {
  padding: 14px 18px 16px;
}
.ad-popup-title {
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 6px;
  line-height: 1.3;
}
.ad-popup-link {
  font-size: 12.5px;
  color: #22c55e;
  margin: 0;
  opacity: 0.85;
}
.ad-popup-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(0, 0, 0, 0.45);
  padding: 3px 10px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  letter-spacing: 0.5px;
}

/* 弹窗过渡动画 */
.ad-popup-fade-enter-active { transition: opacity 0.3s ease; }
.ad-popup-fade-leave-active { transition: opacity 0.25s ease; }
.ad-popup-fade-enter-from,
.ad-popup-fade-leave-to { opacity: 0; }

/* ===== QUICK STATS ===== */
.quick-stats {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 0.825rem;
  color: var(--text-muted);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

/* ===== SECTION SHARED ===== */
.section-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.2rem;
}

.section-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.section-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--primary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.see-all {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s ease;
}

.see-all:hover {
  color: var(--primary);
}

/* ===== 公告通知栏 ===== */
.announcement-bar {
  background: linear-gradient(135deg, #FFF7ED 0%, #FEF3C7 100%);
  border-bottom: 1px solid #FDE68A;
}

.announcement-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.announcement-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: var(--primary);
  animation: bell-ring 2s ease-in-out infinite;
}

@keyframes bell-ring {
  0%, 100% { transform: rotate(0); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-12deg); }
  30% { transform: rotate(10deg); }
  40% { transform: rotate(-6deg); }
  50% { transform: rotate(0); }
}

.announcement-icon svg {
  width: 24px;
  height: 24px;
}

.announcement-scroll {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

.announcement-item {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  background: #fff;
  border-radius: 20px;
  font-size: 0.8rem;
  color: var(--text-primary);
  border: 1px solid rgba(202, 138, 4, 0.2);
  transition: all 0.2s ease;
}

.announcement-item:hover {
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(202, 138, 4, 0.15);
}

.announcement-pinned {
  border-color: var(--primary);
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
}

.pin-tag {
  padding: 1px 6px;
  background: var(--primary);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 600;
  border-radius: 8px;
  letter-spacing: 0.5px;
}

.type-tag {
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 0.68rem;
  font-weight: 500;
}

.type-notice {
  background: #DBEAFE;
  color: #1D4ED8;
}

.type-maintenance {
  background: #FEE2E2;
  color: #DC2626;
}

.type-activity {
  background: #DCFCE7;
  color: #16A34A;
}

.announcement-title {
  font-weight: 500;
  white-space: nowrap;
}

/* ===== FEATURED SECTION ===== */
.featured-section {
  padding: 1.5rem 0;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.novel-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.novel-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-cover-wrap {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
}

.card-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.novel-card:hover .card-cover {
  transform: scale(1.05);
}

.card-category {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 3px 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 0.675rem;
  font-weight: 500;
  border-radius: 12px;
}

.card-hover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.novel-card:hover .card-hover-overlay {
  opacity: 1;
}

.hover-text {
  padding: 0.5rem 1.25rem;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 20px;
}

.card-content {
  padding: 0.75rem;
}

.card-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.2rem;
  line-height: 1.3;
}

.card-author {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0 0 0.25rem;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}
.card-tag {
  font-size: 0.68rem;
  color: #9CA3AF;
  background: rgba(156,163,175,0.1);
  border: 1px solid rgba(156,163,175,0.2);
  padding: 1px 8px;
  border-radius: 10px;
  font-family: var(--font-sans-cn);
}

.card-desc {
  font-size: 0.8rem;
  color: #6B7280;
  line-height: 1.5;
  margin: 0 0 0.4rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.775rem;
  color: #9CA3AF;
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

/* ===== CATEGORIES SECTION ===== */
.categories-section {
  padding: 2.5rem 0;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}

.category-card {
  padding: 1.5rem 1rem;
  background: var(--bg-paper);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--category-color);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.category-card:hover::before {
  opacity: 1;
}

.category-card:hover {
  border-color: var(--category-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.cat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: color-mix(in srgb, var(--category-color) 10%, transparent);
  color: var(--category-color);
}

.cat-icon svg {
  width: 22px;
  height: 22px;
}

.cat-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.cat-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ===== LATEST SECTION ===== */
.latest-section {
  padding: 3rem 0;
}

.latest-list {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.latest-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s ease;
}

.latest-item:last-child {
  border-bottom: none;
}

.latest-item:hover {
  background: #FAFAFA;
}

.item-cover {
  width: 56px;
  height: 78px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-author {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0 0 0.2rem;
}

.item-chapter {
  font-size: 0.78rem;
  color: #9CA3AF;
  margin: 0;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.375rem;
}

.item-category {
  padding: 2px 9px;
  background: #F3F4F6;
  color: var(--text-muted);
  font-size: 0.675rem;
  border-radius: 12px;
}

.item-time {
  font-size: 0.75rem;
  color: #9CA3AF;
}

/* ===== 新书上架 · 横向滚动 ===== */
.newbooks-section {
  padding: 2rem 0;
}

.scroll-controls {
  display: flex;
  gap: 6px;
}

.scroll-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.scroll-btn:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
}

.scroll-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.scroll-btn svg {
  width: 14px;
  height: 14px;
}

.newbooks-track {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  padding: 0.5rem 0 0.75rem;
  cursor: grab;
  -webkit-user-select: none;
  user-select: none;
}

.newbooks-track::-webkit-scrollbar {
  display: none;
}

.newbook-card {
  flex-shrink: 0;
  width: 160px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  scroll-snap-align: start;
  transition: all 0.25s ease;
  cursor: pointer;
}

.newbook-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.newbook-cover {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
}

.newbook-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.newbook-card:hover .newbook-cover img {
  transform: scale(1.06);
}

.newbook-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  background: var(--primary);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 600;
  border-radius: 6px;
}

.newbook-info {
  padding: 0.6rem 0.7rem;
}

.newbook-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.newbook-author {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin: 0 0 0.25rem;
}

.newbook-cat {
  display: inline-block;
  padding: 1px 8px;
  background: #F3F4F6;
  color: var(--text-muted);
  font-size: 0.65rem;
  border-radius: 8px;
}

/* ===== 热门榜单 ===== */
.ranking-section {
  padding: 2rem 0;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.rank-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1rem;
  border-bottom: 2px solid #F3F4F6;
}

.rank-tab {
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.rank-tab:hover {
  color: var(--text-primary);
}

.rank-tab.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.7rem 0.5rem;
  border-bottom: 1px solid #F5F5F5;
  cursor: pointer;
  transition: background 0.2s ease;
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-item:hover {
  background: #FAFAFA;
  border-radius: 6px;
}

.rank-num {
  width: 24px;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 700;
  color: #9CA3AF;
  flex-shrink: 0;
}

.rank-num.top3 {
  color: var(--primary);
  font-size: 0.95rem;
}

.rank-cover {
  width: 42px;
  height: 56px;
  border-radius: 5px;
  overflow: hidden;
  flex-shrink: 0;
}

.rank-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-meta {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin: 0;
}

.rank-hot {
  font-size: 0.72rem;
  color: var(--primary);
  font-weight: 600;
  flex-shrink: 0;
}

/* ===== 书单推荐 ===== */
.booklist-section {
  padding: 2.5rem 0;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

/* ---- 主推大卡片 ---- */
.bl-featured {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.bl-featured:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.bl-featured-bg {
  position: absolute;
  inset: 0;
}

.bl-featured-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.2) 60%, transparent 100%);
}

.bl-featured-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2.5rem 2.5rem 2rem;
  gap: 2rem;
  min-height: 200px;
}

.bl-featured-info {
  flex: 1;
  color: #fff;
}

.bl-badge--lg {
  display: inline-block;
  padding: 4px 14px;
  background: rgba(255, 215, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.4);
  color: #ffd700;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  border-radius: 20px;
  margin-bottom: 0.85rem;
  backdrop-filter: blur(8px);
}

.bl-title--lg {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.65rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 0.5rem;
  line-height: 1.3;
}

.bl-desc--lg {
  font-size: 0.88rem;
  opacity: 0.85;
  margin: 0 0 0.85rem;
  line-height: 1.6;
  max-width: 420px;
}

.bl-tags {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-bottom: 0.85rem;
}

.bl-tag {
  padding: 3px 10px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(6px);
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.72rem;
  font-weight: 500;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.bl-action {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #ffd700;
  cursor: pointer;
  transition: gap 0.2s ease;
}

.bl-featured:hover .bl-action {
  gap: 0.65rem;
}

/* 主推封面堆叠 */
.bl-featured-covers {
  display: flex;
  gap: -16px;
  flex-shrink: 0;
}

.bl-cover-lg {
  width: 80px;
  height: 110px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
  animation: cover-float 3s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
  cursor: pointer;
}

@keyframes cover-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.bl-cover-lg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bl-cover-lg:nth-child(1) { transform: rotate(-5deg) translateY(0); }
.bl-cover-lg:nth-child(2) { transform: rotate(2deg) translateY(-10px); z-index: 1; }
.bl-cover-lg:nth-child(3) { transform: rotate(-3deg) translateY(-5px); z-index: 2; }
.bl-cover-lg:nth-child(4) { transform: rotate(4deg) translateY(-12px); z-index: 3; }
.bl-cover-lg:nth-child(5) { transform: rotate(-2deg) translateY(-8px); z-index: 4; }

.bl-featured:hover .bl-cover-lg {
  animation-play-state: paused;
  transform: rotate(0) translateY(0) !important;
}

/* ---- 普通书单网格 ---- */
.booklist-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.15rem;
}

.booklist-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.28s ease;
  background: var(--bg-card);
}

.booklist-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.booklist-header {
  padding: 1.35rem 1.15rem;
  color: #fff;
  position: relative;
}

.booklist-badge {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(8px);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  border-radius: 20px;
  margin-bottom: 0.55rem;
}

.booklist-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 0.35rem;
}

.booklist-desc {
  font-size: 0.78rem;
  opacity: 0.85;
  margin: 0 0 0.45rem;
  line-height: 1.45;
}

.bl-mini-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.bl-mini-tag {
  padding: 1px 7px;
  background: rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.62rem;
  font-weight: 500;
  border-radius: 8px;
}

.booklist-books {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1rem;
  background: #FAFAFA;
}

.bl-mini-cover {
  width: 38px;
  height: 52px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
}

.bl-mini-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bl-more {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 500;
  margin-left: auto;
}

/* ===== FOOTER ===== */
.site-footer {
  background: #111111;
  color: #fff;
  padding: 2rem 0 1.5rem;
}

.footer-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  gap: 4rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #222;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.footer-logo svg {
  width: 24px;
  height: 24px;
  color: var(--primary);
}

.footer-desc {
  color: #6B7280;
  font-size: 0.875rem;
  margin: 0 0 1.25rem;
}

.social-links {
  display: flex;
  gap: 0.5rem;
}

.social-link {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1E1E1E;
  border: 1px solid #2A2A2A;
  border-radius: 50%;
  color: #6B7280;
  transition: all 0.2s ease;
}

.social-link:hover {
  color: #fff;
  border-color: #444;
}

.social-link svg {
  width: 16px;
  height: 16px;
}

.footer-links {
  display: flex;
  gap: 3rem;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.link-group h4 {
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 0.75rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.link-group a {
  color: #6B7280;
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s ease;
}

.link-group a:hover {
  color: #D1D5DB;
}

.footer-bottom {
  padding-top: 2rem;
  text-align: center;
}

.footer-bottom p {
  color: #374151;
  font-size: 0.8rem;
  margin: 0;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .ad-popup-card {
    width: 380px;
  }
  .ad-popup-img {
    height: 220px;
  }

  .hero-inner {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }

  .hero-content {
    text-align: center;
  }

  .hero-book-showcase {
    height: 320px;
  }

  .book-item {
    width: 110px;
    height: 160px;
  }

  .book-2 {
    width: 130px;
    height: 180px;
  }

  .book-4 {
    width: 120px;
    height: 170px;
  }

  .book-5 {
    width: 100px;
    height: 145px;
  }

  .stats-container {
    flex-wrap: wrap;
  }

  .stat-divider {
    display: none;
  }

  .stat-item {
    min-width: calc(50% - 1rem);
  }

  /* 新上架响应式 */
  .newbook-card {
    width: 140px;
  }

  /* 书单响应式 */
  .booklist-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .bl-featured-inner {
    padding: 2rem;
    min-height: 170px;
  }

  .bl-title--lg {
    font-size: 1.4rem;
  }

  .bl-cover-lg {
    width: 65px;
    height: 90px;
  }
}

@media (max-width: 768px) {
  .ad-popup-card {
    width: 92vw;
    border-radius: 12px;
  }
  .ad-popup-img {
    height: 180px;
  }
  .ad-popup-close {
    width: 28px;
    height: 28px;
  }
  .header-inner {
    padding: 0 1.25rem;
    gap: 1rem;
  }

  .main-nav {
    display: none;
  }

  .search-box {
    width: 150px;
  }

  .hero-inner {
    padding: 2rem 1.25rem;
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-book-showcase {
    height: 260px;
  }

  .book-item {
    width: 90px;
    height: 130px;
  }

  .book-2 {
    width: 105px;
    height: 150px;
  }

  .book-4 {
    width: 100px;
    height: 140px;
  }

  .book-5 {
    display: none;
  }

  .section-container {
    padding: 0 1.25rem;
  }

  .featured-section,
  .latest-section {
    padding: 1.5rem 0;
  }

  .categories-section {
    padding: 1.75rem 0;
  }

  .categories-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
  }

  .category-card {
    padding: 1rem 0.5rem;
  }

  .cat-icon {
    width: 32px;
    height: 32px;
  }

  .cat-icon svg {
    width: 18px;
    height: 18px;
  }

  .cat-name {
    font-size: 0.85rem;
  }

  /* 新上架响应式 */
  .newbook-card {
    width: 130px;
  }

  .newbook-info {
    padding: 0.5rem;
  }

  /* 榜单响应式 */
  .rank-cover {
    width: 36px;
    height: 48px;
  }

  /* 书单响应式 - 平板 */
  .booklist-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bl-featured-inner {
    flex-direction: column;
    text-align: center;
    padding: 2rem 1.5rem;
    min-height: auto;
  }

  .bl-desc--lg {
    max-width: none;
  }

  .bl-tags {
    justify-content: center;
  }

  .bl-featured-covers {
    justify-content: center;
  }

  .bl-title--lg {
    font-size: 1.25rem;
  }

  .bl-cover-lg {
    width: 56px;
    height: 78px;
  }

  .footer-content {
    flex-direction: column;
    gap: 2rem;
  }

  .footer-links {
    flex-wrap: wrap;
    gap: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-book-showcase {
    height: 200px;
  }

  .book-item {
    width: 70px;
    height: 100px;
  }

  .book-2 {
    width: 85px;
    height: 120px;
  }

  .book-3,
  .book-4 {
    display: none;
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-item {
    min-width: 100%;
  }

  /* 新上架手机端 */
  .newbook-card {
    width: 120px;
  }

  .scroll-controls {
    display: none;
  }

  /* 书单手机端 */
  .booklist-grid {
    grid-template-columns: 1fr;
  }

  .bl-featured-inner {
    padding: 1.5rem 1rem;
  }

  .bl-title--lg {
    font-size: 1.15rem;
  }

  .bl-cover-lg {
    width: 48px;
    height: 66px;
  }
}
</style>
