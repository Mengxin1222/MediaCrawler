# Hello-Agents 时序图

## 1. ReAct Agent 执行时序

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant RA as ReActAgent
    participant LLM as HelloAgentsLLM
    participant TE as ToolExecutor
    participant ST as SearchTool

    U->>RA: 提问（query）
    RA->>RA: 初始化对话上下文（context）
    loop ReAct 循环
        RA->>RA: 构建 Prompt（system + history + tools）
        RA->>LLM: 发送 Prompt 请求推理
        LLM-->>RA: 返回 Thought + Action
        RA->>RA: 解析 LLM 输出（parse_thought_action）
        alt Action 类型为 Finish
            RA-->>U: 返回最终答案（final_answer）
        else Action 类型为 Tool 调用
            RA->>TE: 调用工具（tool_name, tool_input）
            TE->>ST: 执行 SearchTool.search(...)
            ST-->>TE: 返回 Observation（搜索结果）
            TE-->>RA: 返回工具执行结果
            RA->>RA: 将 Observation 追加到上下文
        end
    end
```

### 解释

**触发阶段**：用户向 ReActAgent 发起提问，Agent 首先初始化当前的对话上下文，包括系统提示词、历史对话记录以及可用工具的 Schema 描述。这一步为后续的推理循环奠定基础。

**推理阶段**：ReActAgent 将上下文构建成完整的 Prompt 并发送给 HelloAgentsLLM。LLM 基于 ReAct 范式生成包含 Thought（思考过程）和 Action（行动指令）的结构化输出，体现了"先思考再行动"的核心理念。

**解析阶段**：Agent 对 LLM 的原始输出进行解析，提取 Thought 和 Action 的内容，并判断 Action 的类型。如果是 Finish 类型，说明 LLM 认为已经得到最终答案，循环终止；否则进入工具执行阶段。

**执行阶段**：当 Action 为 Tool 调用时，Agent 将工具名称和参数传递给 ToolExecutor。ToolExecutor 负责路由到具体的 SearchTool 并执行搜索操作，获取外部知识或数据作为 Observation。

**循环阶段**：工具执行返回的 Observation 被追加到上下文中，Agent 再次构建 Prompt 进入下一轮 ReAct 循环，直到 LLM 输出 Finish 动作为止，最终向用户返回答案。

---

## 2. MCP 工具调用时序（旅行助手场景）

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant FE as Frontend
    participant BE as FastAPI Backend
    participant TPA as TripPlannerAgent
    participant MCP as MCPTool
    participant AMS as AmapMCPService

    U->>FE: 输入目的地（如"杭州"）
    FE->>BE: POST /api/trip/plan {destination}
    BE->>TPA: 调用 plan_trip(destination)
    TPA->>TPA: 分析用户需求并拆解任务
    TPA->>MCP: 调用 MCP 工具（amap_search_poi）
    MCP->>AMS: 发送 MCP 请求（JSON-RPC）
    AMS->>AMS: 构造高德 API 请求参数
    AMS->>AMS: 调用高德 POI 搜索 API
    AMS-->>MCP: 返回 POI 数据列表
    MCP-->>TPA: 返回结构化 POI 结果
    TPA->>TPA: 基于 POI 数据生成行程规划
    TPA-->>BE: 返回行程方案（itinerary）
    BE-->>FE: 返回 JSON 响应
    FE-->>U: 展示行程卡片与地图
```

### 解释

**触发阶段**：用户在旅行助手前端界面输入目的地（如"杭州"），Frontend 将用户输入封装为 HTTP POST 请求发送到 FastAPI Backend 的 `/api/trip/plan` 接口，携带目的地参数。

**分析阶段**：Backend 将请求转发给 TripPlannerAgent，Agent 首先分析用户的出行需求，将整体任务拆解为多个子任务，例如搜索景点、餐厅、酒店等 POI（兴趣点）信息。

**调用阶段**：TripPlannerAgent 通过 MCPTool 接口发起工具调用，使用 `amap_search_poi` 工具名称和相应参数。MCPTool 作为 MCP 协议的客户端，将请求序列化为 JSON-RPC 格式发送给 AmapMCPService。

**服务阶段**：AmapMCPService 接收到 MCP 请求后，构造对应的高德地图开放平台 API 请求，调用高德 POI 搜索接口获取实时数据，并将原始 API 响应解析为结构化数据返回给 MCPTool。

**生成阶段**：TripPlannerAgent 获得 POI 数据后，结合时间、距离、用户偏好等因素生成完整的行程规划方案（itinerary），经 Backend 返回给 Frontend，最终以行程卡片和地图的形式展示给用户。

---

## 3. A2A 多智能体通信时序

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant AC as A2AClient
    participant AS as A2AServer(calculator-agent)
    participant SR as SkillRegistry

    U->>AC: 发送计算查询（如"2+3*4"）
    AC->>AC: 封装 A2A 消息（A2AMessage）
    AC->>AS: 发送 A2A 请求（HTTP/JSON）
    AS->>AS: 解析 A2A 消息头与载荷
    AS->>SR: 查询技能注册表（skill_name）
    SR-->>AS: 返回技能处理器（SkillHandler）
    AS->>AS: 路由到 calculator Skill 执行计算
    AS->>AS: 执行计算逻辑（2+3*4=14）
    AS-->>AC: 返回 A2A 响应（result=14）
    AC-->>U: 展示计算结果
```

### 解释

**触发阶段**：用户向 A2AClient 发送一个计算查询请求，例如数学表达式"2+3*4"。A2AClient 作为多智能体通信的客户端入口，负责接收用户输入并准备后续的消息封装。

**封装阶段**：A2AClient 将用户的原始查询按照 A2A（Agent-to-Agent）协议规范封装为 A2AMessage 对象，包含消息头（metadata、sender、receiver）和载荷（payload），确保消息格式符合 A2A 标准。

**通信阶段**：封装好的 A2A 消息通过 HTTP/JSON 传输到 A2AServer，Server 端首先解析消息头和载荷，提取目标技能名称（如 calculator），然后向 SkillRegistry 查询对应的技能处理器。

**路由阶段**：SkillRegistry 根据技能名称返回对应的 SkillHandler，A2AServer 将请求路由到 calculator-agent 的计算技能模块执行具体的计算逻辑，得到结果 14。

**返回阶段**：A2AServer 将计算结果封装为 A2A 响应消息返回给 A2AClient，Client 解析响应后向用户展示最终结果，完成一次完整的 A2A 多智能体通信闭环。
