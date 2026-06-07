/**
 * 默认封面图（内联SVG Data URI，与站点视觉风格统一）
 * 古铜色调 + 书本图标 + "墨香书阁 暂无封面"
 */
export const DEFAULT_COVER = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="400" viewBox="0 0 300 400">' +
  '<defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">' +
  '<stop offset="0%" style="stop-color:#2A2018"/><stop offset="100%" style="stop-color:#1A1410"/>' +
  '</linearGradient></defs>' +
  '<rect width="300" height="400" rx="4" fill="url(#bg)"/>' +
  '<rect x="12" y="12" width="276" height="376" rx="2" fill="none" stroke="#CA8A04" stroke-width="1" opacity="0.4"/>' +
  '<text x="150" y="295" text-anchor="middle" font-family="serif" font-size="20" fill="#CA8A04" letter-spacing="6" opacity="0.7">墨香书阁</text>' +
  '<text x="150" y="325" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#9CA3AF" letter-spacing="2" opacity="0.5">暂无封面</text></svg>'
)

export function resolveCover(src: string | null | undefined): string {
  if (!src) return DEFAULT_COVER
  if (src.startsWith('http://') || src.startsWith('https://') || src.startsWith('data:')) return src
  if (src.startsWith('/')) return src
  return src
}
