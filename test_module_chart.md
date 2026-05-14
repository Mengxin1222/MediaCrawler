# Apricity-InnocoreAI 模块结构图

## 1. 整体模块结构

```mermaid
graph TB
    subgraph 入口层
        A[main.py 主入口]
        B[run.py 运行脚本]
        C[setup.py 安装脚本]
        D[diagnose.py 诊断工具]
    end
    
    subgraph API层
        E[api/main.py FastAPI服务]
    end
    
    subgraph Agent核心层
        F[agents/controller.py 控制器]
        G[agents/coach.py 教练Agent]
        H[agents/hunter.py 猎人Agent]
        I[agents/miner.py 矿工Agent]
        J[agents/validator.py 验证Agent]
        K[agents/base.py Agent基类]
    end
    
    subgraph 服务层
        L[services/user_service.py 用户服务]
        M[services/paper_service.py 论文服务]
        N[services/task_service.py 任务服务]
        O[services/analysis_service.py 分析服务]
        P[services/writing_service.py 写作服务]
    end
    
    subgraph 模型层
        Q[models/user.py 用户模型]
        R[models/paper.py 论文模型]
        S[models/task.py 任务模型]
        T[models/analysis.py 分析模型]
        U[models/writing.py 写作模型]
    end
    
    subgraph 核心基础设施层
        V[core/config.py 配置管理]
        W[core/llm_adapter.py LLM适配器]
        X[core/database.py 数据库]
        Y[core/vector_store.py 向量存储]
        Z[core/exceptions.py 异常处理]
    end
    
    subgraph 工具层
        AA[utils/pdf_parser.py PDF解析]
        AB[utils/text_processor.py 文本处理]
        AC[utils/embedding.py 嵌入向量]
        AD[utils/citation_formatter.py 引用格式化]
    end
    
    subgraph 前端层
        AE[frontend/index.html Web界面]
    end
    
    A --> E
    B --> A
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    G --> L
    H --> M
    I --> N
    J --> O
    K --> P
    L --> Q
    M --> R
    N --> S
    O --> T
    P --> U
    F --> V
    F --> W
    W --> X
    W --> Y
    M --> AA
    M --> AB
    M --> AC
    M --> AD
    E --> AE
```

### 图表解释

#### 1. 整体概述
- 这张图讲的是：Apricity-InnocoreAI 项目的模块组织结构
- 解决什么问题：看清项目分层和各模块职责
- 核心看点：6层架构 + Agent协作模式

#### 2. 关键元素说明
- **入口层**：程序启动入口，包含主程序、运行脚本、安装和诊断工具
- **API层**：FastAPI 提供 HTTP 接口
- **Agent核心层**：5种 Agent 角色（控制器、教练、猎人、矿工、验证）+ 基类
- **服务层**：业务逻辑封装，对应用户、论文、任务、分析、写作5个领域
- **模型层**：数据模型定义
- **核心基础设施层**：配置、LLM适配、数据库、向量存储
- **工具层**：PDF解析、文本处理、嵌入向量、引用格式化
- **前端层**：Web 界面

#### 3. 关键流程/关系说明
1. 用户通过 main.py 或 API 入口进入系统
2. 控制器 Agent 协调其他 Agent 协作
3. 各 Agent 调用对应服务处理业务
4. 服务层操作模型层读写数据
5. 基础设施层提供底层支持（LLM、数据库、向量存储）

#### 4. 关键技术解释
- **多Agent协作**：控制器 + 4个角色Agent，模拟研究团队分工
- **分层架构**：入口→API→Agent→服务→模型→基础设施，职责清晰
- **向量存储**：用于论文检索和相似度匹配
- **LLM适配器**：封装不同大模型接口，便于切换

#### 5. 设计意图
- 为什么要这样设计：模拟真实学术研究团队的角色分工
- 解决了什么痛点：复杂任务拆解为多个Agent协作，降低单Agent负担
- 带来了什么好处：模块化清晰，新增Agent类型只需扩展基类
- 如果不这样会怎样：单Agent处理所有逻辑，代码臃肿，难以维护

---

*生成时间: 2026-05-14*
*模式: 深度*
*所属项目: Apricity-InnocoreAI*
*文件包含: 1 张图*
