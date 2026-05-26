import { createApp, type Directive } from 'vue'

const observerMap = new WeakMap<HTMLElement, IntersectionObserver>()

const lazyLoad: Directive = {
  mounted(el: HTMLElement, _binding) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = el as HTMLImageElement
            if (img.dataset.src) {
              img.src = img.dataset.src
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

    const img = el as HTMLImageElement
    if (img.dataset.src) {
      observer.observe(el)
    }

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
