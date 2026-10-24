## **1. RabbitMQ 的核心组件有哪些？**

RabbitMQ 主要包含 **Producer、Exchange、Queue、Binding、Consumer、Connection、Channel、Broker** 八个核心组件。

|**核心组件**|**作用**|
|---|---|
|**Producer（生产者）**|负责发送消息|
|**Exchange（交换机）**|接收生产者发送的消息，并根据规则路由到队列|
|**Queue（队列）**|存储消息，等待消费者消费|
|**Binding（绑定）**|建立 Exchange 和 Queue 之间的绑定关系|
|**Consumer（消费者）**|从队列获取消息并执行业务逻辑|
|**Connection（连接）**|应用程序与 RabbitMQ Broker 之间建立的 TCP 连接|
|**Channel（信道）**|复用 TCP 连接的轻量级通信通道，消息操作通常通过 Channel 完成|
|**Broker（消息代理）**|RabbitMQ 服务端，负责接收、路由和存储消息|

### **2. RabbitMQ 的工作流程**

```text
Producer（生产者）
       │
       │ 通过 Connection / Channel 发送消息
       ↓
Exchange（交换机）
       │
       │ 根据 Binding + Routing Key 路由
       ↓
Queue（消息队列）
       │
       │ 消费者获取消息
       ↓
Consumer（消费者）
       │
       ↓
执行业务逻辑 → ACK 确认
```

**需要注意三个概念：**

- **Exchange**：负责消息路由，本身不负责普通消息的长期存储。
- **Queue**：负责存储消息，消费者从 Queue 获取消息，而不是直接从 Exchange 获取。
- **Routing Key**：生产者发送消息时指定的路由标识，交换机结合绑定规则决定消息进入哪个队列。

### **3. Exchange 有哪些类型？**

RabbitMQ 常见的交换机类型有四种：

| **类型**      | **路由规则**                                        |
| ----------- | ----------------------------------------------- |
| **Direct**  | Routing Key 与 Binding Key 精确匹配                  |
| **Topic**   | 根据 Routing Key 进行通配符匹配，`*` 匹配一个单词，`#` 匹配零个或多个单词 |
| **Fanout**  | 忽略 Routing Key，将消息发送到所有绑定的队列（广播模式）              |
| **Headers** | 根据消息头属性进行匹配                                     |

---

### **4. 面试回答（背诵版）**

**RabbitMQ 的核心组件主要包括：**

1. **Producer**：负责发送消息。
2. **Exchange**：接收消息，根据 Routing Key 和 Binding 规则进行路由。
3. **Queue**：负责存储消息，等待消费者消费。
4. **Binding**：建立交换机与队列之间的绑定关系。
5. **Consumer**：负责消费消息并执行业务逻辑。
6. **Connection 和 Channel**：负责客户端与 RabbitMQ 之间的通信，Channel 可以复用 TCP 连接。
7. **Broker**：RabbitMQ 服务端，负责消息的接收、路由和存储。

其中，Exchange 主要分为 Direct、Topic、Fanout 和 Headers 四种类型。