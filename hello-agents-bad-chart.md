# 测试错误图

```mermaid
graph TB
    A[Start] --> B{Decision}
    B -->|Yes| C[Success]
    B -->|No| D[Retry]
    D --> A
    invalid syntax here!!!
```
