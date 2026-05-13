# MediaCrawler 业务流程图 (Business Process Diagram)

## 1. 整体业务流程图

```mermaid
graph TB
    Start([开始]) --> Config[读取配置参数]
    Config --> Validate{参数校验}
    Validate -->|无效| Error1[报错退出]
    Validate -->|有效| InitProxy[初始化代理池]
    
    InitProxy --> InitBrowser[启动浏览器]
    InitBrowser --> CheckLogin{检查登录态}
    
    CheckLogin -->|已登录| SelectType[选择爬取类型]
    CheckLogin -->|未登录| Login[执行登录]
    Login --> LoginSuccess{登录成功?}
    LoginSuccess -->|否| Error2[登录失败退出]
    LoginSuccess -->|是| SelectType
    
    SelectType -->|搜索| SearchProcess[搜索关键词流程]
    SelectType -->|详情| DetailProcess[指定帖子流程]
    SelectType -->|创作者| CreatorProcess[创作者主页流程]
    
    SearchProcess --> StoreData[存储数据]
    DetailProcess --> StoreData
    CreatorProcess --> StoreData
    
    StoreData --> GenReport[生成报告/词云]
    GenReport --> Cleanup[清理资源]
    Cleanup --> End([结束])
    
    Error1 --> End
    Error2 --> End
```

### 图表解释

#### 1. 整体概述
该图描述了 MediaCrawler 爬虫系统从启动到结束的完整生命周期。流程以配置读取为起点，经过环境初始化、身份认证、任务分发、数据存储、报告生成和资源清理六个阶段，形成一条端到端的业务主线。系统支持三种爬取模式（搜索、详情、创作者），并在关键节点设置了校验和错误处理分支，确保异常情况下能够安全退出。

#### 2. 关键元素说明
- **配置参数**：包括目标平台、爬取类型、关键词列表、并发数、存储方式等运行时配置，通常从配置文件或命令行参数注入。
- **代理池**：维护一组可用的代理 IP，用于轮换请求来源，降低被封禁的风险。
- **浏览器实例**：基于 Playwright 或 Selenium 启动的 headless 浏览器，负责渲染动态页面和执行 JavaScript。
- **登录态**：通过 Cookie 或本地存储维护的会话状态，决定是否需要重新认证。
- **爬取类型**：搜索模式按关键词检索；详情模式抓取指定帖子；创作者模式遍历用户主页内容。

#### 3. 关键流程/关系说明
流程的主干顺序为：读取配置 → 校验参数 → 初始化代理 → 启动浏览器 → 检查登录态 → 选择爬取类型 → 执行爬取 → 存储数据 → 生成报告 → 清理资源。两条错误分支分别处理参数无效和登录失败，均直接导向结束节点，避免无效执行。三种爬取模式为互斥选择，最终汇入统一的数据存储节点，体现业务逻辑的收敛性。

#### 4. 关键技术解释
- **参数校验**：在流程早期进行 schema 校验，防止非法配置进入后续阶段，属于 fail-fast 设计。
- **代理池初始化**：涉及代理供应商 API 调用、可用性探测和池化维护，通常采用异步加载以缩短启动时间。
- **浏览器启动**：需要管理 WebDriver 或 CDP（Chrome DevTools Protocol）连接，以及上下文隔离和 Cookie 注入。
- **登录态检查**：通过访问需要登录才能访问的接口或页面元素，判断当前会话是否有效，避免重复登录。

#### 5. 设计意图
该流程图采用线性主干加错误旁路的设计，核心目标是保证爬虫在复杂网络环境下的鲁棒性和可维护性。将配置校验前置、资源清理后置，符合资源安全原则。三种爬取模式共享存储和报告生成逻辑，减少了代码冗余。错误分支直接终止而非重试，是因为启动阶段的错误通常不可恢复，避免无意义的循环消耗资源。

## 2. 搜索关键词业务流程

```mermaid
graph TB
    Start([开始搜索]) --> ReadKeywords[读取关键词列表]
    ReadKeywords --> Split[按逗号分割关键词]
    Split --> LoopKeyword{还有关键词?}
    
    LoopKeyword -->|是| SetKeyword[设置当前关键词]
    SetKeyword --> InitPage[页码=1]
    InitPage --> LoopPage{达到最大数量?}
    
    LoopPage -->|否| BuildRequest[构建搜索请求]
    BuildRequest --> GenSign[生成请求签名]
    GenSign --> SendRequest[发送HTTP请求]
    SendRequest --> CheckResponse{响应正常?}
    
    CheckResponse -->|否| HandleError[错误处理]
    HandleError --> Retry{重试次数<3?}
    Retry -->|是| SendRequest
    Retry -->|否| NextPage[下一页]
    
    CheckResponse -->|是| ParseList[解析帖子列表]
    ParseList --> HasMore{has_more?}
    HasMore -->|否| LoopPage
    HasMore -->|是| ExtractIds[提取帖子ID列表]
    
    ExtractIds --> LoopNote{还有帖子?}
    LoopNote -->|是| GetDetail[获取帖子详情]
    GetDetail --> ParseDetail[解析帖子内容]
    ParseDetail --> SaveNote[保存帖子数据]
    
    SaveNote --> NeedComment{启用评论?}
    NeedComment -->|是| GetComments[获取评论]
    GetComments --> SaveComments[保存评论数据]
    SaveComments --> LoopNote
    NeedComment -->|否| LoopNote
    
    LoopNote -->|否| NeedMedia{下载媒体?}
    NeedMedia -->|是| DownloadMedia[下载图片/视频]
    DownloadMedia --> SaveMedia[保存媒体文件]
    SaveMedia --> Sleep1[睡眠间隔]
    NeedMedia -->|否| Sleep1
    
    Sleep1 --> NextPage
    NextPage --> LoopPage
    LoopPage -->|是| LoopKeyword
    LoopKeyword -->|否| End([搜索结束])
```

### 图表解释

#### 1. 整体概述
该图描述了基于关键词的搜索爬取流程，采用双层循环结构：外层按关键词迭代，内层按分页迭代。每个分页获取帖子列表后，再对每个帖子进行详情解析、评论抓取和媒体下载。流程中嵌入了请求签名、错误重试、数量控制和睡眠间隔等机制，构成一个完整的批量数据采集闭环。

#### 2. 关键元素说明
- **关键词列表**：用户输入的搜索词集合，以逗号分隔，支持批量任务。
- **请求签名**：针对目标平台 API 的加密签名，通常基于时间戳、参数和密钥生成，用于通过服务端校验。
- **has_more**：分页标志字段，指示是否存在下一页数据，决定内层循环是否继续。
- **帖子ID列表**：从列表页提取的唯一标识符，用于后续详情接口的批量请求。
- **睡眠间隔**：控制请求频率的延时操作，降低触发反爬策略的概率。

#### 3. 关键流程/关系说明
外层循环控制关键词粒度：读取 → 分割 → 逐词处理。内层循环控制分页粒度：构建请求 → 签名 → 发送 → 解析列表 → 提取 ID → 遍历帖子。每个帖子内部又分出评论和媒体两个可选分支，通过条件判断决定是否执行。错误处理分支在请求异常时提供最多 3 次重试，超过则进入下一页，避免单点阻塞整体进度。

#### 4. 关键技术解释
- **请求签名生成**：通常采用 HMAC-SHA256 或 MD5 算法，将请求参数按特定规则排序后加盐计算，防止请求被篡改或重放。
- **错误重试机制**：采用固定次数重试（最多 3 次），属于断路器模式的简化实现，避免对故障接口无限重试。
- **分页控制**：通过 has_more 字段和最大数量双重限制，防止无限循环，同时支持增量采集。
- **睡眠间隔**：通常配合随机抖动（jitter）使用，使请求间隔呈非规律性分布，降低被频率检测识别的概率。

#### 5. 设计意图
该流程的设计核心是"可控的批量并发"。双层循环结构实现了任务的分层拆解，使每个关键词和每页数据都能独立处理。可选的评论和媒体分支通过条件开关控制，提升了流程的灵活性，适应不同业务场景的需求。重试和睡眠机制的组合，在采集效率和系统稳定性之间取得平衡，既保证数据完整性，又降低被封禁的风险。

## 3. 登录认证业务流程

```mermaid
graph TB
    Start([开始登录]) --> CheckType{登录类型}
    
    CheckType -->|二维码| QrcodeFlow
    CheckType -->|手机| PhoneFlow
    CheckType -->|Cookie| CookieFlow
    
    subgraph QrcodeFlow [二维码登录流程]
        Q1[打开登录页面]
        Q2[查找二维码元素]
        Q3{找到二维码?}
        Q4[显示二维码]
        Q5[用户扫码]
        Q6[循环检测登录状态]
        Q7{登录成功?}
        Q8[保存Cookie]
        Q9[超时退出]
        
        Q1 --> Q2
        Q2 --> Q3
        Q3 -->|否| Q1
        Q3 -->|是| Q4
        Q4 --> Q5
        Q5 --> Q6
        Q6 --> Q7
        Q7 -->|否| Q6
        Q7 -->|是| Q8
        Q6 --> Q9
    end
    
    subgraph PhoneFlow [手机登录流程]
        P1[打开登录页面]
        P2[点击手机登录]
        P3[输入手机号]
        P4[点击发送验证码]
        P5[等待用户输入验证码]
        P6[输入验证码]
        P7[勾选隐私协议]
        P8[点击登录]
        P9[检测登录状态]
        P10{登录成功?}
        P11[保存Cookie]
        P12[超时退出]
        
        P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P9 --> P10
        P10 -->|否| P9
        P10 -->|是| P11
        P9 --> P12
    end
    
    subgraph CookieFlow [Cookie登录流程]
        C1[加载预设Cookie]
        C2[访问首页]
        C3[检测登录状态]
        C4{登录有效?}
        C5[登录成功]
        C6[Cookie失效]
        
        C1 --> C2 --> C3 --> C4
        C4 -->|是| C5
        C4 -->|否| C6
    end
    
    Q8 --> End([登录完成])
    P11 --> End
    C5 --> End
    C6 --> End
    Q9 --> End
    P12 --> End
```

### 图表解释

#### 1. 整体概述
该图描述了 MediaCrawler 支持的三类登录认证机制：二维码登录、手机号验证码登录和 Cookie 复用登录。三种方式通过条件分支互斥选择，最终均收敛到统一的结束节点。二维码和手机登录依赖浏览器自动化模拟用户交互，Cookie 登录则直接复用已有会话，属于无头（headless）模式。

#### 2. 关键元素说明
- **二维码元素**：登录页面中用于承载二维码图像的 DOM 节点，通常通过 CSS 选择器或 XPath 定位。
- **循环检测登录状态**：基于轮询（polling）机制，定时访问用户主页或特定接口，检查响应中是否包含登录标识。
- **验证码**：通过短信网关下发的一次性密码，用于验证手机号所有权。
- **隐私协议勾选**：平台合规要求，需在提交登录前模拟点击同意按钮。
- **预设 Cookie**：上次登录成功后持久化存储的会话凭证，通常保存为 JSON 文件。

#### 3. 关键流程/关系说明
二维码流程的核心是"展示-扫码-轮询"：打开页面 → 定位二维码 → 展示给用户 → 循环检测状态直至成功或超时。手机流程是"表单填写-提交-验证"：依次完成页面切换、手机号输入、验证码获取与填写、协议勾选、登录提交，最后检测状态。Cookie 流程最为简洁：加载本地 Cookie → 访问首页 → 验证有效性，有效则直接成功，失效则退出。三种方式的出口均汇入结束节点，保证后续流程的一致性。

#### 4. 关键技术解释
- **浏览器自动化**：二维码和手机登录均依赖 Playwright/Selenium 操作真实浏览器，处理 JavaScript 渲染和事件触发，相比纯 HTTP 请求更能绕过基于前端行为的反爬检测。
- **轮询检测**：通过 setInterval 或递归 setTimeout 实现，通常配合最大等待时间（如 60 秒）和退避策略，避免无限阻塞。
- **Cookie 持久化**：利用浏览器 context 的 cookie 导出功能，将 sessionid、token 等关键凭证序列化到本地，下次启动时注入新上下文，实现会话复用。
- **超时处理**：二维码和手机流程均设置超时退出机制，防止用户未操作时流程永久挂起，属于防御性编程。

#### 5. 设计意图
提供三种登录方式的设计意图是覆盖不同的使用场景和自动化程度。二维码登录适合人工辅助的半自动场景，手机登录适合完全自动化的部署环境，Cookie 登录则最大化效率，避免重复认证。三种方式共享"保存 Cookie"和"结束"节点，保证登录模块的接口统一性。超时和循环检测的设计，兼顾了用户体验和系统稳定性，防止因外部依赖（用户操作、短信延迟）导致流程僵死。

## 4. 数据存储业务流程

```mermaid
graph TB
    Start([数据到达]) --> CheckType{数据类型}
    
    CheckType -->|帖子| NoteProcess
    CheckType -->|评论| CommentProcess
    CheckType -->|创作者| CreatorProcess
    CheckType -->|媒体| MediaProcess
    
    subgraph NoteProcess [帖子存储流程]
        N1[提取帖子字段]
        N2{存储方式}
        N3[写入CSV]
        N4[写入JSON/JSONL]
        N5[检查数据库是否存在]
        N6{存在?}
        N7[UPDATE更新]
        N8[INSERT插入]
        N9[写入MongoDB]
        N10[写入Excel]
        
        N1 --> N2
        N2 -->|CSV| N3
        N2 -->|JSON| N4
        N2 -->|DB| N5
        N5 --> N6
        N6 -->|是| N7
        N6 -->|否| N8
        N2 -->|MongoDB| N9
        N2 -->|Excel| N10
    end
    
    subgraph CommentProcess [评论存储流程]
        C1[提取评论字段]
        C2{存储方式}
        C3[写入CSV]
        C4[写入JSONL]
        C5[检查数据库是否存在]
        C6{存在?}
        C7[UPDATE更新]
        C8[INSERT插入]
        C9[写入MongoDB]
        
        C1 --> C2
        C2 -->|CSV| C3
        C2 -->|JSONL| C4
        C2 -->|DB| C5
        C5 --> C6
        C6 -->|是| C7
        C6 -->|否| C8
        C2 -->|MongoDB| C9
    end
    
    subgraph CreatorProcess [创作者存储流程]
        R1[提取创作者字段]
        R2{存储方式}
        R3[写入DB/MongoDB]
        
        R1 --> R2
        R2 -->|DB/MongoDB| R3
    end
    
    subgraph MediaProcess [媒体存储流程]
        M1[下载媒体文件]
        M2[生成文件名]
        M3[保存到本地]
        M4[记录媒体URL]
        
        M1 --> M2 --> M3 --> M4
    end
    
    N3 --> End([存储完成])
    N4 --> End
    N7 --> End
    N8 --> End
    N9 --> End
    N10 --> End
    C3 --> End
    C4 --> End
    C7 --> End
    C8 --> End
    C9 --> End
    R3 --> End
    M4 --> End
```

### 图表解释

#### 1. 整体概述
该图描述了爬虫采集数据的持久化流程，按数据类型分为四个独立子流程：帖子、评论、创作者和媒体。每种类型根据配置选择不同的存储后端，包括 CSV、JSON/JSONL、关系型数据库、MongoDB 和 Excel。关系型数据库分支额外支持 UPSERT 语义（存在则更新，不存在则插入），媒体数据则直接落盘为本地文件。

#### 2. 关键元素说明
- **字段提取**：将原始响应 JSON 映射为结构化字段，通常通过 Pydantic 模型或 dataclass 进行校验和转换。
- **CSV/Excel**：面向表格型数据的文件格式，适合数据分析人员直接查看，但不支持嵌套结构。
- **JSON/JSONL**：JSON Lines 格式每行一个独立 JSON 对象，兼顾结构化和大规模追加写入的性能。
- **关系型数据库**：通常指 SQLite 或 MySQL，通过 SQLAlchemy 等 ORM 操作，支持事务和去重。
- **MongoDB**：文档型数据库，适合存储 schema 灵活的半结构化数据，如帖子的嵌套标签和位置信息。

#### 3. 关键流程/关系说明
数据到达后首先按类型路由到对应的子流程。帖子和评论的子流程结构相似：先提取字段，再根据存储方式分支。选择 DB 时，先查询记录是否存在，存在则执行 UPDATE，不存在则执行 INSERT，实现幂等写入。创作者的存储方式较为精简，仅支持 DB 和 MongoDB。媒体流程独立为线性顺序：下载二进制内容 → 生成唯一文件名 → 写入磁盘 → 记录元数据。所有子流程最终汇入结束节点。

#### 4. 关键技术解释
- **UPSERT 机制**：通过先 SELECT 后 UPDATE/INSERT 的两步操作模拟 UPSERT，避免主键冲突。在支持的数据库中也可使用 INSERT ... ON CONFLICT 或 REPLACE INTO 等原生语法优化。
- **JSONL 格式**：相比标准 JSON 数组，JSONL 支持流式写入和逐行读取，无需一次性加载整个文件到内存，适合大规模数据场景。
- **文件命名策略**：媒体文件通常采用哈希（如 MD5 或 SHA256）或组合键（post_id + index）命名，避免文件名冲突，同时实现内容去重。
- **存储抽象层**：通过统一接口封装不同后端的具体实现，使上层业务代码无需关心底层是文件还是数据库，符合依赖倒置原则。

#### 5. 设计意图
该存储模块的设计目标是"多后端适配和幂等写入"。提供多种存储方式，满足不同下游系统的对接需求：分析师偏好 Excel/CSV，工程师偏好数据库，日志系统偏好 JSONL。UPSERT 逻辑保证重复运行爬虫不会导致数据重复，支持增量更新。媒体文件独立处理，是因为二进制数据不适合存入关系型数据库的文本字段，且文件系统在大文件读写上更具优势。四种子流程共享结束节点，保持了存储接口的一致性。

## 5. 反爬对抗业务流程

```mermaid
graph TB
    Start([发送请求]) --> CheckProxy{代理有效?}
    
    CheckProxy -->|否| RefreshProxy[刷新代理]
    RefreshProxy --> CheckProxy
    CheckProxy -->|是| GenSign[生成签名]
    
    GenSign --> SendReq[发送HTTP请求]
    SendReq --> CheckStatus{状态码}
    
    CheckStatus -->|200| CheckCode{业务code}
    CheckStatus -->|461/471| Captcha[触发验证码]
    CheckStatus -->|429| RateLimit[频率限制]
    CheckStatus -->|5xx| ServerError[服务器错误]
    
    CheckCode -->|success| Success[请求成功]
    CheckCode -->|300012| IPBlocked[IP被封]
    CheckCode -->|-510000| NotFound[帖子不存在]
    CheckCode -->|其他| OtherError[其他错误]
    
    Captcha --> HandleCaptcha{处理方式}
    HandleCaptcha -->|暂停| Pause[暂停爬取]
    HandleCaptcha -->|人工| Manual[等待人工处理]
    
    RateLimit --> IncreaseSleep[增加睡眠间隔]
    IncreaseSleep --> Retry1{重试<3?}
    Retry1 -->|是| SendReq
    Retry1 -->|否| Error1[放弃请求]
    
    ServerError --> Retry2{重试<3?}
    Retry2 -->|是| SendReq
    Retry2 -->|否| Error2[放弃请求]
    
    IPBlocked --> SwitchProxy[切换代理]
    SwitchProxy --> Retry3{重试<3?}
    Retry3 -->|是| SendReq
    Retry3 -->|否| Error3[放弃请求]
    
    NotFound --> Skip[跳过该帖子]
    OtherError --> Retry4{重试<3?}
    Retry4 -->|是| SendReq
    Retry4 -->|否| Error4[放弃请求]
    
    Success --> ParseData[解析数据]
    ParseData --> ReturnData[返回数据]
    
    Pause --> End1([结束])
    Manual --> End1
    Error1 --> End1
    Error2 --> End1
    Error3 --> End1
    Error4 --> End1
    Skip --> End1
    ReturnData --> End1
```

### 图表解释

#### 1. 整体概述
该图描述了爬虫在请求发送阶段面对各类反爬机制时的应对策略。流程以代理检查和请求签名为前置步骤，然后根据 HTTP 状态码和业务码进行多级分支判断，分别处理验证码、频率限制、服务器错误、IP 封禁、资源不存在和其他异常。每类异常配备特定的恢复策略，包括重试、等待、切换代理和跳过，最终收敛到成功返回或结束。

#### 2. 关键元素说明
- **代理有效性检查**：验证当前代理是否可用，通常通过访问检测地址或检查代理池状态实现。
- **HTTP 状态码**：461/471 通常表示行为验证或验证码触发；429 表示请求频率过高；5xx 表示服务端异常。
- **业务 code**：平台自定义的错误码，如 300012 表示 IP 被封，-510000 表示帖子不存在，success 表示业务逻辑成功。
- **睡眠间隔**：请求间的延时，频率限制时会动态增加，通常采用指数退避策略。
- **切换代理**：从代理池中移除当前失效代理，重新获取一个新的 IP 地址。

#### 3. 关键流程/关系说明
主干流程为：检查代理 → 生成签名 → 发送请求 → 判断状态码。状态码 200 时进一步判断业务码；非 200 时直接进入对应处理分支。验证码分支提供暂停和人工处理两种策略；频率限制分支增加睡眠后重试；服务器错误直接重试；IP 封禁切换代理后重试；帖子不存在直接跳过；其他错误重试。所有重试分支均限制最多 3 次，超过则放弃。成功分支解析数据后返回。

#### 4. 关键技术解释
- **状态码与业务码分层**：HTTP 状态码反映传输层结果，业务码反映应用层逻辑，两者结合才能准确判断请求的真实状态。例如 200 + 300012 表示请求到达服务器但 IP 已被封禁。
- **指数退避**：频率限制时睡眠间隔按指数增长（如 1s, 2s, 4s），避免固定间隔仍被检测，同时减少无效请求。
- **代理切换与池化**：IP 被封时从代理池轮换，结合代理的匿名性（高匿/透明）和地理位置分布，降低单一 IP 的行为特征集中度。
- **验证码处理**：461/471 通常对应滑块、点选或旋转验证码，暂停和人工处理是成本与成功率的权衡，自动打码需集成第三方识别服务。

#### 5. 设计意图
该流程的设计核心是"分层防御和优雅降级"。将代理检查前置，避免无效请求浪费签名计算资源。按状态码和业务码分层处理，使每类异常都有针对性的恢复策略，而非统一重试。重试次数上限防止无限循环，跳过机制保证单点失败不阻塞整体任务。验证码分支提供人工介入入口，在全自动和可靠性之间保留弹性。整体结构呈扇形发散后收敛，保证无论经历何种异常，流程都能到达确定性的结束状态。

## 6. WebUI控制业务流程

```mermaid
graph TB
    Start([用户访问WebUI]) --> LoadPage[加载配置页面]
    LoadPage --> FillForm[填写配置表单]
    FillForm --> Validate{参数校验}
    
    Validate -->|无效| ShowError[显示错误提示]
    ShowError --> FillForm
    Validate -->|有效| ClickStart[点击启动按钮]
    
    ClickStart --> SendAPI[POST /api/crawler/start]
    SendAPI --> BuildCmd[后端构建命令]
    BuildCmd --> SpawnProcess[启动子进程]
    SpawnProcess --> ConnectWS[建立WebSocket连接]
    
    ConnectWS --> ShowLog[实时显示日志]
    ShowLog --> CheckStatus{用户操作}
    
    CheckStatus -->|停止| ClickStop[点击停止按钮]
    ClickStop --> SendStop[POST /api/crawler/stop]
    SendStop --> KillProcess[发送SIGTERM]
    KillProcess --> WaitExit{15秒内退出?}
    WaitExit -->|否| ForceKill[强制kill]
    WaitExit -->|是| ShowStopped[显示已停止]
    ForceKill --> ShowStopped
    
    CheckStatus -->|查看数据| ClickData[点击数据预览]
    ClickData --> FetchData[GET /api/data/notes]
    FetchData --> RenderTable[渲染数据表格]
    RenderTable --> CheckStatus
    
    CheckStatus -->|下载| ClickDownload[点击下载]
    ClickDownload --> GenerateFile[生成文件]
    GenerateFile --> Download[浏览器下载]
    Download --> CheckStatus
    
    CheckStatus -->|退出| ClosePage[关闭页面]
    ShowStopped --> ClosePage
    ClosePage --> End([结束])
```

### 图表解释

#### 1. 整体概述
该图描述了通过 WebUI 控制爬虫运行的完整交互流程。用户在前端页面配置参数并启动任务，后端通过 API 接收指令、构建命令、启动子进程，并通过 WebSocket 向前端推送实时日志。运行期间用户可执行停止、查看数据和下载三种操作，系统提供优雅停止和强制终止两种结束方式。整个流程围绕"配置-启动-监控-操作-结束"五个阶段展开。

#### 2. 关键元素说明
- **配置表单**：前端界面中的输入组件集合，包括平台选择、关键词、并发数、存储方式等参数，通常基于 React/Vue 表单库实现。
- **POST /api/crawler/start**：后端 REST API 端点，接收前端提交的 JSON 配置，负责参数校验和任务调度。
- **子进程**：后端通过 child_process（Node.js）或 subprocess（Python）启动的独立爬虫进程，与 Web 服务解耦，避免阻塞主线程。
- **WebSocket**：全双工通信通道，用于后端向前端推送实时日志流，替代轮询以降低延迟和资源消耗。
- **SIGTERM**：Unix 信号，请求进程优雅退出，允许执行清理操作；SIGKILL 则强制终止，无法拦截。

#### 3. 关键流程/关系说明
用户访问后加载配置页，填写表单并通过校验后点击启动。前端发送 POST 请求，后端构建命令行参数并 spawn 子进程，同时建立 WebSocket 连接推送日志。此后流程进入用户操作循环：停止操作发送 SIGTERM，15 秒内未退出则强制 kill；查看数据通过 GET API 拉取并渲染表格；下载操作生成文件后触发浏览器下载；退出操作关闭页面。停止后的状态也会导向关闭页面，最终结束。

#### 4. 关键技术解释
- **前后端分离架构**：前端负责界面渲染和用户交互，后端负责业务逻辑和进程管理，通过 REST API 和 WebSocket 通信，符合现代 Web 应用的分层设计。
- **子进程管理**：爬虫作为独立进程运行，与 Web 服务生命周期隔离，即使爬虫崩溃也不会影响 WebUI 的可用性。进程间通过标准输出重定向或管道传递日志。
- **WebSocket 实时推送**：相比 HTTP 轮询，WebSocket 在建立连接后由服务端主动推送数据，减少了请求头和连接建立的开销，适合日志流等高频率场景。
- **优雅停止机制**：先发送 SIGTERM 给予进程清理资源的机会（如关闭数据库连接、保存状态），超时后再强制 kill，平衡了数据完整性和响应速度。

#### 5. 设计意图
WebUI 的设计目标是降低爬虫工具的使用门槛，使非技术人员也能通过图形界面操作。将爬虫进程与 Web 服务分离，保证了系统的稳定性和可扩展性，支持同时管理多个爬虫实例。WebSocket 实时日志提供了透明的执行反馈，增强用户信任感。操作循环的设计允许用户在任务运行期间随时干预，体现了交互系统的响应性。优雅停止和强制终止的分级策略，既保护了数据一致性，又避免僵尸进程长期占用资源。

## 7. 代理管理业务流程

```mermaid
graph TB
    Start([需要代理]) --> CheckPool{代理池初始化?}
    
    CheckPool -->|否| InitPool[初始化代理池]
    InitPool --> LoadProxy[从供应商加载代理]
    LoadProxy --> ValidateProxy{验证代理?}
    ValidateProxy -->|是| TestProxy[测试代理可用性]
    TestProxy --> Valid{可用?}
    Valid -->|是| AddPool[加入代理池]
    Valid -->|否| Discard[丢弃]
    ValidateProxy -->|否| AddPool
    
    CheckPool -->|是| GetProxy[获取代理]
    AddPool --> GetProxy
    
    GetProxy --> RandomSelect[随机选择]
    RandomSelect --> RemovePool[从池移除]
    RemovePool --> CheckExpired{验证过期?}
    
    CheckExpired -->|是| TestAgain[再次测试]
    TestAgain --> StillValid{仍可用?}
    StillValid -->|是| UseProxy[使用代理]
    StillValid -->|否| GetAnother[获取下一个]
    GetAnother --> GetProxy
    
    CheckExpired -->|否| UseProxy
    UseProxy --> SendRequest[发送请求]
    SendRequest --> CheckResult{请求结果}
    
    CheckResult -->|成功| ReturnResult[返回结果]
    CheckResult -->|IP被封| MarkExpired[标记过期]
    MarkExpired --> GetProxy
    CheckResult -->|代理失效| MarkExpired2[标记过期]
    MarkExpired2 --> GetProxy
    
    ReturnResult --> End([完成])
```

### 图表解释

#### 1. 整体概述
该图描述了代理池的完整生命周期管理，包括初始化加载、可用性验证、随机分配、过期检测和运行时回收。代理池采用懒加载策略，首次需要时才初始化，从供应商获取代理列表后经过测试筛选加入池中。使用时随机选取并临时移除，用完后根据请求结果决定放回或标记失效，形成闭环管理。

#### 2. 关键元素说明
- **代理供应商**：提供代理 IP 的第三方服务，通常通过 HTTP API 按量或按时计费，返回格式多为 JSON 列表。
- **代理池**：内存中的代理队列或集合，维护当前可用的代理列表，支持并发安全的存取操作。
- **可用性测试**：通过代理访问检测地址（如 httpbin.org/ip），验证连通性和匿名性，排除透明代理和已失效节点。
- **随机选择**：从池中随机抽取代理，避免按固定顺序使用导致的行为模式化。
- **过期标记**：将失效代理从池中移除或加入黑名单，防止后续请求重复使用该代理。

#### 3. 关键流程/关系说明
流程起点为"需要代理"，首次使用时初始化代理池：加载 → 可选验证 → 测试 → 可用则加入，不可用则丢弃。若跳过验证则直接加入。代理池就绪后进入获取循环：随机选择 → 从池移除 → 检查是否过期 → 过期则重测 → 仍可用则使用，否则重新获取。使用代理发送请求后，成功则返回结果；IP 被封或代理失效则标记过期并重新获取代理。成功路径到达结束，失败路径回到获取代理节点循环。

#### 4. 关键技术解释
- **懒加载（Lazy Initialization）**：代理池在首次需要时才创建，减少系统启动时间和资源占用，属于常见的性能优化策略。
- **并发安全**：代理池作为共享资源，在多线程环境下需要加锁或使用线程安全的数据结构（如 queue.Queue），防止竞态条件导致同一代理被重复分配。
- **代理匿名级别**：透明代理会暴露真实 IP，匿名代理隐藏真实 IP 但暴露代理身份，高匿代理两者均隐藏。测试阶段通常优先选择高匿代理。
- **连接池与代理的协同**：HTTP 客户端（如 requests.Session 或 aiohttp.ClientSession）维护连接池，切换代理时需重置连接或创建新会话，避免复用旧连接导致 IP 未切换。

#### 5. 设计意图
代理管理模块的设计核心是"动态维护和失效隔离"。懒加载避免无意义的资源消耗，测试筛选保证池中代理质量。随机选择分散请求来源，降低单一 IP 的请求密度。使用时从池移除（而非复制引用）防止并发冲突，用完后根据实际请求结果反馈更新状态，实现自适应的池维护。标记过期后重新获取的循环，保证即使代理大面积失效，流程也能持续尝试恢复，提升系统的容错能力。

## 8. 爬虫监控告警业务流程

```mermaid
graph TB
    Start([爬虫运行]) --> CollectMetrics[收集指标]
    
    CollectMetrics --> CheckCPU{CPU使用率}
    CheckCPU -->|>80%| AlertCPU[CPU告警]
    CheckCPU -->|正常| CheckMemory
    
    AlertCPU --> ScaleUp[扩容/降速]
    ScaleUp --> CollectMetrics
    
    CheckMemory{内存使用率}
    CheckMemory -->|>80%| AlertMemory[内存告警]
    CheckMemory -->|正常| CheckProxyStatus
    
    AlertMemory --> Restart[重启爬虫]
    Restart --> CollectMetrics
    
    CheckProxyStatus{代理可用率}
    CheckProxyStatus -->|<50%| AlertProxy[代理告警]
    CheckProxyStatus -->|正常| CheckErrorRate
    
    AlertProxy --> ReloadProxy[重新加载代理]
    ReloadProxy --> CollectMetrics
    
    CheckErrorRate{错误率}
    CheckErrorRate -->|>20%| AlertError[错误告警]
    CheckErrorRate -->|正常| CheckProgress
    
    AlertError --> AnalyzeError[分析错误类型]
    AnalyzeError --> AdjustStrategy[调整策略]
    AdjustStrategy --> CollectMetrics
    
    CheckProgress{爬取进度}
    CheckProgress -->|停滞| AlertStuck[卡死告警]
    CheckProgress -->|正常| CheckComplete
    
    AlertStuck --> Recover[自动恢复]
    Recover --> CollectMetrics
    
    CheckComplete{任务完成?}
    CheckComplete -->|否| CollectMetrics
    CheckComplete -->|是| SendNotify[发送完成通知]
    SendNotify --> GenerateReport[生成报告]
    GenerateReport --> End([结束])
```

### 图表解释

#### 1. 整体概述
该图描述了爬虫运行期间的监控告警机制，采用循环检测结构，周期性地采集系统指标并按优先级依次检查 CPU、内存、代理可用率、错误率和爬取进度。任一指标异常时触发对应的告警和恢复动作，所有恢复路径均回到指标采集节点，形成持续监控闭环。任务完成后发送通知并生成报告，流程结束。

#### 2. 关键元素说明
- **指标采集**：收集系统和业务层面的运行时数据，包括进程资源占用、请求成功率、代理池状态、已爬取数量等，通常通过 psutil 等库或应用内计数器实现。
- **CPU/内存阈值**：80% 作为资源紧张的警戒线，超过时可能影响系统稳定性或其他进程运行。
- **代理可用率**：可用代理数占总代理数的比例，低于 50% 意味着代理池质量严重下降，需要补充新代理。
- **错误率**：失败请求占总请求的比例，超过 20% 表明当前策略或环境存在系统性问题。
- **爬取进度停滞**：通过比较单位时间内的增量判断，若长时间无新数据产生，可能遭遇封禁或目标页面结构变更。

#### 3. 关键流程/关系说明
流程以循环为核心：采集指标 → 依次检查五项条件。CPU 超限触发扩容或降速；内存超限触发重启；代理可用率过低触发重载；错误率过高触发错误分析和策略调整；进度停滞触发自动恢复。所有异常处理完成后均回到采集节点，继续下一轮检测。若全部指标正常且任务未完成，同样回到采集节点。任务完成时跳出循环，发送通知并生成报告后结束。

#### 4. 关键技术解释
- **周期性采样**：通过定时器（如 setInterval 或后台线程）按固定频率（如每 30 秒）执行指标采集，平衡监控实时性和系统开销。
- **阈值告警**：基于经验值或历史数据设定静态阈值，简单有效但可能存在误报。进阶方案可采用动态基线或异常检测算法（如 3-sigma 原则）。
- **自动恢复策略**：卡死恢复通常包括重启浏览器上下文、清空 Cookie、切换用户代理或重置代理池，尝试消除导致停滞的状态污染。
- **错误分类分析**：将错误按类型（网络超时、反爬拦截、解析失败、服务端错误）统计，识别主导因素，指导策略调整方向，如增加睡眠间隔或更换解析规则。

#### 5. 设计意图
监控告警模块的设计目标是实现爬虫的"无人值守运行"。通过多维度指标检测，覆盖资源、网络、业务逻辑和进度四个层面的异常，确保问题被及时发现和处理。循环结构保证监控的持续性，任何异常处理后都能恢复检测，避免单点故障导致监控本身中断。分级处理策略（扩容、重启、重载、调整、恢复）针对不同根因提供针对性措施，而非一刀切的重启。任务完成后的通知和报告，满足运维和业务的闭环需求，使爬虫从启动到结束的全过程可观测、可干预、可复盘。
