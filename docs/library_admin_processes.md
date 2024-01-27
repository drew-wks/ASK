```mermaid
sequenceDiagram
    actor Curator
    participant System
    Curator->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Curator: Great!
    John->>System: How about you?
    System-->>John: Jolly good!
```
