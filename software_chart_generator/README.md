# Software Chart Generator

自动分析源码并生成 6 种软件开发标准图表的 AI Skill。

## 功能特点

- **深度分析**：基于实际代码结构生成图表，不是凭空想象
- **6 种图表类型**：时序图、用例图、数据流E-R图、系统架构图、业务流程图、模块结构图
- **Mermaid 语法**：输出标准 Mermaid 图表，支持 GitHub/GitLab/VS Code 直接渲染
- **并发加速**：多类图时自动并发生成
- **自动校验**：Mermaid 语法自动检查，出错自动重画

## 触发方式

```
/software-chart-generator [图类型] [源码路径]
```

- **图类型**：sequence / usecase / er / architecture / business / module / all
- **源码路径**：本地目录或 GitHub URL

## 示例

```bash
# 生成模块结构图
/software-chart-generator module ./src

# 生成系统架构图
/software-chart-generator architecture /path/to/project

# 生成全部 6 种图（并发）
/software-chart-generator all ./my-project
```

## 支持的图类型

| 类型 | 关键词 | 说明 |
|------|--------|------|
| 时序图 | sequence | 对象间交互时间顺序 |
| 用例图 | usecase | 系统功能与用户角色关系 |
| 数据流E-R图 | er / dataflow | 数据流动与实体关系 |
| 系统架构图 | architecture | 分层架构与技术栈 |
| 业务流程图 | business | 业务操作执行流程 |
| 模块结构图 | module | 代码模块组织与依赖 |
| 全部 | all | 并发生成所有 6 种图 |

## 输出格式

每种图类型输出一个 Markdown 文件：

```
[项目名]-charts/
├── 01-sequence-diagram.md
├── 02-use-case-diagram.md
├── 03-data-flow-er-diagram.md
├── 04-system-architecture.md
├── 05-business-process.md
└── 06-module-structure.md
```

每个文件包含多张图表，每张图都有 5 段式解释：
1. 整体概述
2. 关键元素说明
3. 关键流程/关系说明
4. 关键技术解释
5. 设计意图

## 安装

1. 下载 `software_chart_generator` 目录或压缩包
2. 放入你的 AI Assistant 的 skills 目录
3. 重启 AI Assistant

## 使用前提

- 需要 AI Assistant 支持 Skill 插件
- Mermaid 渲染需要 Markdown 阅读器支持（如 VS Code + Mermaid 插件、GitHub、GitLab）

## License

MIT
