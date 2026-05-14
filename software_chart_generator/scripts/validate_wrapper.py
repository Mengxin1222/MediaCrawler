#!/usr/bin/env python3
import subprocess
import sys
import os
import json
import tempfile
import time


def validate_mermaid(code: str) -> dict:
    """
    检测 Mermaid 代码语法是否正确

    Returns:
        dict: {
            "success": bool,
            "error": str (if success is False)
        }
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.join(script_dir, "..")

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
                return {
                    "success": False,
                    "error": "Node.js is not installed. Please install Node.js from https://nodejs.org/"
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Node.js is not installed. Please install Node.js from https://nodejs.org/"
            }

        # 2. 检查 mermaid-cli 是否安装，若未安装则自动安装
        node_modules_dir = os.path.join(package_dir, "node_modules")
        mmdc_exists = (
            os.path.exists(os.path.join(node_modules_dir, ".bin", "mmdc")) or
            os.path.exists(os.path.join(node_modules_dir, ".bin", "mmdc.cmd"))
        )

        if not mmdc_exists:
            print("Installing Mermaid CLI dependencies (this may take a minute)...", file=sys.stderr)
            npm_install = subprocess.run(
                ["npm", "install"],
                cwd=package_dir,
                capture_output=True,
                text=True,
                timeout=180
            )
            if npm_install.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to install dependencies: {npm_install.stderr}"
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
                return {
                    "success": True
                }
            else:
                try:
                    error_json = json.loads(result.stderr.strip())
                    return error_json
                except:
                    return {
                        "success": False,
                        "error": (result.stderr or result.stdout or "Unknown error").strip()
                    }
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Validation timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
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

    result = validate_mermaid(code)
    print(json.dumps(result, ensure_ascii=False))
#!/usr/bin/env python3
""#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
    按优先级查找：
    1.#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
    按优先级查找：
    1. node_modules/.bin/mmdc（本地安装#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
    按优先级查找：
    1. node_modules/.bin/mmdc（本地安装）
    2. npx m#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
    按优先级查找：
    1. node_modules/.bin/mmdc（本地安装）
    2. npx mmdc（全局或通过 npx）
#!/usr/bin/env python3
"""
Mermaid 语法检测的 Python 包装脚本（V2）
作用：自动安装 Node.js 依赖、调用 Node.js 检测脚本、返回结构化结果
V2 优化：更健壮的路径查找、错误信息截断、错误类型分类
"""

import subprocess
import sys
import os
import json
import tempfile
import hashlib


def _find_mmdc_binary(package_dir: str) -> str:
    """
    查找 mmdc 可执行文件的路径
    
    按优先级查找：
    1. node_modules/.bin/mmdc（本地安装）
    2. npx mmdc（全局或通过 npx）
    3. 报错
    
