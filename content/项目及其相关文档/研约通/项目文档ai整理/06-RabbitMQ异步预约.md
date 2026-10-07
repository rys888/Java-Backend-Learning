# 06 · RabbitMQ 异步预约

> **只讲代码在做什么。** 承接 05 篇：05 讲到「学生抢到名额、`submit` 返回 200，但 `tb_reservation` 里还没有那一行」就停了。本篇从那一步接手，讲**那条消息怎么走完**——从发出、到 broker、到消费者、到 MySQL 落库。
>
> **全篇还是一个例子**：**学生 102 在 2026-10-07 09:00 抢到批次 7 的名额**，跟着他那条消息从头走到尾。每个代码块后面都写「例子里的对应值」。

**涉及文件**

```
config/RabbitMQConfig.java              mq/ReservationMessageDTO.java
mq/ReservationMessageConsumer.java      config/ReservationDlqListenerConfig.java
service/impl/ReservationServiceImpl.java（publishReservationMessage / markPublishedWithRetry）
service/impl/ReservationPersistenceServiceImpl.java
service/impl/ReservationRequestServiceImpl.java
enums/ReservationPersistResult.java     enums/ReservationStatus.java
enums/ReservationRequestStatus.java     utils/RedisConstants.java
resources/application.yaml
```

---
---

# 零、先把例子摆出来

## 0.1 接手时的状态（05 篇结束的那一刻）

实验室、设备、批次、学生都沿用 05 篇：**设备 3（高效液相色谱仪，实验室 2 分析测试实验室）** 下的**批次 7**，`total_quota = 5`，使用时段 2026-10-08 14:00～16:00。学生 101～105 抢到了名额。

学生 102 走完 05 篇的 `submit` 之后，三个存储是这样：

| 存储 | Key / 表 | 值 |
|---|---|---|
| Redis | `reservation:batch:quota:7` | `"3"`（101、102 各扣 1） |
| Redis | `reservation:batch:users:7` | `{101, 102}` |
| MySQL | `tb_reservation_request` | 1 行：`PRE_ACCEPTED` |
| MySQL | `tb_reservation` | **没有**设备 3 / 批次 7 的预约单（一行都没有） |
| MySQL | `tb_reservation_batch` | `id=7` 那行 `remaining_quota` 还是 **5** |
| HTTP | — | 已返回 `200` + `645827360351847424` |

那一行账本长这样（`tb_reservation_request`）：

| `request_id` | `user_id` | `batch_id` | `status` | `fail_reason` |
|---|---|---|---|---|
| `645827360351847424` | 102 | 7 | **`PRE_ACCEPTED`** | NULL |

**本篇要把它从 `PRE_ACCEPTED` 推到 `CONFIRMED`，同时把 `tb_reservation` 那行插进去。**

## 0.2 这条消息（`ReservationMessageDTO`）

消息体是 `mq/ReservationMessageDTO.java:9-18` 的四个字段：

```java
// mq/ReservationMessageDTO.java:11-17
private Long reservationId;
private Long userId;
private Long batchId;
private LocalDateTime createTime;
```

**例子里的对应值** —— 学生 102 那条消息发出去，body 就是这 20 来个字节（`ReservationServiceImpl:241-245` 逐字段填的）：

```json
{"reservationId":645827360351847424,"userId":102,"batchId":7,"createTime":"2026-10-07T09:00:00"}
```

| 字段 | 值 | 从哪来 |
|---|---|---|
| `reservationId` | `645827360351847424` | 05 篇 §7 那个 `RedisIdWorker` 算出来的 id |
| `userId` | `102` | `UserHolder.getUser().getId()` |
| `batchId` | `7` | `submit` 的入参 |
| `createTime` | `2026-10-07T09:00:00` | `submit:101` 那次 `LocalDateTime.now()`（真实值带纳秒小数，这里写成整秒便于阅读） |

**注意消息体里没有 `equipmentId`。** 源码里这个 DTO 只有上面四个字段，消费者落库只用得到 `batchId`（配一个 `user_id` 就能定位 `tb_reservation` 那一行），所以设备信息根本没进消息。

`createTime` 被序列化成 **ISO-8601 字符串**（`"2026-10-07T09:00:00"`），不是数组也不是时间戳——因为注入的是 Spring Boot 的 `ObjectMapper`，它注册了 JSR-310 模块且默认关掉了 `WRITE_DATES_AS_TIMESTAMPS`。

## 0.3 这条消息在 broker 里带的属性

| 属性 | 值 | 谁加的 |
|---|---|---|
| `content_type` | `application/json` | `Jackson2JsonMessageConverter`（`AbstractJackson2MessageConverter:378`） |
| `__TypeId__`（header） | `com.yanyuetong.mq.ReservationMessageDTO` | 同上（类型映射器写进去的类名） |
| `spring_returned_message_correlation`（header） | `"645827360351847424"` | `RabbitTemplate.setupConfirm`（`RabbitTemplate:2348-2351`），键名见 `PublisherCallbackChannel:46` |
| `deliveryMode` | `2`（PERSISTENT） | `MessageProperties` 的默认值 |

**`__TypeId__` 是消费者能直接拿到 `ReservationMessageDTO` 对象的原因**：监听器方法参数写的是 `@Payload ReservationMessageDTO`，converter 靠这个 header 知道该反序列化成哪个类。

---
---

# 一、先看结果：这条消息走完，各存储变成什么

## 1.1 时间线

从 05 篇结束那一刻起（时刻列是**示意**，不是实测；重要的是顺序和每一步改了什么）：

| # | 时刻 | 发生什么 | Redis `quota:7` | 账本 `status` | `tb_reservation` | 批次 `remaining_quota` |
|---|---|---|---|---|---|---|
| 0 | 05 结束 | `submit` 走完 §6.5 | `"3"` | `PRE_ACCEPTED` | 无行 | 5 |
| 1 | +0ms | `convertAndSend` 把消息交给 channel | `"3"` | `PRE_ACCEPTED` | 无行 | 5 |
| 2 | +1ms | broker 落盘并回 confirm → `ACKED` | `"3"` | `PRE_ACCEPTED` | 无行 | 5 |
| 3 | +1ms | `markPublishedWithRetry` CAS 成功 | `"3"` | **`PUBLISHED`** | 无行 | 5 |
| 4 | +1ms | `submit` 返回 `200` + `645827360351847424` | `"3"` | `PUBLISHED` | 无行 | 5 |
| 5 | +2ms | 消费者预取到消息（`prefetch=1`），`getByRequestId` 读到 `PUBLISHED` | `"3"` | `PUBLISHED` | 无行 | 5 |
| 6 | +3ms | 拿到 `lock:reservation:102` | `"3"` | `PUBLISHED` | 无行 | 5 |
| 7 | +5ms | `selectById(645827...424)` → null；`selectCount(user+batch)` → 0 | `"3"` | `PUBLISHED` | 无行 | 5 |
| 8 | +6ms | `UPDATE tb_reservation_batch SET remaining_quota = remaining_quota - 1 WHERE id = 7 AND remaining_quota > 0` | `"3"` | `PUBLISHED` | 无行 | **4** |
| 9 | +7ms | `INSERT INTO tb_reservation` | `"3"` | `PUBLISHED` | **1 行** | 4 |
| 10 | +8ms | `markConfirmedSafely` 把账本推到 `CONFIRMED` | `"3"` | **`CONFIRMED`** | 1 行 | 4 |
| 11 | +9ms | `basicAck` —— 消息从队列里消失 | `"3"` | `CONFIRMED` | 1 行 | 4 |

**两条路各扣一次名额，最后对上**：Redis `quota:7` 由 Lua 脚本在抢名额那一刻扣（101、102 → `"3"`），MySQL `remaining_quota` 由 `persist` 里那条 `UPDATE` 在真落库那一刻扣（101、102 → 3）。

第 0～7 步之间 Redis 已是 `"3"`、MySQL 还是 `5`——**两个存储不一致**，在途的差额就是「还没被消费掉的消息条数」，消费完就收敛到同一个值。

> **第 8 步为什么是 5 → 4，而汇总写 4 → 3**：队列先进先出，学生 101 的消息排在 102 前面，102 这条进来时批次已经是 `4` 了。若 102 是第一条被消费的，就是 `5 → 4`。**「减 1」是确定的，从几减到几取决于前面几条有没有落库。**

## 1.2 五种变体（同一个例子，换个地方出错）

| 变体 | 哪一步变了 | 投递结果的判定 | 结果 |
|---|---|---|---|
| **A** | broker 回的是 nack | `!confirm.isAck()` → `CONFIRM_NACK` | 确定未投递 → 归还名额 + 账本 `COMPENSATED` → `503` |
| **B** | broker ack 了，但 exchange 路由不到队列（消息被退回） | `getReturnedMessage() != null` → `CONFIRM_RETURN` | 同上（归还名额 + `COMPENSATED` → `503`） |
| **C** | 等 confirm 超过 5 秒没等到 | `TimeoutException` 落进 `catch (Exception)` | `UNKNOWN` → **不归还名额** → `503 预约结果待确认，请稍后查询` |
| **D** | 消费者落库时 MySQL `remaining_quota` 已经是 0 | `persist` 返回 `QUOTA_CONFLICT` | 写 `fail_reason` + `basicNack` → **进 DLQ**，行列都不插 |
| **E** | 消费者落库前，账本已经被对账改成 `COMPENSATED` | `getByRequestId` 读到 `COMPENSATED` | 直接 `basicAck`，**不落库**（落库会超发） |

变体 A/B 里「归还名额」的 Redis 效果：`quota:7` `"3" → "4"`，`users:7` `{101,102} → {101}`（脚本见 05 篇与 09 篇）。

---
---

# 二、拓扑：这条消息从哪走到哪

## 2.1 六个常量

`config/RabbitMQConfig.java:26-31`：

```java
public static final String RESERVATION_EXCHANGE               = "reservation.exchange";
public static final String RESERVATION_CREATE_ROUTING_KEY     = "reservation.create";
public static final String RESERVATION_CREATE_QUEUE           = "reservation.create.queue";
public static final String RESERVATION_DLX                    = "reservation.dlx";
public static final String RESERVATION_CREATE_DLQ             = "reservation.create.dlq";
public static final String RESERVATION_CREATE_DLQ_ROUTING_KEY = "reservation.create.dlq";
```

**例子里的对应值** —— 学生 102 那条消息的路线：

```
publishReservationMessage
   │  exchange = "reservation.exchange"     routingKey = "reservation.create"
   ▼
reservation.exchange    (DirectExchange, durable=true, autoDelete=false)
   │  binding: routingKey "reservation.create"
   ▼
reservation.create.queue  (durable)
   │  x-dead-letter-exchange    = "reservation.dlx"
   │  x-dead-letter-routing-key = "reservation.create.dlq"
   │  ← 消费者在这里取消息（prefetch=1）；basicNack(tag, false, false) 或反序列化失败
   ▼
reservation.dlx         (DirectExchange, durable=true, autoDelete=false)
   │  routingKey = "reservation.create.dlq"
   ▼
reservation.create.dlq  (durable)  ← ReservationDlqConsumer 消费（containerFactory = reservationDlqListenerContainerFactory）
   ▼
tb_reservation_dlq（死信台账，10 篇）
```

**注意 `RESERVATION_CREATE_DLQ_ROUTING_KEY` 和 `RESERVATION_CREATE_DLQ` 是同一个字符串**（`"reservation.create.dlq"`）——队列名和路由键同名，但它们是两个不同的东西。

## 2.2 六个 Bean

`RabbitMQConfig.java:36-71`：

```java
@Bean DirectExchange reservationExchange() {                     // :37-39
    return new DirectExchange(RESERVATION_EXCHANGE, true, false); }
@Bean Queue reservationCreateQueue() {                           // :41-47  业务队列：唯一配了死信参数的
    return QueueBuilder.durable(RESERVATION_CREATE_QUEUE)
            .withArgument("x-dead-letter-exchange", RESERVATION_DLX)
            .withArgument("x-dead-letter-routing-key", RESERVATION_CREATE_DLQ_ROUTING_KEY).build(); }
@Bean Binding reservationCreateBinding() {                       // :49-54
    return BindingBuilder.bind(reservationCreateQueue()).to(reservationExchange())
            .with(RESERVATION_CREATE_ROUTING_KEY); }
@Bean DirectExchange reservationDlx() {                          // :56-59
    return new DirectExchange(RESERVATION_DLX, true, false); }
@Bean Queue reservationCreateDlq() {                             // :61-64  裸队列，没有 DLX
    return QueueBuilder.durable(RESERVATION_CREATE_DLQ).build(); }
@Bean Binding reservationCreateDlqBinding() {                    // :66-71
    return BindingBuilder.bind(reservationCreateDlq()).to(reservationDlx())
            .with(RESERVATION_CREATE_DLQ_ROUTING_KEY); }
```

`new DirectExchange(name, durable, autoDelete)`：第二个参数 `true` 是持久化（broker 重启后交换机还在），第三个 `false` 是不自动删除。**只有业务队列 `reservation.create.queue` 配了死信参数**；`reservation.create.dlq` 自己**没有 DLX**，进了 DLQ 的消息不会再自动转走（落台账与重放见 10 篇）。这些 Bean 都是应用启动时由 `RabbitAdmin` 自动声明到 broker 的。

**例子里的对应值**：学生 102 那条消息 ack 掉之前，`reservation.exchange` 上挂着 1 条 binding（`reservation.create`），`reservation.create.queue` 上挂着 2 个死信参数。

## 2.3 消息怎么变成 JSON

`RabbitMQConfig.java:73-76` 把 converter 注册成 Bean，**没有手动 `rabbitTemplate.setMessageConverter(...)`**：

```java
@Bean                                                                   // RabbitMQConfig.java:73-76
public Jackson2JsonMessageConverter jackson2JsonMessageConverter(ObjectMapper objectMapper) {
    return new Jackson2JsonMessageConverter(objectMapper); }
```

生效靠 Spring Boot 自动配置取容器里的 `MessageConverter` Bean 装上去（Spring Boot 2.3.12 的 `RabbitTemplateConfigurer:80`、`AbstractRabbitListenerContainerFactoryConfigurer:103`）。所以发送端把 `ReservationMessageDTO` 写成 §0.2 那个 JSON，接收端靠 `__TypeId__` 反序列化回同一个类。

---
---

# 三、配置：`application.yaml` 里的真实值

## 3.1 四项（逐字核对过）

`resources/application.yaml:31-39`：

```yaml
spring:
  rabbitmq:
    publisher-confirm-type: correlated        # :31
    publisher-returns: true                   # :32
    listener:
      simple:
        acknowledge-mode: manual              # :35
        prefetch: 1                           # :36
        # 手动 ack 模式下默认 recoverer 不会真正 nack、会卡死消费者，故关闭自动重试，由监听器显式 basicNack 进死信
        retry:
          enabled: false                      # :38-39
```

| 配置 | 真实值 | 干什么 |
|---|---|---|
| `publisher-confirm-type` | `correlated` | 开启 Publisher Confirm，并且**允许发送时传 `CorrelationData`**（`simple` 也开启 confirm，但不带 correlationData） |
| `publisher-returns` | `true` | exchange 收到了但路由不到队列时，把消息退回给发送端 |
| `acknowledge-mode` | `manual` | 容器**不自动 ack**，由监听器方法里的 `channel.basicAck/basicNack` 决定 |
| `prefetch` | `1` | 每个消费者最多同时持有 **1** 条未确认消息，处理完才取下一条 |
| `retry.enabled` | **`false`** | **完全不装重试拦截器**。`AbstractRabbitListenerContainerFactoryConfigurer:118` 的 `if (retryConfig.isEnabled())` 为假 → 既不建 `RetryTemplate`，也不会装上默认的 `RejectAndDontRequeueRecoverer`。异常直接冒到容器的 `ErrorHandler`，由监听器自己 `basicNack` |

**`:37` 那条注释说的就是 `retry.enabled: false` 的理由**：手动 ack 模式下，Spring AMQP 默认的 `RejectAndDontRequeueRecoverer` 不会真正把消息 nack 掉，消费者会卡在那条消息上。所以关掉自动重试，让异常冒到 `ConditionalRejectingErrorHandler`，再由 `onReservationMessage` 里的 `catch` 显式 `basicNack`。

**`prefetch = 1` 在例子里的含义**：学生 101～105 的五条消息都在 `reservation.create.queue` 里排队，消费者一次只拿走一条（102 那条要等 101 那条 ack 完才被取）——**同一条队列的消费是串行的**，所以 §1.1 第 8 步能说清「从 4 减到 3」。

> **注意**：这些值在 `application-local.yaml` 里**没有被覆盖**——那个文件只覆盖了 datasource / redis / rabbitmq 的密码和用户名。

## 3.2 两个回调

`RabbitMQConfig.java:92-103`：

```java
@PostConstruct
public void init() {
    rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
        if (!ack) log.error("预约消息发送未获确认：correlationData={}，cause={}", correlationData, cause);
    });
    rabbitTemplate.setReturnCallback((message, replyCode, replyText, exchange, routingKey) ->
            log.error("预约消息路由失败：replyCode={}，replyText={}，routingKey={}", replyCode, replyText, routingKey));
    rabbitTemplate.setMandatory(true);                                    // :102
}
```

- **这两个回调只打日志**，不决定投递结果。发送端（§4）不去读回调写了什么，它同步等的是 `correlationData.getFuture()`。
- `setMandatory(true)`（`:102`）是 Return 回调能触发的**前提**：没开 mandatory，路由不到队列的消息会被 broker 静默丢掉，你不会收到退回通知。

**例子里的对应值**：学生 102 这条投递成功，confirm 回调进来时 `ack = true` → 不满足 `!ack` → **一行日志都不打**。走的是 §4.5 那条路。

---
---

# 四、发送端：`publishReservationMessage` 逐行

`ReservationServiceImpl.java:236-329`，由 `submit` 在 `:136` 调用：

```java
// ReservationServiceImpl.java:136-137
publishReservationMessage(reservationId, user.getId(), batchId, now);
return reservationId;
```

## 4.1 组装消息 + 发出 + 同步等 confirm

```java
// ReservationServiceImpl.java:241-256
ReservationMessageDTO message = new ReservationMessageDTO();
message.setReservationId(reservationId);
message.setUserId(userId);
message.setBatchId(batchId);
message.setCreateTime(createTime);
CorrelationData correlationData = new CorrelationData(String.valueOf(reservationId));
try {
    rabbitTemplate.convertAndSend(
            RabbitMQConfig.RESERVATION_EXCHANGE,
            RabbitMQConfig.RESERVATION_CREATE_ROUTING_KEY,
            message,
            correlationData);
    CorrelationData.Confirm confirm = correlationData.getFuture().get(5, TimeUnit.SECONDS);
```

| 行 | 干什么 |
|---|---|
| `:241-245` | 四个 setter 填进去的就是 §0.2 那行 JSON 的四个值 |
| `:246` | `correlationData.getId()` = `"645827360351847424"`——构造参数是**字符串形式**的 id（`String.valueOf`），不是 `Long` |
| `:251-255` | 发出去：exchange = `"reservation.exchange"`，routingKey = `"reservation.create"`，body = JSON，附带 `correlationData` |
| `:256` | **阻塞当前线程，最多等 5 秒**，等 broker 的 confirm |

**`:256` 的超时值是写死的 `5` 秒**，不是配置项。`convertAndSend` 本身是异步的（发完就返回），是这行 `getFuture().get(...)` 把它变成了同步等待；超时抛 `TimeoutException`。

**例子里的对应值**：学生 102 这条大约 1 毫秒就拿到 confirm，等满 5 秒的情况见 §1.2 变体 C。

## 4.2 三种投递结果

```java
// ReservationServiceImpl.java:257-265
    if (!confirm.isAck()) {
        outcome = PublishOutcome.DEFINITELY_NOT_DELIVERED;
        failureReason = "CONFIRM_NACK";
    } else if (correlationData.getReturnedMessage() != null) {
        outcome = PublishOutcome.DEFINITELY_NOT_DELIVERED;
        failureReason = "CONFIRM_RETURN";
    } else {
        outcome = PublishOutcome.ACKED;
    }
```

判定就这三步，**依据全部来自 `CorrelationData` 的两个读取点**；枚举定义在同文件 `:362-366`（`ACKED` / `DEFINITELY_NOT_DELIVERED` / `UNKNOWN`）——**只有三个值**：确定成功、确定失败、不知道。**`UNKNOWN` 不是错误码，是「没有足够信息下判断」**。

- **`:257` `!confirm.isAck()`** → `DEFINITELY_NOT_DELIVERED`，`failureReason = "CONFIRM_NACK"`：broker 明确说没收到 → **确定没投递**。
- **`:260` ack 了但 `getReturnedMessage() != null`** → `DEFINITELY_NOT_DELIVERED`，`"CONFIRM_RETURN"`：exchange 收到了（所以 ack），但**路由不到任何队列**被退回 → 也是**确定没投递**。
- **`:263` 其余** → `ACKED`，`failureReason = null`：ack 了且没退回 → 认为已经落到队列里。

`:260` 这一支能成立，靠的是 §3.1 的 `publisher-returns: true` + `:102` 的 `setMandatory(true)`；两者缺一，退回的消息就是静默丢失。

## 4.3 三个 `catch`

```java
// ReservationServiceImpl.java:266-280
} catch (AmqpConnectException e) {
    log.error("预约消息连接 RabbitMQ 失败：reservationId={}，userId={}，batchId={}",
            reservationId, userId, batchId, e);
    outcome = PublishOutcome.DEFINITELY_NOT_DELIVERED;
    failureReason = "AMQP_CONNECT_FAILED";
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    log.error("等待预约消息确认时被中断：reservationId={}，userId={}，batchId={}",
            reservationId, userId, batchId, e);
    outcome = PublishOutcome.UNKNOWN;
} catch (Exception e) {
    log.error("预约消息发送结果不确定：reservationId={}，userId={}，batchId={}",
            reservationId, userId, batchId, e);
    outcome = PublishOutcome.UNKNOWN;
}
```

- **`AmqpConnectException`（`:266`）**：**根本没连上 broker** → 消息肯定没出去（`AMQP_CONNECT_FAILED`）→ 确定未投递。
- **`InterruptedException`（`:271`）**：等 ack 时线程被中断；`:272` 先恢复中断标志再往下走；消息到没到不知道 → `UNKNOWN`。
- **`Exception`（`:276`）**：其余全部，**包括 5 秒超时**；超时时消息可能已经在路上 → `UNKNOWN`。

**`AmqpConnectException` 和 `Exception` 分开写就是整套错误处理的核心分界**：前者能确定「没发出去」，后者不能。若把 `AmqpConnectException` 并进 `Exception`，连带失败时会误判成 UNKNOWN，名额就白扣了。

## 4.4 `ACKED`：只改账本

```java
// ReservationServiceImpl.java:282-285
if (outcome == PublishOutcome.ACKED) {
    markPublishedWithRetry(reservationId);
    return;
}
```

**什么都不回滚**——名额是 05 篇正常抢到的，消息也已经进了队列，接下来等消费者落库就行。

`markPublishedWithRetry`（`:331-360`）：**最多 2 次 CAS**，目标 `PUBLISHED`、期望 `PRE_ACCEPTED`，两次之间**没有退避**：

```java
// ReservationServiceImpl.java:332-354（节选，两处 log 略）
for (int attempt = 1; attempt <= 2; attempt++) {
    if (reservationRequestService.casStatus(
            reservationId,
            ReservationRequestStatus.PUBLISHED,        // 目标
            ReservationRequestStatus.PRE_ACCEPTED)) {  // 期望
        return;
    }
    log.warn("预约消息 ACK 后账本置为 PUBLISHED 失败：reservationId={}，attempt={}", reservationId, attempt);
}
// 两次都失败后读一次账本：已被消费者/对账推进成终态就 return——正常的先后竞争，不是故障
if (reservationRequestService.getByRequestId(reservationId).getStatus().isTerminal()) return;
```

终态只有 `CONFIRMED` 和 `COMPENSATED`（`enums/ReservationRequestStatus.java:17-19`）。**账本状态机的完整推演在 07 篇**，这里只记一条：两次重试都没成、账本又不是终态时，`:359` 只打一条 `error` 日志就结束——**不回滚、不抛异常**，因为消息已经发出去了。

**例子里的对应值**（学生 102，正常路径）：attempt 1 执行

```sql
UPDATE tb_reservation_request SET status='PUBLISHED'
 WHERE request_id = 645827360351847424 AND status = 'PRE_ACCEPTED'
```

影响 1 行 → `return`。账本那一行 `645827360351847424 / 102 / 7 / PUBLISHED / NULL`。然后 `publishReservationMessage` 返回，`submit` 返回 05 篇 §6.5 那个 `reservationId`，`ReservationController:27-30` 把它包成 `Result.ok(...)` → **HTTP 200**。

## 4.5 `DEFINITELY_NOT_DELIVERED`：归还名额 + 账本置 `COMPENSATED`

```java
// ReservationServiceImpl.java:287-312（四处 log.error/warn 的参数略）
if (outcome == PublishOutcome.DEFINITELY_NOT_DELIVERED) {
    try {
        int rollbackCode = reservationQuotaRollbackExecutor.rollback(batchId, userId);   // :289 先还 Redis 名额
        log.warn("预约消息确定未投递，名额回滚完成：reservationId={}，rollbackCode={}", reservationId, rollbackCode);
        try {
            reservationRequestService.casStatusWithFailReason(
                    reservationId,
                    ReservationRequestStatus.COMPENSATED,      // 目标
                    failureReason,                              // "CONFIRM_NACK" / "CONFIRM_RETURN" / "AMQP_CONNECT_FAILED"
                    ReservationRequestStatus.PRE_ACCEPTED,      // 期望状态可以有两个
                    ReservationRequestStatus.PUBLISHED);
        } catch (RuntimeException statusException) {
            log.error("名额回滚后账本置为 COMPENSATED 异常：reservationId={}，reason={}", reservationId, failureReason, statusException);
        }
    } catch (RuntimeException rollbackException) {
        log.error("预约消息确定未投递但名额回滚异常，账本保留非终态：reservationId={}", reservationId, rollbackException);
    }
    throw new ServiceUnavailableException("预约失败，请重试");                            // :311
}
```

三步，顺序不能换：

1. **`:289` 先还 Redis 名额**（`rollback` 的 Lua 在 05 篇 §六 讲过）；
2. **`:293-298` 再把账本置 `COMPENSATED`**，`fail_reason` 就是 §4.2/§4.3 那个字符串，期望状态**允许两个**（`PRE_ACCEPTED` 或 `PUBLISHED`）——消息已经发出去了，confirm 也可能回来过，账本处在哪个状态取决于时序；
3. **`:311` 抛 `ServiceUnavailableException`** → `WebExceptionAdvice` 映射成 **HTTP 503**，message 是「预约失败，请重试」。

**`rollback` 失败时**（`:307` 那个 catch）只打日志，**账本保持非终态**，留给对账扫——名额没还回去，账本也不能标成终态。

**例子里的对应值**（变体 A，`CONFIRM_NACK`）：

| 位置 | 变化 |
|---|---|
| Redis | `quota:7` `"3"` → `"4"`（`INCR`）；`users:7` `{101,102}` → `{101}`（`SREM`） |
| 账本 | → **`COMPENSATED`**，`fail_reason = 'CONFIRM_NACK'` |
| HTTP | `503 预约失败，请重试` |
| `tb_reservation` | **仍然没有行** |

## 4.6 `UNKNOWN`：不碰 Redis，账本置 `UNKNOWN`

```java
// ReservationServiceImpl.java:314-328（三处 log 略）
reservationRequestService.casStatus(
        reservationId,
        ReservationRequestStatus.UNKNOWN,           // 目标
        ReservationRequestStatus.PRE_ACCEPTED,      // 期望可以有两个
        ReservationRequestStatus.PUBLISHED);
throw new ServiceUnavailableException("预约结果待确认，请稍后查询");
```

**和 §4.5 只差两处**：这里**没有 `rollback`**（名额先留着），账本目标状态是 `UNKNOWN` 而不是 `COMPENSATED`。

**为什么不还名额**：5 秒超时只说明「没等到 confirm」，消息完全可能已经落到队列里、消费者可能正在落库；这时候还名额 = 同一份名额被两个人用，直接超发。所以停在 `UNKNOWN`，等对账去判（08 篇）。

**例子里的对应值**（变体 C）：Redis **一个字节都没动**（`quota:7` 还是 `"3"`）；账本 → **`UNKNOWN`**，`fail_reason` 不变（仍是 NULL）；HTTP `503 预约结果待确认，请稍后查询`。

## 4.7 一个源码上的纠正：`CorrelationData` 的 id 是给「退回」用的，不是给 confirm 用的

老文档里写过「broker 的 ack 就是靠这个 id 对回来的」，**源码不是这样**。翻 Spring AMQP 2.2.18（本项目实际用的版本）：

```java
// spring-rabbit RabbitTemplate.java:2344-2351
long nextPublishSeqNo = channel.getNextPublishSeqNo();
message.getMessageProperties().setPublishSequenceNumber(nextPublishSeqNo);
publisherCallbackChannel.addPendingConfirm(this, nextPublishSeqNo,
        new PendingConfirm(correlationData, System.currentTimeMillis()));
if (correlationData != null && StringUtils.hasText(correlationData.getId())) {
    message.getMessageProperties().setHeader(PublisherCallbackChannel.RETURNED_MESSAGE_CORRELATION_KEY,
            correlationData.getId());
}
```

```java
// spring-rabbit PublisherCallbackChannelImpl.java:1072-1081（节选）
LongString returnCorrelation = (LongString) properties.getHeaders().get(RETURNED_MESSAGE_CORRELATION_KEY);
if (returnCorrelation != null) {
    confirm = this.pendingReturns.remove(returnCorrelation.toString());
}
```

1. **Publisher Confirm 是按「发布序号」（`deliveryTag` / publish sequence number）对回来的**，`CorrelationData` 在 `addPendingConfirm` 时就按序号存进了 map——broker 根本看不到这个 id。这就是消息属性里多一个 `spring_returned_message_correlation` header 的原因。
2. **`CorrelationData` 的 id 真正的作用是「把被退回的消息认回来」**，写进 header 由 `pendingReturns` 匹配（`PublisherCallbackChannelImpl:1075-1080` 那段）。`CorrelationData.java:51-52` 的注释正是这么说的：*"Must be unique if returns are enabled to allow population of the returnedMessage"*。

所以 `new CorrelationData(String.valueOf(reservationId))` 用 `reservationId` 做 id **正确且必要**（它天然唯一），但原因不是「broker 靠它对 ack」，而是「退回的回调靠它找回 `CorrelationData`」。

---
---

# 五、消费端：`onReservationMessage` 逐行

`mq/ReservationMessageConsumer.java:39-97`

## 5.1 方法签名

```java
// ReservationMessageConsumer.java:39-44
@RabbitListener(queues = RabbitMQConfig.RESERVATION_CREATE_QUEUE)
public void onReservationMessage(
        @Payload ReservationMessageDTO messageDTO,
        Channel channel,
        Message message) throws IOException {
    long deliveryTag = message.getMessageProperties().getDeliveryTag();
```

三个参数各司其职：`@Payload` 是 §0.2 那个 JSON 反序列化回来的对象；`Channel` 用来 `basicAck` / `basicNack`；`Message` 取 `deliveryTag`（`:44`，这条消息在本信道上的投递序号，ack/nack 都要带上）。

**`@RabbitListener` 没有指定 `containerFactory`**，所以用默认 Bean 名 `rabbitListenerContainerFactory`——就是 `RabbitMQConfig:78-90` 那个工厂。§3.1 那五项配置都是通过它生效的。

## 5.2 先查账本

```java
// ReservationMessageConsumer.java:45-57（log 参数略）
try {
    ReservationRequest request = reservationRequestService.getByRequestId(messageDTO.getReservationId());
    if (request == null) {
        log.warn("预约请求账本不存在，继续落库：reservationId={}", messageDTO.getReservationId());
    } else if (request.getStatus() == ReservationRequestStatus.COMPENSATED) {
        // 已被对账判定终结并归还名额；此时仍落库会形成「MySQL 有行 + Redis 名额已归还」的超发
        log.warn("预约请求已被补偿，拒绝落库并确认消息：reservationId={}", messageDTO.getReservationId());
        channel.basicAck(deliveryTag, false);
        return;
    }
```

`getByRequestId` 就是 `reservationRequestMapper.selectById(requestId)`（`ReservationRequestServiceImpl.java:33-36`）。两个分支：

- **账本不存在**（`:48`）：`log.warn` 一下，**继续往下落库**（不 return）——消息本身带着完整的 id/user/batch，够落库了。
- **账本已经是 `COMPENSATED`**（`:51`）：对账已经判定这次预约失败、**并且已经把名额还回 Redis 了**。此时若还落库，就会出现「`tb_reservation` 多一行 + Redis 名额已归还」→ **同一份名额被用了两次**。所以直接 `basicAck` 丢掉消息，**不落库**。

**例子里的对应值**：读到 102 那行账本，`status = 'PUBLISHED'`（§4.4 已 CAS 过）——既不是 null 也不是 `COMPENSATED`，两个分支都不进。若消费者跑在 `markPublishedWithRetry` 前面，读到的是 `PRE_ACCEPTED`，**结论不变**。

## 5.3 加锁落库

```java
// ReservationMessageConsumer.java:59-66（log 参数略）
ReservationPersistResult result = persistWithLock(messageDTO);
if (result == null) {
    log.error("获取预约锁超时，消息进入死信队列：userId={}", messageDTO.getUserId());
    recordFailReasonSafely(messageDTO.getReservationId(), "LOCK_TIMEOUT");
    channel.basicNack(deliveryTag, false, false);
    return;
}
```

**`null` 不是一种「持久化结果」，是「没拿到锁」**——`persistWithLock` 拿不到锁时返回 `null` 而不是抛异常。处理三步：写 `fail_reason = "LOCK_TIMEOUT"` → **`basicNack(tag, false, false)`** → 进 DLQ。

`persistWithLock`（`:127-148`）：

```java
// ReservationMessageConsumer.java:127-148
RLock lock = redissonClient.getLock(RedisConstants.LOCK_RESERVATION_KEY + messageDTO.getUserId());
if (!lock.tryLock(2, 10, TimeUnit.SECONDS)) {                       // :131 最多等 2 秒；租期 10 秒
    return null;
}
try {
    Reservation reservation = new Reservation()
            .setId(messageDTO.getReservationId())                   // :137 主键由消息给（IdType.INPUT，不自增）
            .setUserId(messageDTO.getUserId())
            .setBatchId(messageDTO.getBatchId())
            .setStatus(ReservationStatus.RESERVED)                  // :140
            .setCreateTime(messageDTO.getCreateTime());             // :141 用消息里的时间，不是现在
    return reservationPersistenceService.persist(reservation);
} finally {
    if (lock.isHeldByCurrentThread()) lock.unlock();                // :144-146
}
```

- **锁的粒度是「每个用户一把」**：`RedisConstants.LOCK_RESERVATION_KEY = "lock:reservation:"`（`RedisConstants.java:17`），key 后缀拼 `userId`（例子：`lock:reservation:102`）。同一用户的消息串行，不同用户并发。
- **`:131` `tryLock(2, 10, TimeUnit.SECONDS)`**：最多等 **2 秒**；拿到后租期 **10 秒**（显式给了 leaseTime，Redisson 的看门狗不续期）。
- **`:137` `setId(...)` 用消息里的 id**：`Reservation` 实体是 `@TableId(value = "id", type = IdType.INPUT)`（`entity/Reservation.java:22-23`）——主键外部给，不是数据库自增。**`:141` `createTime` 也用消息里的**（2026-10-07 09:00），不是消费者处理的时间。
- **`:144-146` `finally` 先 `isHeldByCurrentThread()` 再 `unlock()`**：Redisson 的 `unlock` 只能由持有线程调用，非持有线程调会抛 `IllegalMonitorStateException`。

**例子里的对应值**：锁 key 是 `lock:reservation:102`，等 0 毫秒就拿到了（没有别人在抢），组装出来的 `Reservation` 对象：

| 字段 | 值 |
|---|---|
| `id` | `645827360351847424` |
| `userId` | `102` |
| `batchId` | `7` |
| `status` | `RESERVED` |
| `createTime` | `2026-10-07T09:00:00` |
| `quotaReleased` | `null`（没 set，留给数据库默认值） |
| `updateTime` | `null`（同上） |

## 5.4 按持久化结果分三支

```java
// ReservationMessageConsumer.java:67-79
switch (result) {
    case PERSISTED:
    case DUPLICATE:
        markConfirmedSafely(messageDTO.getReservationId());
        channel.basicAck(deliveryTag, false);
        break;
    case QUOTA_CONFLICT:
        recordFailReasonSafely(messageDTO.getReservationId(), "QUOTA_CONFLICT");
        channel.basicNack(deliveryTag, false, false);
        break;
    default:
        throw new IllegalStateException("未知的预约持久化结果：" + result);
}
```

枚举只有三个值（`enums/ReservationPersistResult.java:3-7`）：

| result | 含义 | 动作 |
|---|---|---|
| `PERSISTED` | 这次真落库了 | 账本置 `CONFIRMED` + **ACK** |
| `DUPLICATE` | 之前已经落过了（重复投递/重放） | 账本置 `CONFIRMED` + **ACK** |
| `QUOTA_CONFLICT` | MySQL 的 `remaining_quota` 已经是 0 | 写 `fail_reason` + **NACK** → DLQ |

- **`PERSISTED` 和 `DUPLICATE` 走同一支**：重复投递不报错，确认掉就行，这就是幂等点。
- **`QUOTA_CONFLICT` 为什么不能 ACK**：Redis 说有名额、MySQL 的 `remaining_quota` 却是 0，两个存储不一致。既不能当成功丢掉，也不能无脑重试，所以 NACK 进 DLQ 留下痕迹。

## 5.5 两个 `catch`

```java
// ReservationMessageConsumer.java:80-96（log 参数略）
} catch (DuplicateKeyException e) {
    // 同一 user 的消息已被 persistWithLock 串行化 → 这里可达的冲突只可能是 reservationId 主键冲突，
    // 不是 uk_user_batch_active。这条消息没落库，若 ACK 会静默消失且 DLQ 无痕迹，必须 NACK。
    log.error("预约记录主键冲突，消息进入死信队列：reservationId={}", messageDTO.getReservationId(), e);
    channel.basicNack(deliveryTag, false, false);
} catch (Exception e) {
    if (e instanceof InterruptedException) Thread.currentThread().interrupt();
    log.error("预约消息处理异常，进入死信队列：reservationId={}", messageDTO.getReservationId(), e);
    recordFailReasonSafely(messageDTO.getReservationId(), "PERSIST_EXCEPTION:" + e.getClass().getSimpleName());
    channel.basicNack(deliveryTag, false, false);
}
```

- **`DuplicateKeyException` 单独一个 catch**（`:80`）：同一个 user 的消息已被 `persistWithLock` 的锁串行化，所以能走到这里的唯一键冲突**只可能是 `id` 主键冲突**（不是 `uk_user_batch_active`）。**这条消息没落库，所以绝不能 ACK**，否则会静默消失、DLQ 里也不留痕迹。
- **通用 catch**（`:86`）：`InterruptedException` 先恢复中断标志（`:87-89`）；写 `fail_reason = "PERSIST_EXCEPTION:{异常类名}"`（如 `"PERSIST_EXCEPTION:IllegalStateException"`）；NACK。

**两个 catch 用的都是 `basicNack(deliveryTag, false, false)`**：第 2 个 `false` 是不批量确认，第 3 个 `false` 是 **`requeue = false`**——不重新入队，直接走 `x-dead-letter-exchange` → `reservation.dlx` → `reservation.create.dlq`。**如果第 3 个参数是 `true`**，消息会立刻被投回原队列，消费者再失败一次……无限循环。

## 5.6 `markConfirmedSafely` / `recordFailReasonSafely`

```java
// ReservationMessageConsumer.java:99-112（返回 false 时 :107 只 log.warn，catch (RuntimeException) 只 log.error）
reservationRequestService.casStatus(
        requestId,
        ReservationRequestStatus.CONFIRMED,                       // 目标
        ReservationRequestStatus.nonTerminalStatuses().toArray(new ReservationRequestStatus[0]));  // 期望集合
```

**期望状态是 `nonTerminalStatuses()`**（`enums/ReservationRequestStatus.java:21-23`），展开就是 `{PRE_ACCEPTED, PUBLISHED, UNKNOWN}`（`:14-15`）。**这三个一起写是为了兼容时序**：消费者读账本时看到哪个状态，取决于它和发送端 `markPublishedWithRetry` 谁先跑——发送端先跑看到 `PUBLISHED`、消费者先跑看到 `PRE_ACCEPTED`、曾经超时判过 `UNKNOWN` 但消息其实到了看到 `UNKNOWN`，**三种都能一步推到 `CONFIRMED`**。不管对方跑到哪一步，这一步都落得下。**失败只打日志不抛异常**——预约单已经落库了，不能让账本没跟上把成功的落库回滚掉；账本停在非终态会被对账扫到并修正（07 篇）。

`recordFailReasonSafely`（`:114-125`）同理，只打日志。它调的 `recordFailReason`（`ReservationRequestServiceImpl.java:64-72`）**只改 `fail_reason` 和 `update_time`，不改 `status`**：

```java
// ReservationRequestServiceImpl.java:68-71
return reservationRequestMapper.update(null, new LambdaUpdateWrapper<ReservationRequest>()
        .eq(ReservationRequest::getRequestId, requestId)
        .set(ReservationRequest::getFailReason, failReason)
        .set(ReservationRequest::getUpdateTime, LocalDateTime.now())) == 1;
```

`:65-67` 的注释说明了为什么要显式 set `updateTime`：MySQL 的 `ON UPDATE` 只在值真的变了的时候才触发，重复写同一个 `fail_reason` 是 no-op，行会一直挂在扫描窗口队首。

**例子里的对应值**（学生 102，正常路径）：`markConfirmedSafely` 发出一条

```sql
UPDATE tb_reservation_request
   SET status = 'CONFIRMED'
 WHERE request_id = 645827360351847424
   AND status IN ('PRE_ACCEPTED', 'PUBLISHED', 'UNKNOWN')
```

影响 1 行 → 账本变成 `CONFIRMED`。然后 `basicAck`，消息从队列里消失。

---
---

# 六、落库：`persist` 逐行

`service/impl/ReservationPersistenceServiceImpl.java:26-62`，**带 `@Transactional`**（`:26-27`）——全项目只有三个事务方法，这是其中之一。

```java
// ReservationPersistenceServiceImpl.java:26-62（原注释见源码）
@Override
@Transactional
public ReservationPersistResult persist(Reservation reservation) {
    Reservation existing = reservationMapper.selectById(reservation.getId());                 // :29
    if (existing != null                                            // :29-38 第一层：同 id...
            && existing.getUserId().equals(reservation.getUserId()) //   ...同 userId
            && existing.getBatchId().equals(reservation.getBatchId())) {
        return ReservationPersistResult.DUPLICATE;                                            // :37
    }

    Integer existingCount = reservationMapper.selectCount(                                    // :39-46 第二层：同 user + 同 batch + 仍在占位
            new LambdaQueryWrapper<Reservation>()
                    .eq(Reservation::getUserId, reservation.getUserId())
                    .eq(Reservation::getBatchId, reservation.getBatchId())
                    .in(Reservation::getStatus, ReservationStatus.occupyingStatuses()));
    if (existingCount > 0) {
        return ReservationPersistResult.DUPLICATE;                                            // :45
    }

    // 必须先扣减名额；影响 0 行时直接返回，库中不会留下未扣名额的预约。
    boolean quotaDecremented = reservationBatchService.update(                                 // :49-53
            new LambdaUpdateWrapper<ReservationBatch>()
                    .eq(ReservationBatch::getId, reservation.getBatchId())
                    .gt(ReservationBatch::getRemainingQuota, 0)
                    .setSql("remaining_quota = remaining_quota - 1"));
    if (!quotaDecremented) {
        return ReservationPersistResult.QUOTA_CONFLICT;                                        // :55
    }

    if (reservationMapper.insert(reservation) != 1) {                                          // :58
        throw new IllegalStateException("预约记录持久化失败");
    }
    return ReservationPersistResult.PERSISTED;                                                 // :61
}
```

**两层去重，判据不同**：

- **`:29-38` 按身份判**：同 `id` + 同 `userId` + 同 `batchId` → 「同一次预约的重复投递」，返回 `DUPLICATE`。三个条件缺一个就继续往下走，最终由 `insert` 撞主键抛 `DuplicateKeyException`，交给 §5.5 那个 catch 进 DLQ。`:33-36` 的注释写了理由：同 id 但归属不同也提前返回 `DUPLICATE` 的话，那条**没落库**的消息会被静默 ACK，DLQ 上不留任何痕迹。
- **`:39-46` 按占位判**：判据是「用户 + 批次 + 状态还在占位」。`occupyingStatuses()`（`enums/ReservationStatus.java:30-32`）展开是 `{RESERVED, COMPLETED, NO_SHOW}`——**除 `CANCELLED` 之外都算占用**，必须和数据库的 `active_flag` 生成列严格一致（`db/phase9_reservation_lifecycle.sql:5`：`status='CANCELLED' THEN NULL ELSE 1`），对应唯一键 `uk_user_batch_active`（`:8-10`）。

**`:49-53` 是一条 SQL，不是「先查再减」**：

```sql
UPDATE tb_reservation_batch
   SET remaining_quota = remaining_quota - 1
 WHERE id = 7 AND remaining_quota > 0
```

`remaining_quota > 0` 写在 `WHERE` 里，是**数据库层的原子条件扣减**——并发下不会两个消费者都以为还有名额。影响 0 行 → `QUOTA_CONFLICT`，**这时候不会 insert**，库里不会留下一行「没扣到名额的预约」；`:58` insert 失败（行数不是 1）→ 抛 `IllegalStateException` → §5.5 通用 catch → NACK 进 DLQ。**整个方法在一个事务里**：扣名额和 insert 要么一起成功，要么一起回滚。

**例子里的对应值**（学生 102 那条消息）：

| 步 | SQL | 结果 |
|---|---|---|
| `:29` | `SELECT * FROM tb_reservation WHERE id = 645827360351847424` | `null`（表里还没有）→ 不进 DUPLICATE 分支 |
| `:39` | `SELECT COUNT(*) FROM tb_reservation WHERE user_id = 102 AND batch_id = 7 AND status IN ('RESERVED','COMPLETED','NO_SHOW')` | `0` → 不进 DUPLICATE 分支 |
| `:49` | `UPDATE tb_reservation_batch SET remaining_quota = remaining_quota - 1 WHERE id = 7 AND remaining_quota > 0` | 影响 1 行，`4 → 3` |
| `:58` | `INSERT INTO tb_reservation (...) VALUES (...)` | 1 行 |
| — | 返回 | **`PERSISTED`** |

`INSERT` 插进去的那一行（字段值全部列出来）：

| 列 | 值 | 从哪来 |
|---|---|---|
| `id` | **`645827360351847424`** | 消息里的 `reservationId`（`IdType.INPUT`，不自增） |
| `user_id` | `102` | 消息里的 `userId` |
| `batch_id` | **`7`** | 消息里的 `batchId` |
| `status` | **`RESERVED`** | `ReservationMessageConsumer:140` 硬编码 `.setStatus(ReservationStatus.RESERVED)` |
| `quota_released` | `0` | 实体里是 `null`，MyBatis-Plus 跳过 → 用 DDL 默认值 `DEFAULT 0` |
| `create_time` | **`2026-10-07 09:00:00`** | 消息里的 `createTime`，**不是落库那一刻** |
| `update_time` | 落库那一刻 | 实体里是 `null` → 用 DDL 默认值 `CURRENT_TIMESTAMP` |
| `active_flag` | `1` | 生成列：`status != 'CANCELLED'` → `1` |

**这一行就是 05 篇 §6.5 说的「HTTP 已经返回 200，但预约单还不存在」里，迟到的那一行。**

> **把 `create_time` 和 `update_time` 对照着看**：`create_time` 是 09:00（用户点按钮），`update_time` 是消费者真正落库的时刻。消息在队列里排了几秒，这两个值就差几秒——排查「为什么用户说查不到预约」时，这两个字段的差额就是排队时间。

---
---

# 七、DLQ（一句话）

失败的消息走完 §5.3/§5.4/§5.5 的 `basicNack(tag, false, false)` 之后，会经 `reservation.dlx` 落到 `reservation.create.dlq`，由 `mq/ReservationDlqConsumer.java:28-46` 消费——**它用另一个容器工厂**（`config/ReservationDlqListenerConfig.java:17-30`，`@RabbitListener` 上显式写了 `containerFactory = DLQ_CONTAINER_FACTORY`），关键差别是 `factory.setMessageConverter(new SimpleMessageConverter())`（`:24`）：**故意不用 Jackson**，因为死在 DLQ 里的消息可能本来就是反序列化失败的，再用 Jackson 处理会形成失败循环。它把消息原文和 `x-death` 里的 `reason` 写进 `tb_reservation_dlq` 台账。DLQ 台账、重放与治理的细节在 10 篇。

---
---

# 八、几个边界（4 条）

1. **发送端同步等 5 秒会占着 Tomcat 工作线程。** `ReservationServiceImpl:256` 的 `getFuture().get(5, TimeUnit.SECONDS)` 是阻塞调用，超时值 `5` 秒**写死在源码里**、不是配置项。高峰期每个 `submit` 请求最多占住一个请求线程 5 秒，broker 慢或网络抖动时线程池会被这些等待撑满——`submit` 前半段（05 篇）本来已经靠 Redis + Lua 做到毫秒级了，这 5 秒等待是整条路上最慢、最不可控的一段。

2. **`UNKNOWN` 没有即时兜底，只能等对账。** 发送端把账本置 `UNKNOWN` 就抛 503 走人了——不还名额（怕超发），也不知道消息到底到没到。真正判决要等对账任务扫到：`listStale(update_time < now - reconcile-threshold-ms)`，`application.yaml:52` 里 `reconcile-threshold-ms: 600000`（**10 分钟**），`:51` 里 `reconcile-interval-ms: 300000`（**5 分钟**）。也就是说这条请求最长可能挂十几分钟，期间用户看到的是「预约结果待确认」，而 Redis 名额已经被扣住。对账的判据是「`tb_reservation` 里有没有这一行」：有 → 置 `CONFIRMED`；没有 → 归还名额 + 置 `COMPENSATED`（`ReservationReconcileServiceImpl.java:111-135`）。

3. **消费失败时账本状态不推进，只记 `fail_reason`。** §5.3～§5.5 的四种 NACK（`LOCK_TIMEOUT` / `QUOTA_CONFLICT` / `PERSIST_EXCEPTION:*` / 主键冲突）里，只有主键冲突那条连 `fail_reason` 都不写。账本会停在 `PUBLISHED` / `UNKNOWN` 这些非终态上，全靠 10 篇的 DLQ 台账 + 08 篇的对账收敛。

4. **`markPublishedWithRetry` 的两次重试没有间隔、也不报错。** `ReservationServiceImpl:332-346` 的两次 CAS 是紧接着跑的，连续两次失败后如果账本还不是终态，只打一条 `error` 日志（`:359`）就结束了——**不回滚、不抛异常**，因为消息已经发出去了。这一行最终也会被对账扫到。

---
---

# 九、速查：学生 102 这一条消息从头走到尾

```
POST /reservation  {"batchId": 7}   →  submit()                    ← 05 篇
  │  Redis: quota:7 "5"→"3"，users:7 {101,102}
  │  账本 INSERT (PRE_ACCEPTED)；tb_reservation 还没有行
  │
  └─ publishReservationMessage(reservationId=645827360351847424, userId=102, batchId=7, createTime=09:00)
       │
       ├─ 组装 DTO
       │    {"reservationId":645827360351847424,"userId":102,"batchId":7,
       │     "createTime":"2026-10-07T09:00:00"}
       │  CorrelationData("645827360351847424")
       │
       ├─ convertAndSend("reservation.exchange", "reservation.create", dto, correlationData)
       │    headers: __TypeId__=com.yanyuetong.mq.ReservationMessageDTO
       │             spring_returned_message_correlation=645827360351847424
       │    content_type: application/json
       │
       ├─ correlationData.getFuture().get(5, SECONDS)      ← 阻塞最多 5 秒
       │    ├─ !confirm.isAck()                → CONFIRM_NACK        ┐
       │    ├─ getReturnedMessage() != null    → CONFIRM_RETURN      ├→ DEFINITELY_NOT_DELIVERED
       │    ├─ AmqpConnectException            → AMQP_CONNECT_FAILED ┘
       │    ├─ InterruptedException / 其它异常（含 TimeoutException） → UNKNOWN
       │    └─ 其它                                                  → ACKED   ← 102 走这支
       │
       ├─ ACKED                            ← 102 走这支
       │    └─ markPublishedWithRetry
       │         UPDATE tb_reservation_request SET status='PUBLISHED'
       │          WHERE request_id=645827360351847424 AND status='PRE_ACCEPTED'   → 1 行
       │
       ├─ DEFINITELY_NOT_DELIVERED
       │    └─ rollback(7,102) → quota:7 "3"→"4"；账本→'COMPENSATED'；throw 503
       │
       ├─ UNKNOWN
       │    └─ 不碰 Redis；账本→'UNKNOWN'；throw 503「预约结果待确认」
       │
       └─ return 645827360351847424                                     → 200

───────────── 以上在请求线程里结束；以下在消费者线程里 ─────────────

reservation.create.queue  （prefetch=1，一次一条）
  │
  └─ onReservationMessage(@Payload dto, Channel, Message)      ← rabbitListenerContainerFactory
       │    acknowledge-mode=manual  prefetch=1  retry.enabled=false
       │    deliveryTag = 这条消息的投递序号
       │
       ├─ getByRequestId(645827360351847424)
       │    ├─ null        → log.warn，继续落库
       │    ├─ COMPENSATED → basicAck + return（不落库，防超发）
       │    └─ PUBLISHED   ← 102 到这里（也可能读到 PRE_ACCEPTED，结论相同）
       │
       ├─ persistWithLock
       │    │  lock = redisson.getLock("lock:reservation:102")
       │    │  tryLock(2, 10, SECONDS)
       │    │    └─ 拿不到 → null → fail_reason="LOCK_TIMEOUT" + basicNack → DLQ
       │    │
       │    └─ persist(@Transactional)
       │         ├─ selectById(id)                       → null
       │         ├─ selectCount(user,batch,occupying)    → 0
       │         ├─ UPDATE tb_reservation_batch
       │         │    SET remaining_quota = remaining_quota - 1
       │         │  WHERE id=7 AND remaining_quota > 0   → 1 行（4→3）
       │         ├─ INSERT tb_reservation
       │         │    (id=645827360351847424, user_id=102, batch_id=7,
       │         │     status='RESERVED', quota_released=0,
       │         │     create_time='2026-10-07 09:00:00', active_flag=1)
       │         └─ return PERSISTED
       │
       ├─ switch(result)
       │    ├─ PERSISTED / DUPLICATE → markConfirmedSafely + basicAck      ← 102 走这支
       │    ├─ QUOTA_CONFLICT        → fail_reason="QUOTA_CONFLICT" + basicNack
       │    └─ default               → IllegalStateException
       │
       ├─ catch DuplicateKeyException → basicNack → DLQ
       └─ catch Exception            → fail_reason="PERSIST_EXCEPTION:*" + basicNack → DLQ

  └─ markConfirmedSafely
       UPDATE tb_reservation_request SET status='CONFIRMED'
        WHERE request_id=645827360351847424
          AND status IN ('PRE_ACCEPTED','PUBLISHED','UNKNOWN')      → 1 行
```

**三个存储的最终状态**

| 存储 | 值 |
|---|---|
| Redis `reservation:batch:quota:7` | `"3"` |
| Redis `reservation:batch:users:7` | `{101, 102}` |
| MySQL `tb_reservation_request` | `645827360351847424 / 102 / 7 / CONFIRMED / NULL` |
| MySQL `tb_reservation` | 1 行：`645827360351847424 / 102 / 7 / RESERVED / quota_released=0 / create_time=2026-10-07 09:00:00` |
| MySQL `tb_reservation_batch` | `id=7` 的 `remaining_quota` = **3**（与 Redis 收敛到同一个数） |
| HTTP | `200` + `645827360351847424` |

## 9.1 三种投递结果对照

`PublishOutcome` 三个值的判定条件、`failureReason`、Redis 名额动不动、账本落到哪个状态、返回什么 HTTP 码，都已写在 **§4.2 的判定三步 + §4.3 的三个 catch + §4.4 / §4.5 / §4.6 三支** 里，这里不重复。

## 9.2 账本状态机（`tb_reservation_request.status`）

```
PRE_ACCEPTED ──markPublished 重试 2 次──► PUBLISHED ──(消费者落库成功)──► CONFIRMED    ← 终态
      │                                       │
      │(投递确定失败)                          │(投递结果不确定)
      ▼                                       ▼
COMPENSATED ← ← ← ← ← (对账扫到且无行) ← ← UNKNOWN ──(对账扫到且有行)→ CONFIRMED
```

**终态只有两个**（`ReservationRequestStatus.java:17-19`）：`CONFIRMED`、`COMPENSATED`。**消费者 §5.6 的 CAS 期望集合是 `{PRE_ACCEPTED, PUBLISHED, UNKNOWN}`**——除 `COMPENSATED` 外的三个状态都能一步推到 `CONFIRMED`；这张图的完整推演在 07 篇。

## 9.3 ACK / NACK 对照

| 情况 | 动作 | 结果 |
|---|---|---|
| 账本已 `COMPENSATED` | `basicAck(tag, false)` | 消息丢弃，**不落库**（防超发） |
| `PERSISTED` / `DUPLICATE` | `basicAck(tag, false)` | 正常结束，账本 → `CONFIRMED` |
| 锁超时（`result == null`） | `basicNack(tag, false, false)` | → DLQ，`fail_reason=LOCK_TIMEOUT` |
| `QUOTA_CONFLICT` | `basicNack(tag, false, false)` | → DLQ，`fail_reason=QUOTA_CONFLICT` |
| `DuplicateKeyException` | `basicNack(tag, false, false)` | → DLQ（不写 `fail_reason`） |
| 其它 `Exception` | `basicNack(tag, false, false)` | → DLQ，`fail_reason=PERSIST_EXCEPTION:{类名}` |
| 反序列化失败（进不了方法体） | `ConditionalRejectingErrorHandler` | reject → DLQ（`RejectManual` 默认就是 `true`） |

> 最后一行值得单独说一句：JSON 反序列化发生在**进入 `onReservationMessage` 之前**，所以方法体里的 `try/catch` 根本接不住。这就是 `RabbitMQConfig:86-88` 那个 `ConditionalRejectingErrorHandler` 存在的理由——它按 `DefaultExceptionStrategy.isCauseFatal` 判定，把 `MessageConversionException` 这类**致命**错误转成 reject。
>
> **另外，`RabbitMQConfig:87` 的 `errorHandler.setRejectManual(true)` 其实和默认值相同**（Spring AMQP 2.2.18 里 `ConditionalRejectingErrorHandler:63` 就是 `private boolean rejectManual = true;`），这行代码不改行为，只是把「手动 ack 模式下也要 reject」这个意图写出来。

## 9.4 常量与数值一览

| 项 | 值 | 出处 |
|---|---|---|
| 交换机 | `reservation.exchange`（Direct, durable） | `RabbitMQConfig:26` |
| 路由键 | `reservation.create` | `RabbitMQConfig:27` |
| 业务队列 | `reservation.create.queue`（durable） | `RabbitMQConfig:28` |
| 死信交换机 | `reservation.dlx` | `RabbitMQConfig:29` |
| 死信队列 | `reservation.create.dlq` | `RabbitMQConfig:30` |
| 死信路由键 | `reservation.create.dlq` | `RabbitMQConfig:31` |
| 等 confirm 超时 | **5 秒**（写死） | `ReservationServiceImpl:256` |
| `markPublishedWithRetry` 次数 | **2** 次，无间隔 | `ReservationServiceImpl:332` |
| 消费者锁 key | `lock:reservation:{userId}` → 例子 `lock:reservation:102` | `RedisConstants:17` + `ReservationMessageConsumer:129-130` |
| 锁等待 / 租期 | **2 秒 / 10 秒** | `ReservationMessageConsumer:131` |
| `prefetch` | **1** | `application.yaml:36` |
| `retry.enabled` | **false** | `application.yaml:38-39` |
| `acknowledge-mode` | `manual` | `application.yaml:35` |
| 对账阈值 / 间隔 | **10 分钟 / 5 分钟** | `application.yaml:52` / `:51` |
