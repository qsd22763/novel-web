#!/usr/bin/env node
// vercel-build.js — Vercel 构建脚本
// 在 novel_frontend 目录下执行 npm install + vite build
const { execSync } = require('child_process');
const path = require('path');

const frontendDir = path.join(process.cwd(), 'novel_frontend');

console.log('=== 墨香书阁 Vercel 构建开始 ===');
console.log('前端目录:', frontendDir);

// 切换到前端目录并安装依赖
process.chdir(frontendDir);
console.log('\n[1/2] 安装前端依赖...');
execSync('npm install', { stdio: 'inherit' });

// 构建前端
console.log('\n[2/2] 构建前端...');
execSync('npm run build', { stdio: 'inherit' });

console.log('\n=== 构建完成 ===');
