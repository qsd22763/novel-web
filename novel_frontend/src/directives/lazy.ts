import { createApp, type Directive } from 'vue'

const observerMap = new WeakMap<HTMLElement, IntersectionObserver>()

const lazyLoad: Directive = {
  mounted(el: HTMLElement, binding) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = el as HTMLImageElement
            const src = binding.value
            if (src) {
              img.src = src
              img.onerror = () => {
                img.src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'
                img.onerror = null
              }
            }
            observer.unobserve(el)
          }
        })
      },
      {
        rootMargin: '50px 0px',
        threshold: 0.01,
      }
    )

    observer.observe(el)
    observerMap.set(el, observer)
  },
  unmounted(el: HTMLElement) {
    const observer = observerMap.get(el)
    if (observer) {
      observer.unobserve(el)
      observerMap.delete(el)
    }
  },
}

export const setupLazyLoadDirective = (app: ReturnType<typeof createApp>) => {
  app.directive('lazy', lazyLoad)
}

export default lazyLoad