# MediaCrawler 数据流E-R图 (Data Flow & E-R Diagram)

## 1. 系统数据流图 (DFD Level 0 - 上下文图)

```mermaid
graph TB
    subgraph 外部实体
        U[用户]
        XHS[小红书/抖音/快手等平台]
        PP[代理供应商]
    end

    subgraph MediaCrawler系统
        S[爬虫系统]
    end

    subgraph 数据存储
        DB[(数据库)]
        FS[文件系统]
        Cache[(缓存)]
    end

    U -->|配置参数/启动命令| S
    S -->|爬取请求| XHS
    XHS -->|返回数据| S
    S -->|获取代理IP| PP
    PP -->|返回代理| S
    S -->|存储数据| DB
    S -->|存储文件| FS
    S -->|读写缓存| Cache
    S -->|实时日志| U
```

## 2. 系统数据流图 (DFD Level 1)

```mermaid
graph TB
    subgraph 外部实体
        U[用户]
        XHS[自媒体平台]
        PP[代理供应商]
    end

    subgraph 处理过程
        P1[1.0 配置管理]
        P2[2.0 浏览器管理]
        P3[3.0 登录认证]
        P4[4.0 数据采集]
        P5[5.0 数据处理]
        P6[6.0 数据存储]
        P7[7.0 代理管理]
        P8[8.0 日志监控]
    end

    subgraph 数据存储
        D1[(配置数据)]
        D2[(Cookie/登录态)]
        D3[(帖子数据)]
        D4[(评论数据)]
        D5[(创作者数据)]
        D6[(代理IP池)]
        D7[(日志数据)]
        D8[(缓存数据)]
        F1[CSV/JSON/Excel文件]
    end

    U -->|配置参数| P1
    P1 -->|读取/写入| D1

    P1 -->|启动命令| P2
    P2 -->|加载/保存| D2
    P2 -->|浏览器操作| XHS
    XHS -->|页面内容| P2

    P2 -->|登录请求| P3
    P3 -->|认证信息| XHS
    XHS -->|登录结果| P3
    P3 -->|保存Cookie| D2

    P3 -->|开始爬取| P4
    P4 -->|请求签名| P5
    P5 -->|签名头| P4
    P4 -->|HTTP请求| XHS
    XHS -->|JSON数据| P4

    P4 -->|原始数据| P5
    P5 -->|清洗/转换| P6
    P6 -->|写入| D3
    P6 -->|写入| D4
    P6 -->|写入| D5
    P6 -->|写入| F1

    P4 -->|请求代理| P7
    P7 -->|获取代理| PP
    PP -->|代理IP| P7
    P7 -->|更新| D6
    P7 -->|返回代理| P4

    P4 -->|读写| D8
    P8 -->|读取| D7
    P8 -->|实时日志| U
```

## 3. 数据流详细图 - 搜索爬取流程

```mermaid
graph LR
    subgraph 输入
        I1[关键词: "Python"]
        I2[页码: 1,2,3...]
        I3[最大数量: 100]
    end

    subgraph 处理
        P1[构建搜索请求]
        P2[生成签名头]
        P3[发送HTTP请求]
        P4[解析响应JSON]
        P5[提取帖子ID列表]
        P6[并发获取帖子详情]
        P7[获取评论]
        P8[数据清洗]
    end

    subgraph 输出
        O1[帖子数据]
        O2[评论数据]
        O3[媒体URL]
    end

    I1 --> P1
    I2 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 --> P8
    P8 --> O1
    P8 --> O2
    P6 --> O3
```

## 4. E-R图 - 数据库实体关系

```mermaid
erDiagram
    XHS_NOTE ||--o{ XHS_NOTE_COMMENT : has
    XHS_NOTE }o--|| XHS_CREATOR : created_by
    XHS_NOTE_COMMENT ||--o{ XHS_NOTE_COMMENT : replies_to
    BILIBILI_VIDEO ||--o{ BILIBILI_VIDEO_COMMENT : has
    DOUYIN_VIDEO ||--o{ DOUYIN_VIDEO_COMMENT : has

    XHS_NOTE {
        int id PK
        string note_id UK
        string user_id FK
        string nickname
        string avatar
        string ip_location
        string type
        string title
        string desc
        string video_url
        datetime time
        datetime last_update_time
        int liked_count
        int collected_count
        int comment_count
        int share_count
        string image_list
        string tag_list
        string note_url
        string source_keyword
        string xsec_token
        bigint add_ts
        bigint last_modify_ts
    }

    XHS_NOTE_COMMENT {
        int id PK
        string comment_id UK
        string note_id FK
        string user_id
        string nickname
        string avatar
        string content
        datetime create_time
        int liked_count
        string parent_comment_id
        int sub_comment_count
        bigint add_ts
        bigint last_modify_ts
    }

    XHS_CREATOR {
        int id PK
        string user_id UK
        string nickname
        string avatar
        string desc
        int follow_count
        int fans_count
        int interaction_count
        bigint add_ts
        bigint last_modify_ts
    }

    BILIBILI_VIDEO {
        int id PK
        bigint video_id UK
        string video_url
        bigint user_id
        string nickname
        string avatar
        int liked_count
        string video_type
        string title
        string desc
        bigint create_time
        string video_play_count
        string video_favorite_count
        string video_share_count
        string video_coin_count
        string video_danmaku
        string video_comment
        string video_cover_url
        string source_keyword
    }

    BILIBILI_VIDEO_COMMENT {
        int id PK
        string user_id
        string nickname
        string content
        bigint comment_id
        bigint video_id FK
        bigint create_time
        string sub_comment_count
        string parent_comment_id
        string like_count
    }

    DOUYIN_VIDEO {
        int id PK
        string aweme_id UK
        string video_url
        string user_id
        string nickname
        string avatar
        string desc
        bigint create_time
        int liked_count
        int comment_count
        int share_count
        string cover_url
        string source_keyword
    }

    DOUYIN_VIDEO_COMMENT {
        int id PK
        string comment_id
        string aweme_id FK
        string user_id
        string nickname
        string content
        bigint create_time
        int liked_count
        string parent_comment_id
    }
```

## 5. E-R图 - 代理与缓存实体

```mermaid
erDiagram
    PROXY_IP_POOL ||--o{ PROXY_IP : contains
    PROXY_IP }o--|| PROXY_PROVIDER : provided_by

    PROXY_IP_POOL {
        int id PK
        string pool_name
        int pool_count
        bool enable_validate
        datetime created_at
    }

    PROXY_IP {
        int id PK
        int pool_id FK
        string ip
        int port
        string user
        string password
        string protocol
        datetime expired_time
        bool is_valid
        int used_count
        datetime last_used
    }

    PROXY_PROVIDER {
        int id PK
        string provider_name UK
        string api_url
        string api_key
        datetime created_at
    }

    CACHE_ENTRY {
        string key PK
        string value
        datetime expired_at
        string cache_type
    }

    LOGIN_STATE {
        int id PK
        string platform
        string login_type
        string cookie_str
        string web_session
        bool is_valid
        datetime expired_at
        datetime created_at
    }
```

## 6. 数据字典 - 核心数据项

```mermaid
graph TB
    subgraph 帖子数据项
        D1["note_id: 帖子唯一标识<br/>类型: string<br/>示例: 65a1b2c3d4e5f6"]
        D2["title: 帖子标题<br/>类型: string<br/>示例: 'Python学习笔记'"]
        D3["desc: 帖子描述<br/>类型: string<br/>示例: '分享Python入门经验'"]
        D4["liked_count: 点赞数<br/>类型: int<br/>示例: 1234"]
        D5["user_id: 作者ID<br/>类型: string<br/>示例: '5f8a9b2c3d4e'"]
    end

    subgraph 评论数据项
        C1["comment_id: 评论唯一标识<br/>类型: string"]
        C2["content: 评论内容<br/>类型: string<br/>示例: '感谢分享！'"]
        C3["parent_comment_id: 父评论ID<br/>类型: string<br/>用于二级评论"]
        C4["liked_count: 点赞数<br/>类型: int"]
    end

    subgraph 签名数据项
        S1["x-s: 主签名<br/>类型: string<br/>生成: XOR+Base64"]
        S2["x-t: 时间戳<br/>类型: string<br/>生成: 当前时间戳"]
        S3["x-s-common: 通用签名<br/>类型: string<br/>包含设备信息"]
        S4["x-b3-traceid: 追踪ID<br/>类型: string<br/>用于链路追踪"]
    end

    subgraph 代理数据项
        P1["ip: 代理IP地址<br/>类型: string<br/>示例: '1.2.3.4'"]
        P2["port: 代理端口<br/>类型: int<br/>示例: 8080"]
        P3["expired_time: 过期时间<br/>类型: timestamp<br/>用于自动刷新"]
    end
```

## 7. 数据转换流程图

```mermaid
graph LR
    subgraph 原始数据
        R1[平台JSON响应]
        R2[HTML页面内容]
        R3[媒体文件二进制]
    end

    subgraph 处理层
        P1[JSON解析]
        P2[HTML提取]
        P3[签名验证]
        P4[数据清洗]
        P5[字段映射]
    end

    subgraph 标准数据模型
        M1[NoteModel]
        M2[CommentModel]
        M3[CreatorModel]
        M4[MediaModel]
    end

    subgraph 存储格式
        S1[CSV行]
        S2[JSON对象]
        S3[SQL记录]
        S4[MongoDB文档]
        S5[Excel行]
    end

    R1 --> P1
    R2 --> P2
    R1 --> P3
    P1 --> P4
    P2 --> P4
    P4 --> P5
    P5 --> M1
    P5 --> M2
    P5 --> M3
    R3 --> M4
    M1 --> S1
    M1 --> S2
    M1 --> S3
    M1 --> S4
    M1 --> S5
    M2 --> S1
    M2 --> S3
    M2 --> S4
    M3 --> S3
    M3 --> S4
    M4 --> S4
```

## 8. 数据状态转换图

```mermaid
stateDiagram-v2
    [*] --> 待爬取: 用户启动
    待爬取 --> 登录中: 检查登录态
    登录中 --> 登录成功: 登录完成
    登录中 --> 登录失败: 超时/失败
    登录失败 --> [*]: 退出程序
    登录成功 --> 爬取中: 开始爬取
    爬取中 --> 获取列表: 搜索关键词
    获取列表 --> 获取详情: 提取帖子ID
    获取详情 --> 获取评论: 启用评论
    获取评论 --> 存储数据: 获取完成
    获取详情 --> 存储数据: 跳过评论
    存储数据 --> 获取详情: 下一帖子
    存储数据 --> 获取列表: 下一页
    获取列表 --> 爬取完成: 无更多数据
    爬取中 --> 暂停: 用户停止
    暂停 --> 爬取中: 用户恢复
    暂停 --> [*]: 用户退出
    爬取完成 --> [*]: 正常结束
```
