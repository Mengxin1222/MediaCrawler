#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
使用 mermaid 核心包纯解析，无需浏览器
支持：自动安装依赖、错误截断、调试日志
"""

import subprocess
import sys
import os
import json
import tempfile
import re
from datetime import datetime


# ========== 配置 ==========
MAX_ERROR_LENGTH = 500       # 错误信息最大长度
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")


def ensure_logs_dir():
    """确保日志目录存在"""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)


def get_session_dir():
    """获取本次会话的日志目录（按时间命名）"""
    ensure_logs_dir()
    session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = os.path.join(LOGS_DIR, session_name)
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    return session_dir


def save_debug_log(session_dir, chart_name, attempt, code, error=None):
    """
    保存调试日志
    
    Args:
        session_dir: 本次会话的日志目录
        chart_name: 图表名称（如 "01-登录流程"）
        attempt: 尝试次数（1, 2, 3...）
        code: Mermaid 代码
        error: 错误信息（可选）
    """
    chart_dir = os.path.join(session_dir, chart_name)
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    # 保存代码
    code_file = os.path.join(chart_dir, f"attempt_{attempt}.mmd")
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    # 保存错误
    if error:
        error_file = os.path.join(chart_dir, f"attempt_{attempt}.error")
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error)


def save_success_log(session_dir, chart_name, code):
    """保存最终成功的版本"""
    chart_dir = os.path.join(session_dir, chart_name)
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    final_file = os.path.join(chart_dir, "final.mmd")
    with open(final_file, 'w', encoding='utf-8') as f:
        f.write(code)


def truncate_error(error_msg: str, max_length: int = MAX_ERROR_LENGTH) -> str:
    """
    截断错误信息，保留关键部分
    
    策略：保留前 200 字符（通常包含错误类型和行号）
          + 最后 100 字符（可能包含建议）
    """
    if len(error_msg) <= max_length:
        return error_msg
    
    head = error_msg[:200]
    tail = error_msg[-100:]
    omitted = len(error_msg) - 300
    
    return f"{head}\n... (省略 {omitted} 字符) ...\n{tail}"


def extract_error_key_info(error_msg: str) -> dict:
    """
    从 Mermaid 错误信息中提取关键信息
    
    Returns:
        dict: {
            "type": "parse" | "lexical" | "syntax" | "unknown",
            "line": int | None,
            "message": str,
            "suggestion": str
        }
    """
    lines = error_msg.strip().split('\n')
    
    result = {
        "type": "unknown",
        "line": None,
        "message": "",
        "suggestion": ""
    }
    
    for line in lines:
        line = line.strip()
        
        # 提取错误类型和行号
        if "Parse error on line" in line:
            result["type"] = "parse"
            match = re.search(r'line (\d+)', line)
            if match:
                result["line"] = int(match.group(1))
            result["message"] = line
            
        elif "Lexical error on line" in line:
            result["type"] = "lexical"
            match = re.search(r'line (\d+)', line)
            if match:
                result["line"] = int(match.group(1))
            result["message"] = line
            
        elif "Syntax error" in line:
            result["type"] = "syntax"
            result["message"] = line
            
        # 提取建议
        elif "Expecting" in line or "got" in line:
            result["suggestion"] = line
    
    return result


def format_error_for_model(error_msg: str) -> str:
    """
    把错误信息格式化成给模型看的简洁版本
    
    输出格式："第 X 行有错误 | 错误描述 | 建议: ..."
    """
    info = extract_error_key_info(error_msg)
    
    parts = []
    
    if info["line"]:
        parts.append(f"第 {info['line']} 行有错误")
    
    if info["message"]:
        parts.append(info["message"])
    
    if info["suggestion"]:
        parts.append(f"建议: {info['suggestion']}")
    
    # 如果提取失败，直接截断
    if not parts:
        return truncate_error(error_msg, 300)
    
    return " | ".join(parts)


def validate_mermaid(code: str, chart_name: str = "unknown", attempt: int = 1, enable_log: bool = True) -> dict:
    """
    检测 Mermaid 代码语法是否正确
    
    Args:
        code: Mermaid 代码字符串
        chart_name: 图表名称（用于日志）
        attempt: 尝试次数（用于日志）
        enable_log: 是否启用调试日志
    
    Returns:
        dict: {
            "success": bool,
            "error": str (仅当 success 为 False),
            "error_formatted": str (给模型看的精简版)
        }
    """
    session_dir = None
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.join(script_dir, "..")
        
        # 初始化日志
        if enable_log:
            session_dir = get_session_dir()
            save_debug_log(session_dir, chart_name, attempt, code)
        
        # 1. 检查 Node.js 是否安装
        try:
            node_check = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=package_dir
            )
            if node_check.returncode != 0:
                error = "Node.js is not installed. Please install Node.js from https://nodejs.org/"
                if enable_log and session_dir:
                    save_debug_log(session_dir, chart_name, attempt, code, error)
                return {
                    "success": False,
                    "error": error,
                    "error_formatted": error
                }
        except FileNotFoundError:
            error = "Node.js is not installed. Please install Node.js from https://nodejs.org/"
            if enable_log and session_dir:
                save_debug_log(session_dir, chart_name, attempt, code, error)
            return {
                "success": False,
                "error": error,
                "error_formatted": error
            }
        
        # 2. 检查 mermaid 是否安装，未安装则自动安装
        node_modules_dir = os.path.join(package_dir, "node_modules")
        mermaid_exists = os.path.exists(os.path.join(node_modules_dir, "mermaid"))
        
        if not mermaid_exists:
            print("Installing mermaid (this may take a minute)...", file=sys.stderr)
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=package_dir,
                capture_output=True,
                text=True,
                timeout=180
            )
            if npm_install.returncode != 0:
                error = f"Failed to install dependencies: {npm_install.stderr}"
                if enable_log and session_dir:
                    save_debug_log(session_dir, chart_name, attempt, code, error)
                return {
                    "success": False,
                    "error": error,
                    "error_formatted": error
                }
        
        # 3. 写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # 4. 调用 Node.js 脚本
            validate_script = os.path.join(script_dir, "validate_mermaid.js")
            result = subprocess.run(
                ["node", validate_script, temp_file],
                capture_output=True,
                text=True,
                timeout=45,
                cwd=package_dir
            )
            
            if result.returncode == 0:
                # 成功
                if enable_log and session_dir:
                    save_success_log(session_dir, chart_name, code)
                return {
                    "success": True
                }
            else:
                # 失败，解析错误
                try:
                    error_json = json.loads(result.stderr.strip())
                    raw_error = error_json.get("error", "Unknown error")
                except:
                    raw_error = (result.stderr or result.stdout or "Unknown error").strip()
                
                # 截断和格式化错误
                truncated = truncate_error(raw_error)
                formatted = format_error_for_model(raw_error)
                
                if enable_log and session_dir:
                    save_debug_log(session_dir, chart_name, attempt, code, truncated)
                
                return {
                    "success": False,
                    "error": truncated,
                    "error_formatted": formatted
                }
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    except subprocess.TimeoutExpired:
        error = "Validation timeout"
        if enable_log and session_dir:
            save_debug_log(session_dir, chart_name, attempt, code, error)
        return {
            "success": False,
            "error": error,
            "error_formatted": error
        }
    except Exception as e:
        error = str(e)
        if enable_log and session_dir:
            save_debug_log(session_dir, chart_name, attempt, code, error)
        return {
            "success": False,
            "error": error,
            "error_formatted": error
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python validate_wrapper.py <mermaid_code_or_file>"
        }))
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    if os.path.isfile(input_arg):
        code = open(input_arg, 'r', encoding='utf-8').read()
    else:
        code = input_arg
    
    result = validate_mermaid(code, chart_name="test", attempt=1)
    print(json.dumps(result, ensure_ascii=False))
