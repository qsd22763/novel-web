// Vercel Serverless 单函数入口
const { handler } = require('./api');

module.exports = async (req, res) => {
  try {
    return await handler(req, res);
  } catch (e) {
    console.error('API Handler 错误:', e.message || e);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Internal Server Error', message: e.message });
    }
  }
};

// 本地开发
if (require.main === module) {
  const { startLocal } = require('./api');
  startLocal();
}
