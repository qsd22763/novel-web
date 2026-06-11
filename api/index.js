// Vercel Serverless 单函数入口
const { handler } = require('./api');
module.exports = handler;

// 本地开发
if (require.main === module) {
  const { startLocal } = require('./api');
  startLocal();
}
