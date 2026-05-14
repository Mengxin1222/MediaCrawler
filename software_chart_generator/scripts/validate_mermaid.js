#!/usr/bin/env node
/**
 * Mermaid 语法检测脚本（V2）
 * 使用 mermaid 核心包纯解析，无需浏览器
 * 
 * 注意：mermaid v11+ 是 ES Module，需要用动态 import
 */

const fs = require('fs');

// 动态导入 mermaid（ES Module）
async function validate(inputFile) {
  if (!inputFile) {
    console.error(JSON.stringify({
      success: false,
      error: "No input file specified"
    }));
    process.exit(1);
  }

  // 读取 Mermaid 代码
  const code = fs.readFileSync(inputFile, 'utf8');

  try {
    // 动态导入 mermaid
    const mermaid = await import('mermaid');
    
    // 初始化（不启动浏览器）
    mermaid.default.initialize({
      startOnLoad: false,
      securityLevel: 'strict'
    });

    // 纯解析检测语法
    await mermaid.default.parse(code);
    
    console.log(JSON.stringify({ success: true }));
    process.exit(0);
  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message || String(error)
    }));
    process.exit(1);
  }
}

// 获取命令行参数并执行
const args = process.argv.slice(2);
validate(args[0]);
