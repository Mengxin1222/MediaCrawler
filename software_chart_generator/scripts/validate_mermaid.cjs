#!/usr/bin/env node
/**
 * Mermaid 语法检测脚本（V2）
 * 使用 mermaid-syntax-parser 纯解析，无需浏览器
 * 支持：纯 mmd 文件、md 文件（自动提取 ```mermaid 代码块）
 */

const { ValidateMermaid } = require('mermaid-syntax-parser');
const fs = require('fs');

const args = process.argv.slice(2);
const inputFile = args[0];

if (!inputFile) {
  console.error(JSON.stringify({
    success: false,
    error: "No input file specified"
  }));
  process.exit(1);
}

const content = fs.readFileSync(inputFile, 'utf8');

// 从 md 文件中提取 mermaid 代码块
function extractMermaidCode(text) {
  const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
  const matches = [];
  let match;
  while ((match = mermaidRegex.exec(text)) !== null) {
    matches.push(match[1].trim());
  }
  // 如果没有找到代码块，假设整个文件就是 mermaid 代码
  if (matches.length === 0) {
    return [text.trim()];
  }
  return matches;
}

const codeBlocks = extractMermaidCode(content);

function validate() {
  const errors = [];

  for (let i = 0; i < codeBlocks.length; i++) {
    const code = codeBlocks[i];
    try {
      const valid = ValidateMermaid(code);
      if (!valid) {
        errors.push(`[代码块 ${i + 1}] 语法错误（可能是节点定义、连线或关键字有误）`);
      }
    } catch (err) {
      errors.push(`[代码块 ${i + 1}] ${err.message || String(err)}`);
    }
  }

  if (errors.length === 0) {
    console.log(JSON.stringify({ success: true }));
    process.exit(0);
  } else {
    console.error(JSON.stringify({
      success: false,
      error: errors.join("\n")
    }));
    process.exit(1);
  }
}

validate();
