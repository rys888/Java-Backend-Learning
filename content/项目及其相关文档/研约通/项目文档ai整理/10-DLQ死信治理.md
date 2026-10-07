# 10 · DLQ 死信治理

> **只讲代码在做什么。** 06 篇里消费端 `basicNack(tag, false, false)` 的消息会落到 `reservation.create.dlq`。本篇讲它们怎么被记进台账、怎么看、怎么被人工重放回去。
>
> **全篇用一个例子从头走到尾**：**学生 102 抢批次 7 的那条消息**（`reservationId = 645827360351847424`）消费失败进了死信队列，然后被李老师重放成功。每个代码块后面都写「例子里的对应值」。

**涉及文件**

```
config/RabbitMQConfig.java               config/ReservationDlqListenerConfig.java
mq/ReservationMessageConsumer.java       mq/ReservationDlqConsumer.java
mq/ReservationMessageDTO.java
service/impl/ReservationDlqServiceImpl.java
service/impl/ReservationPersistenceServiceImpl.java
controller/ReservationDlqController.java
entity/ReservationDlq.java               enums/ReservationDlqStatus.java
dto/ReservationDlqQueryDTO.java          vo/ReservationDlqVO.java  vo/ReservationDlqReplayVO.java
resources/db/phase8_consistency.sql      resources/application.yaml
```

---

# 零、先把例子摆出来

## 0.1 那条消息

| 字段 | 值 |
|---|---|
| `reservationId` | **645827360351847424** |
| `userId` | **102** |
| `batchId` | **7**（设备 3 高效液相色谱仪，实验室 2，管理员 = 李老师 uid 2） |
| `createTime` | `2026-10-07T09:00:01` |

消息体是 `ReservationMessageDTO`（`mq/ReservationMessageDTO.java:11-17`）经 Jackson 序列化出来的 JSON，内容等价于：

```json
{"reservationId":645827360351847424,"userId":102,"batchId":7,"createTime":"2026-10-07T09:00:01"}
```

`reservationId` 怎么算出来的见 05 篇 §七：时间戳 `150368400 << 32 | 1024`。

## 0.2 这一刻各存储长什么样

**2026-10-07 09:00:01，学生 102 刚拿到 HTTP 200 的那一刻**：

| 存储 | 内容 |
|---|---|
| Redis `reservation:batch:quota:7` | `"3"`（学生 101 扣过一次 `"5"→"4"`，102 再扣一次 `"4"→"3"`） |
| Redis `reservation:batch:users:7` | `{101, 102}` |
| MySQL `tb_reservation_batch`（id=7） | `total_quota = 5`，`remaining_quota = 4`（101 那条消息已落库扣过一次） |
| MySQL `tb_reservation` | 1 行（101 的），**102 还没有行** |
| MySQL `tb_reservation_request` | `645827360351847424` / 102 / 7 / `status = PRE_ACCEPTED` / `fail_reason = NULL` |
| MySQL `tb_reservation_dlq` | 空 |

**记住两组数字**：Redis 的 `quota:7 = "3"` 和 MySQL 的 `remaining_quota = 4`。它们是**两个独立的名额计数器**——前者在 `submit` 里由 Lua 扣，后者在消费者里由 SQL 扣（08 篇）。本篇最后要回答的就是：这条消息失败、进死信、再重放之后，**这两组数字会不会对不上**。

---

# 一、先看结果：从消费失败到重放成功

这是本篇的「答案」，后面几节拆开讲每一步怎么发生。`remaining_quota` 一列是 MySQL 的 `tb_reservation_batch.remaining_quota`。

| # | 时刻 | 发生了什么 | Redis `quota:7` | MySQL 名额 | 账本 645…424 | `tb_reservation` | `tb_reservation_dlq` |
|---|---|---|---|---|---|---|---|
| 1 | 09:00:00.000 | 学生 101 提交 | `"5"→"4"` | 5 | 101 行 `PRE_ACCEPTED` | 无 | 空 |
| 2 | 09:00:00.050 | 101 的消息被消费落库 | `"4"` | **4** | 101 行 `CONFIRMED` | +101 行 | 空 |
| 3 | 09:00:01.000 | 学生 102 提交，HTTP 200 | `"4"→"3"` | 4 | 645…424 行 `PRE_ACCEPTED` | 101 行 | 空 |
| 4 | 09:00:01.060 | broker confirm ACK → 账本置 `PUBLISHED` | `"3"` | 4 | `PUBLISHED` | 101 行 | 空 |
| 5 | 09:00:03.070 | 消费者 `tryLock` 等 2 秒没拿到锁，返回 null | `"3"` | 4 | `PUBLISHED` | 101 行 | 空 |
| 6 | 09:00:03.080 | 写 `fail_reason = 'LOCK_TIMEOUT'` | `"3"` | 4 | `PUBLISHED` / **`LOCK_TIMEOUT`** | 101 行 | 空 |
| 7 | 09:00:03.090 | `basicNack(tag, false, false)` | `"3"` | 4 | 同上 | 101 行 | 空 |
| 8 | 09:00:03.100 | broker 按 DLX 转发到死信队列 | `"3"` | 4 | 同上 | 101 行 | 空 |
| 9 | 09:00:03.150 | DLQ 消费者落台账 + `basicAck` | `"3"` | 4 | 同上 | 101 行 | **id=1 `NEW` / `LOCK_TIMEOUT` / 0** |
| 10 | 09:00:08.000 | 李老师 `POST /reservation-dlq/1/replay` 成功 | `"3"`**没动** | 4 | 同上 | 101 行 | id=1 **`REPLAYED` / 1** |
| 11 | 09:00:08.050 | 消息回到原队列，消费者这次拿到锁 | `"3"`**没动** | **3** | **`CONFIRMED`** / 仍是 `LOCK_TIMEOUT` | **+645…424 行** | id=1 `REPLAYED` / 1 |

**两个贯穿全篇的结论，先摆在这里（§八展开）**：

- **Redis 的 `quota:7` 从第 3 步到第 11 步一直是 `"3"`，一个字节都没动过。** 因为消费端和重放**根本不碰 Redis 名额**——「扣名额」发生在 `submit` 里、**发消息之前**（§2.1），重放只是把同一条消息再投一次，不会触发第二次 Lua。
- **MySQL 的 `remaining_quota` 只在第 11 步扣了一次（4→3）。** 第 5~10 步全程没扣，因为 `persist` 压根没跑成。所以重放**不多扣也不少扣**。

**变体 A：李老师拖到 09:15 才点重放。** 09:10 之后定时对账会认为这条请求「陈旧且没落库」，**归还 Redis 名额**并把账本置 `COMPENSATED`。这时重放走到第 5 步就被判 `discard`：Redis `quota:7` `"3"→"4"`、`users:7` 变 `{101}`；账本 `COMPENSATED` / `RECONCILE_NO_RESERVATION`；接口返回 `Result.fail("请求已补偿，无法重放")`；台账变 `DISCARDED`，`failure_reason` 追加 ` | DISCARD:COMPENSATED`。

**这是这条链路最要紧的时间事实：重放的有效窗口只有 10 分钟**（`reconcile-threshold-ms: 600000`）。过了窗口名额已经被对账还回去，重放会被主动拒绝——**这是保护，不是 bug**（§8.3）。

**变体 B：重放成功后手滑又点一次。** 第 1 步就拦下：`status` 已是 `REPLAYED`，返回 `Result.fail("死信记录已处理，不能重复重放")`，台账不动。

**变体 C：台账里那行 `payload` 是坏的**（比如被截断过）。第 3 步 `parseReplayablePayload` 解不出三个 id → `discard` → 台账 `DISCARDED`、`failure_reason` 追加 ` | DISCARD:PAYLOAD_NOT_REPLAYABLE`。

---

# 二、消息为什么会变成死信

## 2.1 先确认顺序：名额先扣，消息后发

`service/impl/ReservationServiceImpl.java:116-137`

```java
ReservationResultCode resultCode = reservationQuotaExecutor.tryAcquire(batch, user.getId(), now);   // ← 扣 Redis 名额
...
publishReservationMessage(reservationId, user.getId(), batchId, now);                               // ← 才发消息
```

**例子里的对应值**：第 3 步的 `"4"→"3"` 就发生在这两行之间。所以当消息后来进了死信队列时，**这个名额已经被 Lua 扣掉了**，而 MySQL 侧什么都没有。

## 2.2 消费端 `onReservationMessage` 逐行

`mq/ReservationMessageConsumer.java:39-97`

```java
@RabbitListener(queues = RabbitMQConfig.RESERVATION_CREATE_QUEUE)
public void onReservationMessage(
        @Payload ReservationMessageDTO messageDTO, Channel channel, Message message) throws IOException {
    long deliveryTag = message.getMessageProperties().getDeliveryTag();
```

业务队列的监听器**用 `reservation.create.queue` + 默认容器工厂**（不写 `containerFactory`，走 `RabbitMQConfig:78` 那个）；参数是 `@Payload ReservationMessageDTO`——**走 Jackson 反序列化**（和死信容器对比见 §4.1）。

```java
    try {
        ReservationRequest request = reservationRequestService.getByRequestId(messageDTO.getReservationId());
        if (request == null) {
            log.warn("预约请求账本不存在，继续落库：reservationId={}，userId={}", ...);
        } else if (request.getStatus() == ReservationRequestStatus.COMPENSATED) {
            // 该请求已被对账判定终结并归还名额；若此时仍落库，就会形成「MySQL 有行 + Redis 名额已归还」的超发。
            log.warn("预约请求已被补偿，拒绝落库并确认消息：reservationId={}，userId={}", ...);
            channel.basicAck(deliveryTag, false);
            return;
        }
```

先查账本，**三种情况三样处理**：

| 账本 | 动作 |
|---|---|
| 查不到（`null`） | 只打 warn，**继续落库** |
| `COMPENSATED` | 打 warn + **`basicAck` 直接确认**，不落库 |
| `PRE_ACCEPTED` / `PUBLISHED` / `UNKNOWN` | 继续往下 |

**例子里的对应值**：第 5 步查到的是 `PUBLISHED`，走第三种。`COMPENSATED` 那一支对应变体 A——名额已经还了，再落库就是「MySQL 有行 + Redis 名额已归还」的超发。

```java
        ReservationPersistResult result = persistWithLock(messageDTO);
        if (result == null) {
            log.error("获取预约锁超时，消息进入死信队列：userId={}，reservationId={}", ...);
            recordFailReasonSafely(messageDTO.getReservationId(), "LOCK_TIMEOUT");
            channel.basicNack(deliveryTag, false, false);
            return;
        }
```

**`persistWithLock` 返回 `null` 只有一个含义：拿锁超时。** 这一支就是**例子里走的那一支**，三步：打 error 日志（`userId=102，reservationId=645827360351847424`）→ `recordFailReasonSafely(..., "LOCK_TIMEOUT")` 往账本写原因 → `channel.basicNack(deliveryTag, false, false)`。

**`basicNack` 的三个参数**：

| 参数 | 值 | 含义 |
|---|---|---|
| `deliveryTag` | broker 给的投递号 | 拒绝哪一条 |
| `multiple` | `false` | 只拒绝这一条，不是「这条及之前全部」 |
| `requeue` | **`false`** | **不重新入队** → 队列配了 DLX，broker 会把它**转发到死信交换机** |

`requeue=false` 是「进死信」而不是「原地重试」的关键开关。

```java
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
    } catch (DuplicateKeyException e) {
        // 同一用户的消息已被 persistWithLock 串行化，此处可达的冲突是 reservationId 主键冲突，不是 uk_user_batch。
        // 若 ACK，这条未落库的消息会静默消失且 DLQ 无痕迹；必须 NACK 交给死信治理。
        log.error("预约记录主键冲突，消息进入死信队列：reservationId={}，userId={}", ...);
        channel.basicNack(deliveryTag, false, false);
    } catch (Exception e) {
        if (e instanceof InterruptedException) { Thread.currentThread().interrupt(); }
        log.error("预约消息处理异常，进入死信队列：reservationId={}", ...);
        recordFailReasonSafely(messageDTO.getReservationId(),
                "PERSIST_EXCEPTION:" + e.getClass().getSimpleName());
        channel.basicNack(deliveryTag, false, false);
    }
```

- `PERSISTED`（真落库了）和 `DUPLICATE`（同 id + 同 user + 同 batch 已存在，**幂等**）都算成功 → 账本置 `CONFIRMED` + `basicAck`。
- **`QUOTA_CONFLICT`**（MySQL `remaining_quota` 已是 0，扣减 SQL 影响 0 行）→ 写 `QUOTA_CONFLICT` + `basicNack`。
- **`DUPLICATE` 也 ACK 很重要**：它表示「这条消息的效果已经在库里，不用再做了」，ACK 是正确的终态。这也正是**重放不会重复扣名额的机制**——万一重放时 `tb_reservation` 已有同 id 行，`persist` 第一步就返回 `DUPLICATE`。
- 两条兜底 **都不吞消息**：`DuplicateKeyException`（同 id 但归属对不上，异常的主键冲突）只打日志、**不写 `fail_reason`**；其他任何 `Exception` 写 `PERSIST_EXCEPTION:{异常类简名}`。比如 `persist` 时 MySQL 连接抖动抛 `DataAccessResourceFailureException`，账本上写的就是 `PERSIST_EXCEPTION:DataAccessResourceFailureException`。

## 2.3 `persistWithLock`：锁是怎么超时的

`mq/ReservationMessageConsumer.java:127-148`

```java
RLock lock = redissonClient.getLock(RedisConstants.LOCK_RESERVATION_KEY + messageDTO.getUserId());
boolean locked = lock.tryLock(2, 10, TimeUnit.SECONDS);
if (!locked) {
    return null;
}
try {
    Reservation reservation = new Reservation()
            .setId(messageDTO.getReservationId()).setUserId(messageDTO.getUserId())
            .setBatchId(messageDTO.getBatchId()).setStatus(ReservationStatus.RESERVED)
            .setCreateTime(messageDTO.getCreateTime());
    return reservationPersistenceService.persist(reservation);
} finally {
    if (lock.isHeldByCurrentThread()) { lock.unlock(); }
}
```

- 锁 key 是 **`lock:reservation:` + userId**（例子：`lock:reservation:102`），**粒度是「每个用户一把」**——同一用户的消息必须串行落库。
- `tryLock(2, 10, SECONDS)` = **最多等 2 秒**拿锁；拿到后租约 10 秒。**等不到就返回 `null`**，不重试、不抛异常。

**例子里的失败是怎么发生的**：`tryLock` 从 09:00:01.070 一直等到 09:00:03.070 也没拿到 `lock:reservation:102` → 返回 `null` → §2.2 那一支写 `LOCK_TIMEOUT` + NACK。

> ⚠️ **单独一条消息不会自己跟自己抢锁**。要走到 `LOCK_TIMEOUT`，得是**同一用户的两条消息同时到达**——比如消费者在 `basicAck` 之前与 broker 断连，消息被重新投递，新老两个消费线程同时调用 `persistWithLock`；先拿到的那个被慢 SQL 卡了 2 秒以上，后来的就超时。源码里 `LOCK_RESERVATION_KEY` 只在消费端这一处用（对账用的是另一个 key `lock:reservation:reconcile`）。

落库细节在 `service/impl/ReservationPersistenceServiceImpl.java:28-61`（整个方法带 `@Transactional`）：

```java
Reservation existing = reservationMapper.selectById(reservation.getId());
if (existing != null && existing.getUserId().equals(reservation.getUserId())
        && existing.getBatchId().equals(reservation.getBatchId())) {
    return ReservationPersistResult.DUPLICATE;              // ← 幂等：同 id + 同 user + 同 batch
}
Integer existingCount = reservationMapper.selectCount(new LambdaQueryWrapper<Reservation>()
        .eq(Reservation::getUserId, reservation.getUserId())
        .eq(Reservation::getBatchId, reservation.getBatchId())
        .in(Reservation::getStatus, ReservationStatus.occupyingStatuses()));
if (existingCount > 0) {
    return ReservationPersistResult.DUPLICATE;              // ← 同用户同批次的活跃行已存在
}
// 必须先扣减名额；影响 0 行时直接返回，库中不会留下未扣名额的预约。
boolean quotaDecremented = reservationBatchService.update(new LambdaUpdateWrapper<ReservationBatch>()
        .eq(ReservationBatch::getId, reservation.getBatchId())
        .gt(ReservationBatch::getRemainingQuota, 0)
        .setSql("remaining_quota = remaining_quota - 1"));
if (!quotaDecremented) {
    return ReservationPersistResult.QUOTA_CONFLICT;
}
if (reservationMapper.insert(reservation) != 1) {
    throw new IllegalStateException("预约记录持久化失败");
}
return ReservationPersistResult.PERSISTED;
```

**两道幂等闸门排在扣名额之前**，所以「重复投递 / 重放」不会重复扣 MySQL 名额；扣了名额但 `insert` 失败会一起回滚。

**例子里的对应值**：第 5 步根本没进到这个方法（锁都没拿到），所以 `remaining_quota` 还是 4。

## 2.4 重试到底开没开

`resources/application.yaml:33-39`

```yaml
    listener:
      simple:
        acknowledge-mode: manual
        prefetch: 1
        # 手动 ack 模式下默认 recoverer 不会真正 nack、会卡死消费者，故关闭自动重试，由监听器显式 basicNack 进死信
        retry:
          enabled: false
```

**结论：自动重试是关的，这条消息只被投递一次。** 第一次消费失败 → `basicNack(requeue=false)` → 直接进死信队列，**没有「重试 3 次之后才进死信」这回事**。配置注释也写明原因：手动 ack 模式下默认的 recoverer 不会真正 NACK、消息会被卡住，所以关掉重试，由监听器自己显式 `basicNack`。

> 所以「一条消息失败几次才变成死信」的答案是 **1 次**。§7.4 会看到 `dlq-max-replay: 3` 管的是**另一件事**——台账记录被人工重放的次数，跟 broker 的投递次数无关。

## 2.5 `fail_reason` 的三个真实取值

`recordFailReasonSafely`（`mq/ReservationMessageConsumer.java:114-125`）调 `reservationRequestService.recordFailReason`，SQL 是 `UPDATE tb_reservation_request SET fail_reason = ?, update_time = NOW() WHERE request_id = ?`。Mapper 那层（`service/impl/ReservationRequestServiceImpl.java:64-72`）**显式 `setUpdateTime`**，注释说是为了让持续失败的行离开扫描窗口队首。

| `fail_reason` | 触发点 | 源码行 |
|---|---|---|
| `LOCK_TIMEOUT` | `persistWithLock` 返回 `null` | `ReservationMessageConsumer.java:63` |
| `QUOTA_CONFLICT` | MySQL 扣名额影响 0 行 | `:74` |
| `PERSIST_EXCEPTION:{类简名}` | `persist` 抛任何异常 | `:92-94` |

**例子里的对应值**：第 6 步账本上写的就是 `LOCK_TIMEOUT`（**大写常量名，不是中文**）。这个值后面会被 `tb_reservation_dlq.failure_reason` **原样取走**（§5.3 第 1 优先级）。

---

# 三、死信路由：五个名字

`config/RabbitMQConfig.java:26-31`

```java
public static final String RESERVATION_EXCHANGE = "reservation.exchange";
public static final String RESERVATION_CREATE_ROUTING_KEY = "reservation.create";
public static final String RESERVATION_CREATE_QUEUE = "reservation.create.queue";
public static final String RESERVATION_DLX = "reservation.dlx";
public static final String RESERVATION_CREATE_DLQ = "reservation.create.dlq";
public static final String RESERVATION_CREATE_DLQ_ROUTING_KEY = "reservation.create.dlq";
```

```java
// :41-47  业务队列挂 DLX
QueueBuilder.durable(RESERVATION_CREATE_QUEUE)
        .withArgument("x-dead-letter-exchange", RESERVATION_DLX)
        .withArgument("x-dead-letter-routing-key", RESERVATION_CREATE_DLQ_ROUTING_KEY).build();
// :49-54  业务交换机绑定
BindingBuilder.bind(reservationCreateQueue()).to(reservationExchange()).with(RESERVATION_CREATE_ROUTING_KEY);
// :61-64  死信队列：只有 durable，没有配 DLX
QueueBuilder.durable(RESERVATION_CREATE_DLQ).build();
// :66-71  死信交换机绑定
BindingBuilder.bind(reservationCreateDlq()).to(reservationDlx()).with(RESERVATION_CREATE_DLQ_ROUTING_KEY);
```

**五个名字一次列全**：

| 角色 | 名字 | 类型/绑定 |
|---|---|---|
| 原交换机 | `reservation.exchange` | `DirectExchange`，durable |
| 原队列 | `reservation.create.queue` | durable，带 `x-dead-letter-exchange` |
| 原 routing key | `reservation.create` | 把上面两个绑起来 |
| 死信交换机 DLX | `reservation.dlx` | `DirectExchange`，durable |
| 死信队列 DLQ | `reservation.create.dlq` | durable |

两个细节：**死信队列的 routing key 和队列名是同一个字符串** `"reservation.create.dlq"`（`RESERVATION_CREATE_DLQ` 和 `RESERVATION_CREATE_DLQ_ROUTING_KEY` 两个常量值一样）；**DLQ 自己没配 `x-dead-letter-exchange`**（`reservationCreateDlq()` 里只有 `durable`），所以死信在这里 **NACK 一次就是永久丢弃**，没有第二层兜底——§4.2 的日志就是它最后的痕迹。

**例子里的对应值**（第 7~8 步）：

```
消费端 basicNack(tag, false, false)
   │  队列 reservation.create.queue 的属性：
   │    x-dead-letter-exchange = "reservation.dlx"、x-dead-letter-routing-key = "reservation.create.dlq"
   ▼
broker：以 routing key "reservation.create.dlq" 把消息发到交换机 "reservation.dlx"
        并在 header 加一条 x-death:
          [{ count: 1, reason: "rejected", queue: "reservation.create.queue",
             exchange: "reservation.exchange", "routing-keys": ["reservation.create"] }]
   ▼
队列 "reservation.create.dlq"  ← 与 DLX 用同一个 routing key 绑定
```

`reason` 是 **`rejected`**（被拒绝），不是 `expired`/`maxlen`——因为这是显式 NACK 而死的。

---

# 四、死信消费者：另一套容器工厂

## 4.1 为什么 DLQ 要换一个 `MessageConverter`

| | 业务队列 | 死信队列 |
|---|---|---|
| Factory Bean | `rabbitListenerContainerFactory`（默认名） | `reservationDlqListenerContainerFactory` |
| 定义位置 | `RabbitMQConfig.java:78-90` | `ReservationDlqListenerConfig.java:17-30` |
| `MessageConverter` | `Jackson2JsonMessageConverter`（`RabbitMQConfig:74` 的 Bean，Boot 自动装配注入） | **`SimpleMessageConverter`** |
| 监听器参数 | `@Payload ReservationMessageDTO` | **`Message` + `Channel`** |

`config/ReservationDlqListenerConfig.java`

```java
public static final String DLQ_CONTAINER_FACTORY = "reservationDlqListenerContainerFactory";

@Bean(name = DLQ_CONTAINER_FACTORY)
public SimpleRabbitListenerContainerFactory reservationDlqListenerContainerFactory(
        ConnectionFactory connectionFactory,
        SimpleRabbitListenerContainerFactoryConfigurer configurer) {
    SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
    configurer.configure(factory, connectionFactory);
    // SimpleMessageConverter 对 JSON 只按字符集转成字符串，不会再次反序列化。
    factory.setMessageConverter(new SimpleMessageConverter());
    ...
}
```

**先 `configurer.configure(...)` 复用 Boot 配置（手动 ack、prefetch=1、关闭自动重试），再手动 `setMessageConverter` 覆盖掉 Jackson。** 动机写在消费者类注释里（`ReservationDlqConsumer.java:18-20`）：

> 使用原始 Message 消费死信，**避免反序列化失败的消息再次经过 Jackson 并形成失败循环**。

也就是说：**死信里本来就可能装着「Jackson 反序列化失败」的消息**（业务队列监听器的参数是 `@Payload ReservationMessageDTO`，payload 一变形就抛 `MessageConversionException`，那条消息就进死信）。如果 DLQ 消费者还用 Jackson，它会**再失败一次**。

> **源码核对（一个和注释对不上的细节）**：本机依赖是 `spring-amqp 2.2.18`（Boot 2.3.12）。该版本 `SimpleMessageConverter.fromMessage` 的分支是——`contentType` 以 `text` 开头 → 用 `contentEncoding`（缺省 UTF-8）转成 `String`；等于 `application/x-java-serialized-object` → Java 反序列化；**其余情况（本项目的消息是 `application/json`）直接 `content = message.getBody()`，返回 `byte[]`**。所以注释里「只按字符集转成字符串」对 JSON 来说**不准确**——源码里返回的是 `byte[]`。这不影响结论：**两条分支都不会走 Jackson 的类型化反序列化，也不会因为 payload 不是合法 JSON 而抛异常。**

## 4.2 消费者 `onDeadLetter` 逐行

`mq/ReservationDlqConsumer.java:28-46`

```java
@RabbitListener(
        queues = RabbitMQConfig.RESERVATION_CREATE_DLQ,
        containerFactory = ReservationDlqListenerConfig.DLQ_CONTAINER_FACTORY)
public void onDeadLetter(Message message, Channel channel) throws IOException {
    long deliveryTag = message.getMessageProperties().getDeliveryTag();
    byte[] body = message.getBody();
    try {
        reservationDlqService.recordDeadLetter(body, extractXDeathReason(message));
    } catch (Exception e) {
        String payload = body == null ? null : new String(body, StandardCharsets.UTF_8);
        // DLQ 没有后继死信交换机，拒绝后日志是消息永久丢弃前的最后痕迹，必须保留完整原文。
        log.error("死信台账落库失败，消息将永久丢弃：payload={}", payload, e);
        channel.basicNack(deliveryTag, false, false);
        return;
    }
    channel.basicAck(deliveryTag, false);
}
```

**方法签名里没有 `@Payload XxxDTO`，只有原始的 `Message` 和 `Channel`**——不做反序列化，`body` 就是 `byte[]`。

- **落台账成功 → `basicAck`**（第 9 步）。
- **落台账失败 → 打完整原文的 error 日志 + `basicNack(tag, false, false)`**。因为 DLQ 没有后继 DLX（§三），`requeue=false` 在这里意味着**消息永久消失**，所以必须把**完整 `payload`（不是截断后的）**打进日志。

## 4.3 提取 `x-death` 原因

```java
// ReservationDlqConsumer.java:48-61
private String extractXDeathReason(Message message) {
    try {
        List<Map<String, ?>> deaths = message.getMessageProperties().getXDeathHeader();
        if (deaths == null || deaths.isEmpty() || deaths.get(0) == null) {
            return null;
        }
        Object reason = deaths.get(0).get("reason");
        return reason == null ? null : String.valueOf(reason);
    } catch (Exception e) {
        log.warn("读取死信 x-death 原因失败，降级为空原因", e);
        return null;
    }
}
```

`x-death` 是 broker 在消息进 DLQ 时**自动加的 header**，是一个列表。**这里只取第一条（`deaths.get(0)`）的 `reason`**——broker 给的值是 `rejected` / `expired` / `maxlen` 之类。**整个方法包在 try/catch 里，任何异常都返回 `null`**（降级为空原因），不让它影响台账落库。

**例子里的对应值**：返回 `"rejected"`，但它在 §5.3 里**只排到第 3 优先级，用不上**——账本上的 `LOCK_TIMEOUT` 信息量更大，会先被取走。

---

# 五、落台账：`recordDeadLetter` 逐行

`service/impl/ReservationDlqServiceImpl.java:87-114`

```java
@Override
public ReservationDlq recordDeadLetter(byte[] body, String xDeathReason) {
    byte[] safeBody = body == null ? new byte[0] : body;
    String originalPayload = new String(safeBody, StandardCharsets.UTF_8);
    // 必须先解析完整原始字节；若先按列上限截断，合法的大 JSON 会被切断并误判为不可解析。
    Long reservationId = extractReservationId(originalPayload);

    int payloadLength = Math.min(safeBody.length, MAX_PAYLOAD_BYTES);
    String storedPayload = new String(safeBody, 0, payloadLength, StandardCharsets.UTF_8);

    String failureReason = resolveFailureReason(reservationId, xDeathReason);
    if (failureReason != null && failureReason.length() > MAX_FAILURE_REASON_LENGTH) {
        failureReason = failureReason.substring(0, MAX_FAILURE_REASON_LENGTH);
    }

    ReservationDlq deadLetter = new ReservationDlq()
            .setReservationId(reservationId).setPayload(storedPayload)
            .setFailureReason(failureReason).setReplayCount(0)
            .setStatus(ReservationDlqStatus.NEW);
    if (reservationDlqMapper.insert(deadLetter) != 1) {
        throw new IllegalStateException("死信台账插入失败");
    }
    return deadLetter;
}
```

两个上限（`:42-43`）：`MAX_PAYLOAD_BYTES = 60_000`、`MAX_FAILURE_REASON_LENGTH = 512`。

| 字段 | 上限 | 怎么截 | 列类型 |
|---|---|---|---|
| `payload` | 60000 **字节** | `Math.min(safeBody.length, 60000)` 后按字节取 | `text`（最大 65535 字节） |
| `failure_reason` | 512 **字符** | `substring(0, 512)`，按 `String.length()` | `varchar(512)` |

**`extractReservationId(originalPayload)` 一定在截断之前调用**——注释解释了：它内部要 `objectMapper.readTree(payload)`，**被截掉尾巴的 JSON 解析必然失败**，那就永远拿不到 `reservationId` 了。而 `storedPayload` 用 `new String(safeBody, 0, payloadLength, UTF_8)` **按字节切片**，**可能在多字节字符中间切断**，末尾会出半个字符——代码没做字符边界对齐。

**例子里的对应值**：payload 只有 ~100 字节，远不到 60000，`storedPayload` 就是 §0.1 那行完整 JSON；`failure_reason = "LOCK_TIMEOUT"` 只有 12 个字符，也不截。

## 5.1 `extractReservationId`：解析失败返回 `null`

```java
// :63-85
public Long extractReservationId(String payload) {
    if (payload == null) { return null; }
    try {
        JsonNode root = objectMapper.readTree(payload);
        if (root == null || !root.isObject()) { return null; }
        JsonNode reservationId = root.get("reservationId");
        if (reservationId == null || !reservationId.isNumber() || !reservationId.canConvertToLong()) {
            return null;
        }
        return reservationId.asLong();
    } catch (Exception e) {
        // 非法 JSON 是死信的正常输入形态；解析失败只降级原因判定，不能阻断台账落库。
        log.warn("解析死信 reservationId 失败，按不可解析处理：{}", e.getMessage());
        return null;
    }
}
```

**解析失败返回 `null` 而不是抛异常**——因为「反序列化失败」正是消息进 DLQ 的常见原因之一，如果这里抛异常，**这种消息就永远记不进台账**。

它比 `parseReplayablePayload`（§7.1 第 3 步）**宽松**：这边只要 `reservationId` 一个是数字就行（`isNumber` + `canConvertToLong`，浮点也算），重放那边**三个字段都必须是整型**。

**例子里的对应值**：`reservationId = 645827360351847424`。

## 5.2 `resolveFailureReason` 四级优先级

```java
// :343-373
private String resolveFailureReason(Long reservationId, String xDeathReason) {
    // 第一优先级：账本记录的是业务侧失败原因，信息量高于 broker 的通用拒绝原因。
    if (reservationId != null) {
        try {
            ReservationRequest request = reservationRequestService.getByRequestId(reservationId);
            if (request != null && request.getFailReason() != null && !request.getFailReason().isEmpty()) {
                return request.getFailReason();
            }
        } catch (Exception e) {
            // 账本查询异常时继续使用后续优先级，不能让这条死信失去唯一可查询痕迹。
            log.error("查询预约请求账本失败，降级使用死信元数据：reservationId={}", reservationId, e);
        }
    }
    if (reservationId == null) {                                        // 第二优先级：消息体给不出预约 id
        return "PAYLOAD_UNPARSEABLE";
    }
    if (xDeathReason != null && !xDeathReason.isEmpty()) {              // 第三优先级：保留 broker 原因并标注来源
        return "x-death:" + xDeathReason;
    }
    return null;                                                        // 第四优先级：都没有
}
```

| 优先级 | 条件 | 值 |
|---|---|---|
| 1 | 账本能查到且 `fail_reason` 非空 | 账本里的原值（如 `LOCK_TIMEOUT`） |
| 2 | `reservationId == null`（payload 解析不出来） | `"PAYLOAD_UNPARSEABLE"` |
| 3 | `x-death` header 里有 reason | `"x-death:rejected"` 这样带前缀 |
| 4 | 都没有 | `null` |

**第 2 优先级在「账本查询」之后**：如果账本查不到（返回 `null`）但 `reservationId` 有值，**不会**返回 `PAYLOAD_UNPARSEABLE`，而是继续走到第 3 优先级。`PAYLOAD_UNPARSEABLE` 只在**解析不出 id** 时才出现。

**例子里的对应值**：`reservationId` 有值 → 查到 645…424 那行，`fail_reason = 'LOCK_TIMEOUT'` 非空 → **直接返回 `"LOCK_TIMEOUT"`**，broker 的 `rejected` 被跳过。

## 5.3 落进 `tb_reservation_dlq` 的那一行

`resources/db/phase8_consistency.sql:14-26`

```sql
CREATE TABLE IF NOT EXISTS `tb_reservation_dlq` (
  `id`             bigint unsigned NOT NULL AUTO_INCREMENT,
  `reservation_id` bigint unsigned DEFAULT NULL COMMENT '解析出的预约id，解析失败为 NULL',
  `payload`        text COMMENT '死信消息体原文',
  `failure_reason` varchar(512) DEFAULT NULL COMMENT '失败原因（账本 JOIN 或 x-death）',
  `replay_count`   int NOT NULL DEFAULT 0 COMMENT '已重放次数',
  `status`         varchar(16) NOT NULL DEFAULT 'NEW' COMMENT 'NEW/REPLAYED/DISCARDED',
  `create_time`    timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time`    timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`), ...
```

`reservation_id` **允许为 NULL**——对应 `PAYLOAD_UNPARSEABLE` 那种情况。

**例子里的对应值**（第 9 步，id 从 1 开始）：

| `id` | `reservation_id` | `payload` | `failure_reason` | `replay_count` | `status` | `create_time` |
|---|---|---|---|---|---|---|
| 1 | 645827360351847424 | `{"reservationId":645827360351847424,"userId":102,"batchId":7,"createTime":"2026-10-07T09:00:01"}` | `LOCK_TIMEOUT` | 0 | `NEW` | 2026-10-07 09:00:03 |

`create_time` / `update_time` 由 **MySQL 的 `DEFAULT CURRENT_TIMESTAMP` 写**——`recordDeadLetter` 里没有 `setCreateTime`，MyBatis-Plus 插入时会跳过 null 字段。`replay_count = 0` 和 `status = NEW` 是代码显式设的。

**表上没有任何唯一键**——同一 `reservation_id` 可以有多行。实体类注释（`entity/ReservationDlq.java:14-19`）写明了取舍：

> 同一死信在落库成功、确认前崩溃时可能被重复投递并产生重复行，这是治理日志允许的取舍；事实来源仍是 tb_reservation，本表不做去重。

---

# 六、三个接口

`controller/ReservationDlqController.java`，前缀 `/reservation-dlq`，**三个方法全部 `@RequireRole(UserRole.LAB_ADMIN)`**（`utils/RoleInterceptor.java:20-23` 取注解、`:41` 角色不匹配时直接 `response.setStatus(403)`）。

| 方法 | 路径 | Service | 返回 |
|---|---|---|---|
| GET | `/reservation-dlq/page` | `queryPage` | `Result.ok(records, total)` |
| GET | `/reservation-dlq/{id}` | `queryById` | 查到 → `Result.ok(vo)`；查不到 → `Result.fail("死信记录不存在")` |
| POST | `/reservation-dlq/{id}/replay` | `replay` | `replayed=true` → `Result.ok(record)`；否则 → `Result.fail(reason)` |

**例子里的对应值**：李老师（uid 2，`LAB_ADMIN`）能调；**学生 101 调这三个接口都是 403**（`RoleInterceptor` 在方法执行之前就返回了）。

## 6.1 `queryPage`：列表接口不返回 `payload`

`ReservationDlqServiceImpl.java:117-147`

```java
Page<ReservationDlq> entityPage = new Page<>(current, SystemConstants.DEFAULT_PAGE_SIZE);
IPage<ReservationDlq> result = reservationDlqMapper.selectPage(entityPage,
        new LambdaQueryWrapper<ReservationDlq>()
                .select(ReservationDlq::getId, ReservationDlq::getReservationId,
                        ReservationDlq::getFailureReason, ReservationDlq::getReplayCount,
                        ReservationDlq::getStatus, ReservationDlq::getCreateTime,
                        ReservationDlq::getUpdateTime)          // ← 注意：没有 payload
                .eq(actualQuery.getStatus() != null, ReservationDlq::getStatus, actualQuery.getStatus())
                .orderByDesc(ReservationDlq::getCreateTime)
                .orderByDesc(ReservationDlq::getId));
```

- `.select(...)` **显式列出七个字段，把 `payload` 排除在外**——列表不返回 `text` 消息原文。
- **过滤条件只有 `status` 一个**（三参重载：`status == null` 时不拼这个条件）；排序 `create_time DESC, id DESC`（`id` 做二级排序，顺序稳定）。
- 页大小固定 `SystemConstants.DEFAULT_PAGE_SIZE = 5`（`utils/SystemConstants.java:5`），请求参数只有 `status` 和 `current`（`dto/ReservationDlqQueryDTO.java`）；`current` 缺省 1。
- 之后手工把实体分页转成 VO 分页（`:140-146`）：新建 `Page<ReservationDlqVO>`，拷 `current / size / total`，再放 `map(this::toVO)` 的结果。

⚠️ **但 `toVO` 里是有 `payload` 的**（`:328-341` 里 `.setPayload(deadLetter.getPayload())`）。因为列表查询没 select `payload`，实体上的 `payload` 是 `null`，`toVO` 填进去的也是 `null`。

**列表接口返回的 `payload` 恒为 `null`；`GET /reservation-dlq/{id}`（走 `selectById` 查全字段）才有值。** `vo/ReservationDlqVO.java:11-14` 的类注释也是这么写的。

---

# 七、重放：`replay` 七步

`service/impl/ReservationDlqServiceImpl.java:157-227`。入口是 `POST /reservation-dlq/1/replay`。

## 7.1 七步逐行

```java
ReservationDlq deadLetter = id == null ? null : reservationDlqMapper.selectById(id);

// 1. 只有尚未处理的台账记录可以重放。
if (deadLetter == null) {
    return rejected("死信记录不存在", null);
}
if (deadLetter.getStatus() != ReservationDlqStatus.NEW) {
    return rejected("死信记录已处理，不能重复重放", toVO(deadLetter));
}
```

**第 1 步**：`null` 或「非 `NEW`」都返回 `rejected`（`replayed = false`，**台账一个字段都不改**）。**例子里的对应值**：id=1 那行 `status = NEW`，通过；变体 B 就停在这里。

```java
// 2. 达到次数上限的记录保持 NEW，便于管理员继续审计。
int replayCount = deadLetter.getReplayCount() == null ? 0 : deadLetter.getReplayCount();
if (replayCount >= maxReplay) {
    return rejected("已达到最大重放次数", toVO(deadLetter));
}
```

**第 2 步**：`maxReplay` 来自 `@Value("${yanyuetong.reservation.dlq-max-replay:3}")`（`:60-61`），yaml 里配的是 **`3`**（`application.yaml:54`）。超限**只拒绝、不改状态**。这一分支在本例里不会走到（§7.4）。

```java
// 3. 三个业务 id 都必须是 JSON 数字，保证消息回到主队列后可被消费。
ReservationMessageDTO message = parseReplayablePayload(deadLetter.getPayload());
if (message == null) {
    return discard(deadLetter, replayCount, "PAYLOAD_NOT_REPLAYABLE", "payload 无法重放");
}
```

**第 3 步**：`parseReplayablePayload`（`:229-250`）比 `extractReservationId` 严格——**三个 id 都必须是整型数字**，缺一个就返回 `null`：

```java
if (root == null || !root.isObject()
        || !isLongNumber(root.get("reservationId"))
        || !isLongNumber(root.get("userId"))
        || !isLongNumber(root.get("batchId"))) {
    return null;
}
...
private boolean isLongNumber(JsonNode node) {
    return node != null && node.isIntegralNumber() && node.canConvertToLong();
}
```

`isIntegralNumber()` 把小数也排除了。**`payload` 是可能被截断过的**（§五），被截断的 payload 解析必然失败 → 走 `discard`（**改状态为 `DISCARDED`，不是 `rejected`**）→ 变体 C。

**例子里的对应值**：三个字段都是整数 → `treeToValue` 得到 `ReservationMessageDTO{645827360351847424, 102, 7, 2026-10-07T09:00:01}`，`createTime` 也一起还原。

```java
// 4. 预约事实表已有同 id 记录时不得再投递。
Reservation persisted = reservationMapper.selectById(message.getReservationId());
if (persisted != null) {
    return discard(deadLetter, replayCount, "ALREADY_PERSISTED", "已落库，无需重放");
}

// 5. 已补偿请求的名额已经归还，再投递会造成超发。
ReservationRequest request = null;
try {
    request = reservationRequestService.getByRequestId(message.getReservationId());
} catch (Exception e) {
    // 与主消费者保持一致：账本缺失或暂时不可查询都不阻断事实表落库。
    log.error("重放前查询预约请求账本失败，按未知状态继续：reservationId={}", message.getReservationId(), e);
}
if (request != null && request.getStatus() == ReservationRequestStatus.COMPENSATED) {
    return discard(deadLetter, replayCount, "COMPENSATED", "请求已补偿，无法重放");
}
```

**第 4 步**：`tb_reservation` 里已经有这个 id → 判 `DISCARDED`。这挡的是「其实已经落库了、只是 ACK 没成功」的那种死信。

**第 5 步**：账本已 `COMPENSATED` → 名额已经还回去了，再投递就是**超发**。**查不到账本或查询抛异常都不阻断**（与消费端「账本不存在 → 继续落库」一致）。这是变体 A 停下的一步。**例子里的对应值**：第 10 步（09:00:08）账本还是 `PUBLISHED`，通过。

```java
// 6. 使用与正常生产者一致的 publisher confirm + return 判定。
ReservationDlqReplayVO publishFailure = publish(message, deadLetter);   // 见 §7.2
if (publishFailure != null) {
    return publishFailure;
}

// 7. 只在确认成功后以预检值做乐观 CAS；投递失败绝不修改台账。
boolean updated = reservationDlqMapper.update(null,
        new LambdaUpdateWrapper<ReservationDlq>()
                .eq(ReservationDlq::getId, deadLetter.getId())
                .eq(ReservationDlq::getStatus, ReservationDlqStatus.NEW)
                .eq(ReservationDlq::getReplayCount, replayCount)          // ← 乐观锁
                .set(ReservationDlq::getStatus, ReservationDlqStatus.REPLAYED)
                .set(ReservationDlq::getReplayCount, replayCount + 1)) == 1;
if (!updated) {
    return rejected("死信记录已被并发重放", queryById(deadLetter.getId()));
}
```

**第 6 步**：真正投递（见 §7.2）。**返回 `null` 表示成功，返回 VO 表示失败**；**失败时台账不动**，管理员可以再点一次。

**第 7 步的 CAS 用 `replay_count` 做乐观锁**：

```sql
UPDATE tb_reservation_dlq
   SET status = 'REPLAYED', replay_count = ? + 1
 WHERE id = ? AND status = 'NEW' AND replay_count = ?
```

`.eq(ReplayCount, replayCount)` 比的是第 2 步读到的旧值。如果这期间别的管理员也重放过，`replay_count` 已经变了，影响 0 行 → `rejected("死信记录已被并发重放")`。**注意这时消息已经发出去了，台账却不改**——这是乐观锁失败时的取舍。

**例子里的对应值**（第 10 步）：`UPDATE ... SET status='REPLAYED', replay_count=1 WHERE id=1 AND status='NEW' AND replay_count=0` 影响 1 行 → `replayed = true` → Controller 走 `Result.ok(record)`，台账那行变成 `REPLAYED / 1`。

## 7.2 `publish`：消息重新发回**原队列**，不是直接调业务

```java
// :252-285
private ReservationDlqReplayVO publish(ReservationMessageDTO message, ReservationDlq deadLetter) {
    CorrelationData correlationData = new CorrelationData(String.valueOf(message.getReservationId()));
    try {
        rabbitTemplate.convertAndSend(
                RESERVATION_EXCHANGE, RESERVATION_CREATE_ROUTING_KEY, message, correlationData);
        CorrelationData.Confirm confirm = correlationData.getFuture().get(5, TimeUnit.SECONDS);
        if (!confirm.isAck()) {
            // 打 error 日志（dlqId / reservationId / confirm.getReason()）
            return rejected("REPLAY_CONFIRM_NACK", toVO(deadLetter));
        }
        if (correlationData.getReturnedMessage() != null) {
            return rejected("REPLAY_CONFIRM_RETURN", toVO(deadLetter));
        }
        return null;
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        return rejected("REPLAY_PUBLISH_UNKNOWN", toVO(deadLetter));   // 另一个 catch (Exception e) 同样返回它
    }
}
```

**关键结论**：重放**不是直接调用落库方法**，而是把消息**重新发回原来的交换机 `reservation.exchange` / 原 routing key `reservation.create`**，也就是回到 `reservation.create.queue`，**由消费者按正常路径消费**。

| 问题 | 答案 | 依据 |
|---|---|---|
| 发回哪里 | `reservation.exchange` + `reservation.create` | `:257-261` |
| 发回的是什么 | 由台账 payload 反序列化出来的 `ReservationMessageDTO`（**新消息，没有 `x-death` header**） | `:178` + `:257` |
| 会不会调业务方法 | 不会。消费者会按 §2.2 正常跑一遍 | — |
| 投递判定 | confirm ACK + 没有 returned message，两者都过才算成功 | `:262-273` |
| 超时 | 5 秒 | `:263` |

`mandatory` 是全局设的（`RabbitMQConfig:102` `rabbitTemplate.setMandatory(true)`），所以 `correlationData.getReturnedMessage()` 这个判定才有意义——routing key 打不到队列时消息会被退回。

**例子里的对应值**：`convertAndSend("reservation.exchange", "reservation.create", {645827360351847424,102,7,...})` → confirm ack = true、无 returned message → `publish` 返回 `null` → 消息落在 `reservation.create.queue`（第 11 步被消费者取走）。

## 7.3 `discard`：判定丢弃

```java
// :287-303
private ReservationDlqReplayVO discard(ReservationDlq deadLetter, int replayCount, String code, String reason) {
    String failureReason = appendDiscardReason(deadLetter.getFailureReason(), code);
    boolean updated = reservationDlqMapper.update(null,
            new LambdaUpdateWrapper<ReservationDlq>()
                    .eq(ReservationDlq::getId, deadLetter.getId())
                    .eq(ReservationDlq::getStatus, ReservationDlqStatus.NEW)
                    .eq(ReservationDlq::getReplayCount, replayCount)
                    .set(ReservationDlq::getStatus, ReservationDlqStatus.DISCARDED)
                    .set(ReservationDlq::getFailureReason, failureReason)) == 1;
    if (!updated) {
        return rejected("死信记录已被并发处理", queryById(deadLetter.getId()));
    }
    deadLetter.setStatus(ReservationDlqStatus.DISCARDED)
            .setFailureReason(failureReason);          // 让 toVO 里能带出新状态
    return rejected(reason, toVO(deadLetter));
}
```

和 `replay` 第 7 步同一个 CAS 形状（`status = NEW` + `replay_count` 乐观锁），只是目标是 `DISCARDED` 且**不动 `replay_count`**。

**`discard` 也返回 `replayed = false`**（它调的是 `rejected`）——HTTP 层看到的和「拒绝重放」一模一样：`Result.fail(reason)`。**区别只体现在台账的 `status` 变成了 `DISCARDED`。**

`appendDiscardReason`（`:309-319`）**先算 `suffix` 长度再截 `prefix`**：

```java
String marker = "DISCARD:" + code;
String suffix = " | " + marker;
int prefixLength = Math.min(prefix.length(), MAX_FAILURE_REASON_LENGTH - suffix.length());
return prefix.substring(0, prefixLength) + suffix;
```

这样 `" | DISCARD:XXX"` 一定是完整的，不会被 512 字符上限吞掉治理结论。结果形如 `LOCK_TIMEOUT | DISCARD:COMPENSATED`。`prefix` 为空时直接返回 `DISCARD:code`，不带 ` | `。

## 7.4 重放次数上限是 3，第 4 次会怎样

配置：`application.yaml:54` → `dlq-max-replay: 3`。**如果一条记录真的走到第 2 步**（`replay_count >= 3`）：

```
POST /reservation-dlq/{id}/replay
  → replay() 第 2 步 return rejected("已达到最大重放次数", toVO(deadLetter))
  → Controller：replayed=false → Result.fail("已达到最大重放次数")
  → HTTP 200，body {"success":false,"errorMsg":"已达到最大重放次数","data":null,"total":null}
  → 台账：status 保持 NEW，replay_count 不变
```

**但正常运行期走不到这一步**，这是个必须说清楚的源码事实：

- `replay_count` **只有第 7 步 +1**，而第 7 步同时把 `status` 改成 `REPLAYED`；
- 第 1 步在 `status != NEW` 时先拒绝。

所以「`status = NEW` 且 `replay_count >= 3`」这个组合**在运行期产生不了**：第一次成功重放后 `status` 就是 `REPLAYED`，再点只会被第 1 步以「不能重复重放」拒绝，永远数不到 4。生产代码里唯一往这张表插行的地方是 `recordDeadLetter`，它固定 `replay_count = 0`。

能造出这个组合的只有**直接改库**或**测试里手工插行**——`src/test/java/com/yanyuetong/ReservationDlqGovernanceTest.java:225-231` 就是直接 `insertDlq(..., 3, ReservationDlqStatus.NEW, ...)` 来覆盖第 2 步那个分支的（断言重放后 `status` 仍是 `NEW`）。

**所以「重放到第 4 次会怎样」的准确回答是**：按配置该返回 `Result.fail("已达到最大重放次数")` 且台账不变；但**实际上第 2 次就已经被「不能重复重放」挡住了**——一条台账记录最多成功重放一次。

---

# 八、重放成功之后，各存储变成什么

第 11 步（09:00:08.050）消费者第二次处理这条消息，这次拿到了锁。`persist` 依次做四件事：

| 步骤 | 结果 | 例子里的值 |
|---|---|---|
| ① `selectById(645827360351847424)` | 没有这行 | `null`，继续 |
| ② `selectCount(user=102, batch=7, status in RESERVED/COMPLETED/NO_SHOW)` | 0 | 继续 |
| ③ `UPDATE tb_reservation_batch SET remaining_quota = remaining_quota - 1 WHERE id = 7 AND remaining_quota > 0` | 1 行 | `4 → 3` |
| ④ `INSERT tb_reservation` | 1 行 | 见下表 |

| `id` | `user_id` | `batch_id` | `status` | `quota_released` | `create_time` |
|---|---|---|---|---|---|
| 645827360351847424 | 102 | 7 | `RESERVED` | `0` | 2026-10-07 09:00:01 |

**`create_time` 是 09:00:01 而不是 09:00:08**——它来自 `messageDTO.getCreateTime()`（原始提交时刻），这个值一路从消息体 → DLQ `payload` → 重放消息带了过来（§7.1 第 3 步）。列结构见 `phase7_reservation.sql:1-11` + `phase9_reservation_lifecycle.sql:2-10`。

然后 `markConfirmedSafely` 把账本置 `CONFIRMED`，`basicAck` 确认消息。

## 8.1 六个位置的最终状态（第 11 步之后）

| 位置 | 重放前 | 重放后 | 说明 |
|---|---|---|---|
| Redis `reservation:batch:quota:7` | `"3"` | **`"3"`（没动）** | 消费端和重放都不碰它 |
| Redis `reservation:batch:users:7` | `{101,102}` | **`{101,102}`（没动）** | 同上 |
| MySQL `tb_reservation_batch.remaining_quota` | 4 | **3** | 只在 `persist` 里扣，一共扣了这一次 |
| MySQL `tb_reservation` | 101 行 | **+645827360351847424 行** | `status = RESERVED`，`create_time = 09:00:01` |
| MySQL `tb_reservation_request` | `PUBLISHED` / `LOCK_TIMEOUT` | **`CONFIRMED` / `LOCK_TIMEOUT`** | `ReservationRequestServiceImpl.java:39-48` 的 `casStatus` **只 set status，不碰 `fail_reason`** |
| MySQL `tb_reservation_dlq` | `NEW` / 0 | **`REPLAYED` / 1** | 第 7 步 CAS |

**注意 `tb_reservation_request` 那行 `fail_reason` 永远停在 `LOCK_TIMEOUT`**——成功之后也没被清掉，这是审计线索（08 篇的对账也用 `casStatus` 保留它）。

## 8.2 会不会重复扣名额（本篇最值得看的一节）

**问题**：这条消息在进 DLQ 之前，Redis 名额**已经被 Lua 扣掉了**（§2.1）。重放会不会又扣一次？**答案：不会。两个名额计数器各自的账是清楚的。**

**① Redis 名额（`quota:7`）从头到尾只被扣过一次。**

- 扣它的唯一地方是 `submit` 里的 `reservationQuotaExecutor.tryAcquire`（`ReservationServiceImpl.java:116`），**在发消息之前**。
- 消费端 `onReservationMessage` 全程只做两件事：拿 Redisson 锁 + 落 MySQL，**一行 Redis 名额操作都没有**。
- 还名额的唯一地方是 `ReservationQuotaRollbackExecutor.rollback`。源码里它只有四个调用点：`ReservationServiceImpl:289`（submit 判定「确定未投递」）、`ReservationServiceImpl:163`（用户取消）、`ReservationReconcileServiceImpl:125`（对账补偿）、`ReservationReconcileServiceImpl:159`（取消归还重试）。**重放链路一次都不调。**
- 所以 `quota:7` 在第 3 步变 `"3"` 之后就再没动过。

**② MySQL 名额（`remaining_quota`）在被成功消费的那一刻才扣，一共扣一次。**

- 扣它的唯一地方是 `persist` 里那条 `remaining_quota = remaining_quota - 1`（`ReservationPersistenceServiceImpl:49-53`）。
- 失败那次（`LOCK_TIMEOUT`）**根本没进 `persist`**，没扣。
- 重放后进 `persist`，扣一次 `4 → 3`——**和「第一次就消费成功」的结果完全一样**。
- 而且 `persist` 前面有两道幂等闸门（同 id 已存在 / 同用户同批次已有活跃行 → 直接 `DUPLICATE` 且**不再扣名额**），所以就算这条消息被消费两次也不会多扣。

**③ 真正需要防的是「重放太晚」，但源码已经防住了。**

对账任务（08 篇）每 5 分钟跑一次（`reconcile-interval-ms: 300000`），把 `update_time` 早于 10 分钟前（`reconcile-threshold-ms: 600000`）且状态还是 `PRE_ACCEPTED/PUBLISHED/UNKNOWN` 的请求挑出来。**这条消息的账本是 `PUBLISHED`，09:00:03 写 `LOCK_TIMEOUT` 顺带把 `update_time` 推到了那一刻，所以从 09:10:03 起它就成了「陈旧请求」。**

对账发现 `tb_reservation` 里没有 645827360351847424 → **归还 Redis 名额 + 账本置 `COMPENSATED` / `fail_reason = 'RECONCILE_NO_RESERVATION'`**（`ReservationReconcileServiceImpl:124-135`）：

```
Redis  quota:7  "3" → "4"、users:7 {101,102} → {101}
账本   645827360351847424  PUBLISHED → COMPENSATED / RECONCILE_NO_RESERVATION
```

这时**再重放就会被第 5 步判 `COMPENSATED` 丢弃**——名额已经还回去了，如果还落库就变成「MySQL 有行（占用一个名额）+ Redis 名额已归还」，**这是超发**。所以变体 A 里那个 `discard` 是**保护**，不是缺陷。

**④ 反向的坑**：如果一直不重放、对账也还没跑到，那 Redis 那个名额就**一直压着**（`quota:7` 少 1，`users:7` 里 102 还在），直到对账跑成。**「死信台账记得住，Redis 名额不一定马上还得回来」是这条链路真实的时序差**，不是重放造成的。

---

# 九、当前实现的边界

- **一条台账记录最多成功重放一次**：第 7 步把 `status` 改成 `REPLAYED`，第 1 步就挡住了第二次；`dlq-max-replay: 3` 那个上限在正常运行期够不到（§7.4）。重放失败会新落一条台账行（新 `id`、`replay_count = 0`），想再试得去点那条新行。
- **重放有效期 ≈ 10 分钟**：对账一旦把账本置成 `COMPENSATED`，重放就被第 5 步挡掉（§8.2）。窗口由 `reconcile-threshold-ms` 决定，接口上没有提示「这条还剩多久能重放」。
- **DLQ 是终点，没有第二层**：`reservation.create.dlq` 没配 `x-dead-letter-exchange`，所以 `onDeadLetter` 落库失败时那条 `basicNack(tag, false, false)` 直接等于**永久丢弃**，唯一痕迹是那行 error 日志。
- **台账不做去重**：`tb_reservation_dlq` 没有唯一键，同一 `reservation_id` 可能有多行。`queryPage` 只按 `status` 过滤、按 `create_time DESC, id DESC` 排序，管理员要靠 `create_time`/`payload` 自己分辨哪行最新。

---

# 十、速查

## 10.1 `645827360351847424` 这条消息的完整一条

```
2026-10-07 09:00:01.000  学生 102 提交
  ReservationServiceImpl:110  INSERT tb_reservation_request (PRE_ACCEPTED)
  ReservationServiceImpl:116  EVAL reservation.lua → quota:7 "4"→"3"，users:7 +102
  ReservationServiceImpl:136  publish → reservation.exchange / reservation.create
                              → broker confirm ACK → 账本 CAS 成 PUBLISHED → HTTP 200
  │
09:00:01.070  消费者 onReservationMessage
  :46   getByRequestId(645827360351847424) → PUBLISHED（不是 COMPENSATED）
  :59   persistWithLock → lock:reservation:102 tryLock(2,10,SECONDS)
  :132  等满 2 秒没拿到 → return null
09:00:03.080  :63   recordFailReasonSafely(..., "LOCK_TIMEOUT")
                    UPDATE tb_reservation_request SET fail_reason='LOCK_TIMEOUT'
              :64   channel.basicNack(deliveryTag, false, false)      ← requeue=false
  │
09:00:03.100  broker：x-dead-letter-exchange    = "reservation.dlx"
                      x-dead-letter-routing-key = "reservation.create.dlq"
                    → 消息进 reservation.create.dlq，header 加 x-death[0].reason = "rejected"
  │
09:00:03.150  ReservationDlqConsumer.onDeadLetter(Message, Channel)   ← SimpleMessageConverter，不反序列化
  :48   extractXDeathReason → "rejected"（用不上，排第 3 优先级）
  :35   recordDeadLetter(body, "rejected")
          :93  extractReservationId(完整 payload) → 645827360351847424   ← 先解析后截断
          :95  storedPayload = 前 60000 字节
          :99  resolveFailureReason → 第 1 优先级命中账本 → "LOCK_TIMEOUT"
          :104-110 new ReservationDlq(...).setReplayCount(0).setStatus(NEW) → INSERT tb_reservation_dlq (id=1)
  :45   basicAck
  │
09:00:08.000  李老师（uid 2，LAB_ADMIN）POST /reservation-dlq/1/replay
  :165  status == NEW ✓        :173  replay_count(0) < maxReplay(3) ✓
  :178  parseReplayablePayload → 三个 id 都是整型 ✓
  :185  tb_reservation 无该 id ✓     :194  账本 PUBLISHED（不是 COMPENSATED）✓
  :257  convertAndSend("reservation.exchange", "reservation.create", message)
        → confirm ack ✓，无 returned message → 返回 null
  :212  UPDATE tb_reservation_dlq SET status='REPLAYED', replay_count=1
         WHERE id=1 AND status='NEW' AND replay_count=0  → 1 行
         → replayed=true → Result.ok(record)
  │
09:00:08.050  消费者第二次处理
  :46   账本 PUBLISHED ✓     :59   persistWithLock → 这次拿到锁
          persist ① selectById → null       ② selectCount → 0
                  ③ UPDATE tb_reservation_batch SET remaining_quota=remaining_quota-1
                       WHERE id=7 AND remaining_quota>0    → 4→3
                  ④ INSERT tb_reservation (645827360351847424, 102, 7, RESERVED)
                     create_time = 2026-10-07 09:00:01（来自消息里的 createTime）
                  → PERSISTED
  :70   markConfirmedSafely → 账本 CAS 成 CONFIRMED（fail_reason 仍是 'LOCK_TIMEOUT'）
  :71   basicAck
  │
最终：Redis quota:7 = "3"（没动）  users:7 = {101,102}（没动）
      MySQL remaining_quota = 3   tb_reservation 2 行   tb_reservation_dlq 1 行 REPLAYED/1
```

## 10.2 交换机 / 队列 / routing key

| 角色 | 值 |
|---|---|
| 原交换机 | `reservation.exchange` |
| 原 routing key | `reservation.create` |
| 原队列 | `reservation.create.queue`（带 `x-dead-letter-exchange` = `reservation.dlx`、`x-dead-letter-routing-key` = `reservation.create.dlq`） |
| 死信交换机 | `reservation.dlx` |
| 死信队列 | `reservation.create.dlq` |
| 死信 routing key | `reservation.create.dlq`（和队列名同串） |

## 10.3 台账状态与重放出口

| `status` | 谁写的 | 含义 |
|---|---|---|
| `NEW` | `recordDeadLetter`（`:109`） | 刚落库，可被 `replay` |
| `REPLAYED` | `replay` 第 7 步（`:217`） | 重放投递成功，`replay_count + 1` |
| `DISCARDED` | `discard`（`:295`） | 预检不通过，`replay_count` 不动 |

| `replay` 出口 | 条件 | 返回 | 台账 |
|---|---|---|---|
| 1 | 记录不存在 | `rejected("死信记录不存在")` | 不变 |
| 1 | `status != NEW` | `rejected("死信记录已处理，不能重复重放")` | 不变 |
| 2 | `replay_count >= 3` | `rejected("已达到最大重放次数")` | **保持 `NEW`** |
| 3 | payload 三个 id 不全 | `discard("PAYLOAD_NOT_REPLAYABLE")` | → `DISCARDED` |
| 4 | `tb_reservation` 已有该 id | `discard("ALREADY_PERSISTED")` | → `DISCARDED` |
| 5 | 账本已 `COMPENSATED` | `discard("COMPENSATED")` | → `DISCARDED` |
| 6 | confirm NACK / message 被退回 / 投递超时中断 | `rejected("REPLAY_CONFIRM_NACK" / "REPLAY_CONFIRM_RETURN" / "REPLAY_PUBLISH_UNKNOWN")` | 不变 |
| 7 | CAS 影响 0 行 | `rejected("死信记录已被并发重放")` | 不变（**但消息已发出**） |
| 7 | CAS 影响 1 行 | **`replayed = true`** | → `REPLAYED` |

**`rejected` 与 `discard` 在接口上都返回 `replayed = false` → `Result.fail(reason)`（HTTP 200）**，差别只在台账状态。

## 10.4 `fail_reason` / `failure_reason` 的取值

| 值 | 谁写的 | 触发 |
|---|---|---|
| `LOCK_TIMEOUT` | 消费端 `:63` | `persistWithLock` 拿锁超时 |
| `QUOTA_CONFLICT` | 消费端 `:74` | MySQL 扣名额影响 0 行 |
| `PERSIST_EXCEPTION:{类简名}` | 消费端 `:92-94` | `persist` 抛任何异常 |
| `RECONCILE_NO_RESERVATION` | 对账 `:129` | 账本陈旧且 `tb_reservation` 无行 |
| `PAYLOAD_UNPARSEABLE` | DLQ 落库 `:363` | `payload` 解析不出 `reservationId` |
| `x-death:{reason}` | DLQ 落库 `:368` | 账本给不出原因，退回 broker 的 `rejected` 等 |
| `{原值} \| DISCARD:{code}` | `discard` `:309-319` | 重放预检不通过 |

## 10.5 配置与常量

| 键/常量 | 值 | 用途 |
|---|---|---|
| `yanyuetong.reservation.dlq-max-replay` | `3` | `replay` 第 2 步的上限 |
| `yanyuetong.reservation.reconcile-threshold-ms` | `600000` | 账本「陈旧」判据 = 10 分钟（决定重放窗口） |
| `yanyuetong.reservation.reconcile-interval-ms` | `300000` | 对账固定间隔 5 分钟 |
| `spring.rabbitmq.listener.simple.retry.enabled` | `false` | **消费端不自动重试，一次失败就 NACK 进死信** |
| `spring.rabbitmq.listener.simple.prefetch` | `1` | 每个消费者一次只预取一条 |
| `MAX_PAYLOAD_BYTES` | `60000` | `payload` 落库字节上限 |
| `MAX_FAILURE_REASON_LENGTH` | `512` | `failure_reason` 字符上限 |
| `SystemConstants.DEFAULT_PAGE_SIZE` | `5` | `queryPage` 固定页大小 |
