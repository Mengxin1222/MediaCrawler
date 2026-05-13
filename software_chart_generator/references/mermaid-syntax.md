# Mermaid 语法参考

## 1. 时序图 (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant A as 前端
    participant B as 后端
    participant C as 数据库
    
    User->>A: 点击按钮
    activate A
    A->>B: POST /api/data
    activate B
    
    alt 缓存命中
        B->>B: 读取缓存
    else 缓存未命中
        B->>C: SELECT * FROM table
        activate C
        C-->>B: 返回数据
        deactivate C
        B->>B: 写入缓存
    end
    
    B-->>A: JSON响应
    deactivate B
    A-->>User: 展示结果
    deactivate A
```

**关键语法**：
- `actor` / `participant`：定义参与者
- `->>`：实线箭头（请求）
- `-->>`：虚线箭头（返回）
- `activate` / `deactivate`：激活框
- `alt` / `else` / `end`：条件分支
- `loop` / `end`：循环
- `opt` / `end`：可选步骤
- `autonumber`：自动编号

## 2. 用例图 (Use Case Diagram)

```mermaid
graph TB
    subgraph 用户角色
        U1[普通用户]
        U2[管理员]
    end
    
    subgraph 认证模块
        UC1[登录]
        UC2[注册]
        UC3[找回密码]
    end
    
    subgraph 业务模块
        UC4[查看数据]
        UC5[导出报表]
        UC6[系统配置]
    end
    
    U1 --> UC1
    U1 --> UC2
    U1 --> UC3
    U1 --> UC4
    U1 --> UC5
    
    U2 --> UC1
    U2 --> UC4
    U2 --> UC5
    U2 --> UC6
    
    UC1 -.包含.-> UC2
    UC4 -.扩展.-> UC5
```

**关键语法**：
- `subgraph`：分组
- `-->`：关联关系
- `-.包含.->`：包含关系（include）
- `-.扩展.->`：扩展关系（extend）

## 3. E-R图 (Entity Relationship Diagram)

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ REVIEW : writes
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "included in"
    
    USER {
        int user_id PK
        string username
        string email
        datetime created_at
    }
    
    ORDER {
        int order_id PK
        int user_id FK
        decimal total_amount
        string status
        datetime created_at
    }
    
    ORDER_ITEM {
        int item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
    
    PRODUCT {
        int product_id PK
        string name
        string description
        decimal price
        int stock
    }
    
    REVIEW {
        int review_id PK
        int user_id FK
        int product_id FK
        int rating
        string comment
    }
```

**关键语法**：
- `||--o{`：关系类型（1对多）
- `PK`：主键
- `FK`：外键
- 关系类型：`||`（1）、`o|`（0或1）、`o{`（0或多）、`|{`（1或多）

## 4. 系统架构图 (Architecture Diagram)

```mermaid
graph TB
    subgraph 客户端层
        C1[Web浏览器<br/>React]
        C2[移动端App<br/>Flutter]
        C3[管理后台<br/>Vue]
    end
    
    subgraph 网关层
        G1[Nginx反向代理]
        G2[API Gateway<br/>Kong]
    end
    
    subgraph 服务层
        S1[用户服务<br/>Node.js]
        S2[订单服务<br/>Java Spring]
        S3[支付服务<br/>Go]
        S4[通知服务<br/>Python]
    end
    
    subgraph 数据层
        D1[(MySQL<br/>主从集群)]
        D2[(Redis<br/>缓存)]
        D3[(MongoDB<br/>日志)]
        D4[(Elasticsearch<br/>搜索)]
    end
    
    subgraph 外部服务
        E1[支付宝API]
        E2[微信支付API]
        E3[短信服务商]
    end
    
    C1 --> G1
    C2 --> G1
    C3 --> G2
    G1 --> G2
    
    G2 --> S1
    G2 --> S2
    G2 --> S3
    G2 --> S4
    
    S1 --> D1
    S1 --> D2
    S2 --> D1
    S2 --> D3
    S3 --> D1
    S3 --> E1
    S3 --> E2
    S4 --> E3
    S4 --> D3
    
    S1 -.-> D4
    S2 -.-> D4
```

**关键语法**：
- `subgraph`：层次分组
- `-->`：调用关系
- `-.->`：间接依赖
- `[文本]`：矩形节点
- `[(文本)]`：圆柱形（数据库）
- `((文本))`：圆形
- `{文本}`：菱形

## 5. 业务流程图 (Flowchart)

```mermaid
graph TB
    Start([开始]) --> Input[输入用户名密码]
    Input --> Validate{验证格式}
    
    Validate -->|格式错误| Error1[提示格式错误]
    Error1 --> Input
    
    Validate -->|格式正确| CheckDB{查询数据库}
    
    CheckDB -->|用户不存在| Register{是否注册}
    Register -->|是| CreateUser[创建用户]
    Register -->|否| End1([结束])
    CreateUser --> SendVerify[发送验证邮件]
    
    CheckDB -->|密码错误| Error2[提示密码错误]
    Error2 --> Retry{重试次数<3}
    Retry -->|是| Input
    Retry -->|否| Lock[锁定账户]
    Lock --> End1
    
    CheckDB -->|验证通过| GenToken[生成JWT令牌]
    SendVerify --> GenToken
    GenToken --> SetCookie[设置Cookie]
    SetCookie --> Log[记录登录日志]
    Log --> End2([登录成功])
```

**关键语法**：
- `([文本])`：圆角矩形（开始/结束）
- `[文本]`：矩形（处理步骤）
- `{文本}`：菱形（判断）
- `-->|标签|`：带标签的箭头
- 方向：`TB`（上下）、`LR`（左右）、`RL`（右左）、`BT`（下上）

## 6. 模块结构图 (Module/Package Diagram)

```mermaid
graph TB
    subgraph 入口层
        M1[main.py<br/>程序入口]
        M2[api/main.py<br/>API入口]
    end
    
    subgraph 核心层
        C1[core.py<br/>业务逻辑核心]
        C2[client.py<br/>API客户端]
        C3[login.py<br/>认证模块]
    end
    
    subgraph 基础设施层
        I1[proxy/<br/>代理管理]
        I2[cache/<br/>缓存系统]
        I3[store/<br/>数据存储]
        I4[database/<br/>数据库ORM]
    end
    
    subgraph 工具层
        U1[utils.py<br/>通用工具]
        U2[logger.py<br/>日志系统]
        U3[config.py<br/>配置管理]
    end
    
    M1 --> C1
    M2 --> C1
    
    C1 --> C2
    C1 --> C3
    C2 --> I1
    C2 --> I2
    C3 --> I4
    
    C1 --> I3
    I3 --> I4
    
    C1 --> U1
    C2 --> U2
    M1 --> U3
    M2 --> U3
    
    style C1 fill:#f9f,stroke:#333,stroke-width:2px
    style I3 fill:#bbf,stroke:#333
```

**关键语法**：
- `subgraph`：模块分组
- `-->`：依赖/导入关系
- `style`：自定义样式
- `<br/>`：换行

## 通用技巧

### 样式自定义
```mermaid
graph LR
    A[默认样式]
    B[自定义样式]
    C[强调样式]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#f66,stroke-width:2px,stroke-dasharray: 5 5
    style C fill:#9f9,stroke:#333,stroke-width:4px
```

### 注释
```mermaid
%% 这是注释，不会渲染
graph LR
    A --> B
```

### 子图方向
```mermaid
graph TB
    subgraph 水平布局
        direction LR
        A --> B --> C
    end
    
    subgraph 垂直布局
        direction TB
        D --> E --> F
    end
```
