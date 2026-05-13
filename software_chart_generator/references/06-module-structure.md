# MediaCrawler 模块结构图 (Module Structure Diagram)

## 1. 整体模块结构图

```mermaid
graph TB
    subgraph 入口模块
        M1[main.py<br/>CLI入口]
        M2[api/main.py<br/>WebUI入口]
    end

    subgraph 抽象基类模块
        B1[base/base_crawler.py<br/>AbstractCrawler]
        B2[base/base_crawler.py<br/>AbstractLogin]
        B3[base/base_crawler.py<br/>AbstractApiClient]
        B4[base/base_crawler.py<br/>AbstractStore]
    end

    subgraph 平台实现模块
        P1[media_platform/xhs/]
        P2[media_platform/douyin/]
        P3[media_platform/kuaishou/]
        P4[media_platform/bilibili/]
        P5[media_platform/weibo/]
        P6[media_platform/tieba/]
        P7[media_platform/zhihu/]
    end

    subgraph 基础设施模块
        I1[proxy/]
        I2[cache/]
        I3[store/]
        I4[database/]
        I5[tools/]
        I6[config/]
    end

    subgraph API模块
        A1[api/routers/]
        A2[api/services/]
        A3[api/schemas/]
    end

    M1 --> B1
    M2 --> A1
    A1 --> A2
    A2 --> M1

    B1 --> P1
    B1 --> P2
    B1 --> P3
    B1 --> P4
    B1 --> P5
    B1 --> P6
    B1 --> P7

    P1 --> I1
    P1 --> I2
    P1 --> I3
    P1 --> I4
    P1 --> I5
    P1 --> I6

    I3 --> I4
    I5 --> I1
```

## 2. 小红书平台模块详细结构

```mermaid
graph TB
    subgraph XiaoHongShu模块
        X1[core.py<br/>XiaoHongShuCrawler]
        X2[client.py<br/>XiaoHongShuClient]
        X3[login.py<br/>XiaoHongShuLogin]
        X4[field.py<br/>枚举定义]
        X5[exception.py<br/>自定义异常]
        X6[extractor.py<br/>数据提取]
        X7[help.py<br/>辅助函数]
        X8[playwright_sign.py<br/>签名生成]
        X9[xhs_sign.py<br/>签名算法核心]
    end

    subgraph 依赖关系
        X1 --> X2
        X1 --> X3
        X1 --> X6
        X2 --> X8
        X2 --> X9
        X3 --> X4
        X6 --> X5
        X8 --> X9
    end

    subgraph 外部依赖
        X1 --> Browser[Playwright浏览器]
        X2 --> Httpx[httpx客户端]
        X2 --> Proxy[代理池]
        X3 --> Stealth[stealth.min.js]
        X8 --> Xhshow[xhshow库]
    end
```

## 3. 存储模块结构图

```mermaid
graph TB
    subgraph 存储抽象层
        S0[base/base_crawler.py<br/>AbstractStore]
    end

    subgraph 平台存储工厂
        F1[store/xhs/<br/>XhsStoreFactory]
        F2[store/douyin/<br/>DyStoreFactory]
        F3[store/bilibili/<br/>BiliStoreFactory]
    end

    subgraph 存储实现层
        I1[_store_impl.py<br/>XhsCsvStoreImplement]
        I2[_store_impl.py<br/>XhsJsonStoreImplement]
        I3[_store_impl.py<br/>XhsDbStoreImplement]
        I4[_store_impl.py<br/>XhsMongoStoreImplement]
        I5[_store_impl.py<br/>XhsExcelStoreImplement]
    end

    subgraph 媒体存储
        M1[xhs_store_media.py<br/>媒体文件下载]
    end

    S0 --> F1
    S0 --> F2
    S0 --> F3

    F1 --> I1
    F1 --> I2
    F1 --> I3
    F1 --> I4
    F1 --> I5
    F1 --> M1

    I3 --> DB[(SQLAlchemy ORM)]
    I4 --> Mongo[(MongoDB)]
    I5 --> Excel[(OpenPyXL)]
    M1 --> FS[文件系统]
```

## 4. 代理模块结构图

```mermaid
graph TB
    subgraph 代理抽象层
        A1[proxy/base_proxy.py<br/>ProxyProvider]
    end

    subgraph 代理池核心
        P1[proxy/proxy_ip_pool.py<br/>ProxyIpPool]
        P2[proxy/proxy_mixin.py<br/>ProxyRefreshMixin]
        P3[proxy/types.py<br/>IpInfoModel]
    end

    subgraph 代理供应商实现
        S1[proxy/providers/kuaidl_proxy.py<br/>快代理]
        S2[proxy/providers/wandou_proxy.py<br/>豌豆HTTP]
        S3[proxy/providers/jishu_proxy.py<br/>极速代理]
        S4[proxy/providers/...<br/>其他供应商]
    end

    subgraph 使用方
        U1[media_platform/xhs/client.py<br/>XiaoHongShuClient]
        U2[media_platform/douyin/client.py<br/>DouYinClient]
    end

    A1 --> S1
    A1 --> S2
    A1 --> S3
    A1 --> S4

    S1 --> P1
    S2 --> P1
    S3 --> P1
    S4 --> P1

    P1 --> P2
    P2 --> U1
    P2 --> U2

    U1 --> P3
    U2 --> P3
```

## 5. 缓存模块结构图

```mermaid
graph TB
    subgraph 缓存抽象层
        C0[cache/abs_cache.py<br/>AbstractCache]
    end

    subgraph 缓存工厂
        F1[cache/cache_factory.py<br/>CacheFactory]
    end

    subgraph 缓存实现
        I1[cache/local_cache.py<br/>ExpiringLocalCache]
        I2[cache/redis_cache.py<br/>RedisCache]
    end

    subgraph 使用场景
        U1[登录态缓存]
        U2[签名结果缓存]
        U3[代理状态缓存]
    end

    C0 --> I1
    C0 --> I2

    F1 --> I1
    F1 --> I2

    I1 --> U1
    I1 --> U2
    I2 --> U3

    I2 --> Redis[(Redis服务器)]
```

## 6. 数据库模块结构图

```mermaid
graph TB
    subgraph ORM模型层
        M1[database/models.py<br/>XHS_NOTE]
        M2[database/models.py<br/>XHS_NOTE_COMMENT]
        M3[database/models.py<br/>XHS_CREATOR]
        M4[database/models.py<br/>BILIBILI_VIDEO]
        M5[database/models.py<br/>BILIBILI_VIDEO_COMMENT]
        M6[database/models.py<br/>DOUYIN_VIDEO]
        M7[database/models.py<br/>DOUYIN_VIDEO_COMMENT]
    end

    subgraph 会话管理
        S1[database/db_session.py<br/>async_db_session]
        S2[database/db.py<br/>DBManager]
    end

    subgraph 数据库后端
        D1[SQLite]
        D2[MySQL]
        D3[PostgreSQL]
    end

    subgraph MongoDB层
        MG1[database/mongodb_store_base.py<br/>MongoDBStoreBase]
        MG2[store/xhs/xhs_store_media.py<br/>媒体存储]
    end

    M1 --> S1
    M2 --> S1
    M3 --> S1
    M4 --> S1
    M5 --> S1
    M6 --> S1
    M7 --> S1

    S1 --> S2
    S2 --> D1
    S2 --> D2
    S2 --> D3

    MG1 --> MongoDB[(MongoDB)]
    MG2 --> MongoDB
```

## 7. 工具模块结构图

```mermaid
graph TB
    subgraph 浏览器工具
        B1[tools/cdp_browser.py<br/>CDPBrowserManager]
        B2[tools/browser_launcher.py<br/>BrowserLauncher]
    end

    subgraph 文件工具
        F1[tools/async_file_writer.py<br/>AsyncFileWriter]
        F2[tools/csv_writer.py<br/>CSVWriter]
        F3[tools/json_writer.py<br/>JSONWriter]
    end

    subgraph 网络工具
        N1[tools/utils.py<br/>format_proxy_info]
        N2[tools/utils.py<br/>convert_cookies]
    end

    subgraph 数据处理工具
        D1[tools/word_cloud.py<br/>生成词云图]
        D2[tools/slider.py<br/>滑块验证码]
    end

    B1 --> B2
    B2 --> Chrome[Chrome浏览器]

    F1 --> F2
    F1 --> F3
    F2 --> FS1[CSV文件]
    F3 --> FS2[JSON/JSONL文件]

    N1 --> Proxy[代理IP]
    N2 --> Cookie[Cookie数据]

    D1 --> WordCloud[词云图片]
    D2 --> Page[Playwright页面]
```

## 8. API模块结构图

```mermaid
graph TB
    subgraph FastAPI应用
        A1[api/main.py<br/>FastAPI实例]
    end

    subgraph 路由层
        R1[api/routers/crawler.py<br/>爬虫控制路由]
        R2[api/routers/data.py<br/>数据查询路由]
        R3[api/routers/config.py<br/>配置管理路由]
    end

    subgraph 服务层
        S1[api/services/crawler_manager.py<br/>CrawlerManager]
        S2[api/services/data_service.py<br/>DataService]
    end

    subgraph 数据模型
        M1[api/schemas/crawler.py<br/>CrawlerConfig]
        M2[api/schemas/data.py<br/>NoteResponse]
        M3[api/schemas/log.py<br/>LogEntry]
    end

    subgraph WebSocket
        W1[api/routers/ws.py<br/>日志推送]
    end

    A1 --> R1
    A1 --> R2
    A1 --> R3
    A1 --> W1

    R1 --> S1
    R2 --> S2
    W1 --> S1

    S1 --> M1
    S2 --> M2
    S1 --> M3

    S1 --> Process[子进程]
    S2 --> DB[(数据库)]
    W1 --> Client[Web客户端]
```

## 9. 配置模块结构图

```mermaid
graph TB
    subgraph 配置来源
        S1[.env文件]
        S2[环境变量]
        S3[命令行参数]
    end

    subgraph 配置加载
        L1[config/base_config.py<br/>BaseConfig]
        L2[config/__init__.py<br/>配置导出]
    end

    subgraph 平台配置
        P1[config/xhs_config.py<br/>小红书配置]
        P2[config/douyin_config.py<br/>抖音配置]
        P3[config/bilibili_config.py<br/>B站配置]
    end

    subgraph 配置项
        C1[平台设置]
        C2[代理设置]
        C3[浏览器设置]
        C4[存储设置]
        C5[爬虫控制]
    end

    S1 --> L1
    S2 --> L1
    S3 --> L1

    L1 --> L2
    L2 --> P1
    L2 --> P2
    L2 --> P3

    L1 --> C1
    L1 --> C2
    L1 --> C3
    L1 --> C4
    L1 --> C5
```

## 10. 模块依赖关系图

```mermaid
graph LR
    subgraph 高层模块
        H1[main.py]
        H2[api/main.py]
    end

    subgraph 核心模块
        C1[base/base_crawler.py]
        C2[CrawlerFactory]
    end

    subgraph 平台模块
        P1[xhs/core.py]
        P2[xhs/client.py]
        P3[xhs/login.py]
        P4[douyin/core.py]
    end

    subgraph 基础设施
        I1[proxy/]
        I2[cache/]
        I3[store/]
        I4[database/]
        I5[tools/]
    end

    subgraph 第三方库
        T1[Playwright]
        T2[httpx]
        T3[SQLAlchemy]
        T4[FastAPI]
    end

    H1 --> C2
    H2 --> T4
    T4 --> H1

    C2 --> C1
    C2 --> P1
    C2 --> P4

    P1 --> P2
    P1 --> P3
    P1 --> I1
    P1 --> I2
    P1 --> I3
    P1 --> I5

    P2 --> I1
    P2 --> T2
    P2 --> I5

    P3 --> T1
    P3 --> I5

    I3 --> I4
    I4 --> T3
    I5 --> T1
    I5 --> T2
```

## 11. 类继承关系图

```mermaid
classDiagram
    class AbstractCrawler {
        <<abstract>>
        +start()*
        +search()*
        +launch_browser()*
    }

    class AbstractLogin {
        <<abstract>>
        +begin()*
    }

    class AbstractApiClient {
        <<abstract>>
        +request()*
    }

    class AbstractStore {
        <<abstract>>
        +store_content()*
    }

    class XiaoHongShuCrawler {
        +start()
        +search()
        +get_specified_notes()
        +get_creators_and_notes()
    }

    class XiaoHongShuLogin {
        +begin()
        +login_by_qrcode()
        +login_by_mobile()
        +login_by_cookies()
        +check_login_state()
    }

    class XiaoHongShuClient {
        +request()
        +get_note_by_keyword()
        +get_note_by_id()
        +get_note_all_comments()
        +pong()
    }

    class XhsCsvStoreImplement {
        +store_content()
    }

    class XhsDbStoreImplement {
        +store_content()
    }

    class ProxyRefreshMixin {
        +_refresh_proxy_if_expired()
    }

    AbstractCrawler <|-- XiaoHongShuCrawler
    AbstractLogin <|-- XiaoHongShuLogin
    AbstractApiClient <|-- XiaoHongShuClient
    AbstractStore <|-- XhsCsvStoreImplement
    AbstractStore <|-- XhsDbStoreImplement
    ProxyRefreshMixin <|-- XiaoHongShuClient
```

## 12. 包结构树状图

```mermaid
graph TD
    Root[MediaCrawler/]
    
    Root --> Base[base/]
    Base --> BC[base_crawler.py]
    
    Root --> MP[media_platform/]
    MP --> XHS[xhs/]
    XHS --> XHS1[core.py]
    XHS --> XHS2[client.py]
    XHS --> XHS3[login.py]
    XHS --> XHS4[field.py]
    XHS --> XHS5[exception.py]
    XHS --> XHS6[extractor.py]
    XHS --> XHS7[help.py]
    XHS --> XHS8[playwright_sign.py]
    XHS --> XHS9[xhs_sign.py]
    
    MP --> DY[douyin/]
    DY --> DY1[core.py]
    DY --> DY2[client.py]
    DY --> DY3[login.py]
    
    MP --> KS[kuaishou/]
    MP --> BILI[bilibili/]
    MP --> WB[weibo/]
    MP --> TB[tieba/]
    MP --> ZH[zhihu/]
    
    Root --> Store[store/]
    Store --> SX[xhs/]
    SX --> SX1[__init__.py]
    SX --> SX2[_store_impl.py]
    SX --> SX3[xhs_store_media.py]
    
    Root --> Cache[cache/]
    Cache --> CA1[cache_factory.py]
    Cache --> CA2[local_cache.py]
    Cache --> CA3[redis_cache.py]
    Cache --> CA4[abs_cache.py]
    
    Root --> Proxy[proxy/]
    Proxy --> P1[proxy_ip_pool.py]
    Proxy --> P2[proxy_mixin.py]
    Proxy --> P3[base_proxy.py]
    Proxy --> P4[types.py]
    Proxy --> PP[providers/]
    PP --> PP1[kuaidl_proxy.py]
    PP2[wandou_proxy.py]
    
    Root --> DB[database/]
    DB --> DB1[models.py]
    DB --> DB2[db_session.py]
    DB --> DB3[db.py]
    DB --> DB4[mongodb_store_base.py]
    
    Root --> Tools[tools/]
    Tools --> T1[cdp_browser.py]
    Tools --> T2[browser_launcher.py]
    Tools --> T3[async_file_writer.py]
    Tools --> T4[utils.py]
    Tools --> T5[word_cloud.py]
    
    Root --> API[api/]
    API --> A1[main.py]
    API --> AR[routers/]
    AR --> AR1[crawler.py]
    AR --> AR2[data.py]
    API --> AS[services/]
    AS --> AS1[crawler_manager.py]
    API --> ASC[schemas/]
    
    Root --> CFG[config/]
    CFG --> C1[base_config.py]
    CFG --> C2[xhs_config.py]
    
    Root --> Model[model/]
    Root --> Test[test/]
    Root --> Tests[tests/]
    Root --> Var[var.py]
    Root --> Main[main.py]
    Root --> Req[requirements.txt]
    Root --> PP2[pyproject.toml]
```
