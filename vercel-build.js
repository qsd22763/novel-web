#!/usr/bin/env node
// vercel-build.js — Vercel 构建脚本
// 在 novel_frontend 目录下执行 npm install + vite build，然后复制 dist 到项目根目录
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const rootDir = process.cwd();
const frontendDir = path.join(rootDir, 'novel_frontend');
const srcDist = path.join(frontendDir, 'dist');
const dstDist = path.join(rootDir, 'dist');

console.log('=== 墨香书阁 Vercel 构建开始 ===');
console.log('前端目录:', frontendDir);

// 切换到前端目录并安装依赖
process.chdir(frontendDir);
console.log('\n[1/3] 安装前端依赖...');
execSync('npm install', { stdio: 'inherit' });

// 构建前端 (vite 输出到 novel_frontend/dist)
console.log('\n[2/3] 构建前端...');
execSync('npm run build', { stdio: 'inherit' });

// 复制到项目根目录 /dist（Vercel outputDirectory 指向这里）
console.log('\n[3/3] 复制构建产物到根目录...');
if (fs.existsSync(dstDist)) {
  fs.rmSync(dstDist, { recursive: true });
}
fs.cpSync(srcDist, dstDist, { recursive: true });
console.log(`  ${srcDist} -> ${dstDist}`);

console.log('\n=== 构建完成 ===');
