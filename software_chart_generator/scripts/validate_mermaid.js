#!/usr/bin/env node
/**
 * Mermaid 语法检测脚本（V2）
 * 使用 mermaid-cli 的 mmdc 命令检测语法
 */

const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile) {
  console.error(JSON.stringify({
    success: false,
    error: "No input file specified"
  }));
  process.exit(1);
}

// 读取 Mermaid 代码
const code = fs.readFileSync(inputFile, 'utf8');

// 临时输出文件
const tempOutput = path.join(path.dirname(inputFile), `.temp-${Date.now()}.svg`);

// 查找本地安装的 mmdc
const scriptDir = __dirname;
const packageDir = path.join(scriptDir, '..');
const mmdcBin = path.join(packageDir, 'node_modules', '.bin', 'mmdc');

if (!fs.existsSync(mmdcBin)) {
  console.error(JSON.stringify({
    success: false,
    error: "mmdc not found. Please run 'npm install' in the package directory."
  }));
  process.exit(1);
}

execFile(mmdcBin, ['-i', inputFile, '-o', tempOutput], (error, stdout, stderr) => {
  // 清理临时文件
  try {
    if (fs.existsSync(tempOutput)) {
      fs.unlinkSync(tempOutput);
    }
  } catch (e) {}

  if (error) {
    const errorMsg = stderr || stdout || error.message || "Unknown error";
    console.error(JSON.stringify({
      success: false,
      error: errorMsg.trim()
    }));
    process.exit(1);
  } else {
    console.log(JSON.stringify({ success: true }));
    process.exit(0);
  }
});
