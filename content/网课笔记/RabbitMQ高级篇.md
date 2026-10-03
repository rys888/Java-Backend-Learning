
```
基础篇遗留问题：MQ 通知失败 → 支付流水已成功、订单状态却未支付 → 数据不一致
        ↓ 目标
至少被消费者处理 1 次（extended: 最终一致性，允许重复 → 必须幂等）
        ↓ 拆成三段加固
① 发送方可靠性：重试机制 → Publisher Confirm / Return
② MQ   可靠性：交换机/队列/消息持久化 → LazyQueue
③ 消费方可靠性：ACK 模式 → 失败重试 → 失败处理策略 → 业务幂等
        ↓ 还是可能丢
兜底方案：交易服务定时任务主动查询支付状态（最终一致性）
        ↓ 另一条业务线
延迟消息：死信交换机 + TTL  /  Delayed Message 插件
        ↓ 落地
下单后第 10s/20s/30s/45s/60s/… 分次探测支付状态，未支付则关单释放库存
```

---

# 一、消息丢失的可能性分析

消息从生产者到消费者，每一步都可能丢：

```
Producer ──① ──→ Exchange ──② ──→ Queue ──③ ──→ Consumer
```

| 阶段 | 具体场景 |
|---|---|
| 发送时丢失 | ① 连接 MQ 失败；② 到达 MQ 后未找到 `Exchange`；③ 到达 `Exchange` 后未找到合适的 `Queue`；④ 到达 MQ 后处理消息的进程异常 |
| MQ 导致丢失 | 消息已保存到队列，尚未消费就突然宕机 |
| 消费时丢失 | 接收后尚未处理突然宕机；处理过程中抛出异常 |


---

# 二、发送者的可靠性

## 2.1 生产者重试机制

场景：发送消息时网络故障，与 MQ 的连接中断。

配置（`publisher` 模块 `application.yaml`）：

```yaml
spring:
  rabbitmq:
    connection-timeout: 1s # 设置MQ的连接超时时间
    template:
      retry:
        enabled: true # 开启超时重试机制
        initial-interval: 1000ms # 失败后的初始等待时间
        multiplier: 1 # 下次等待时长 = initial-interval * multiplier
        max-attempts: 3 # 最大重试次数
```

验证方式：`docker stop mq` 后发消息，观察每隔 1 秒重试 1 次、共 3 次。

> ⚠️ **注意**：SpringAMQP 的重试是**阻塞式**的。重试等待期间当前线程被占住。对性能敏感的业务建议禁用；必须用时合理配置等待时长和次数，或把发送逻辑放到异步线程里。

## 2.2 生产者确认机制

网络顺畅时基本不会丢消息，但少数情况仍会丢：

- MQ 内部处理消息的进程发生异常
- 消息到达 MQ 后未找到 `Exchange`
- 到达 `Exchange` 后未找到合适的 `Queue`，无法路由

RabbitMQ 提供两套机制：**Publisher Confirm** 和 **Publisher Return**，MQ 根据处理情况返回不同**回执**。

| 情况 | 回执 |
|---|---|
| 投递到 MQ 但**路由失败** | 通过 **Publisher Return** 返回异常信息，**同时返回 ack**（代表投递成功，只是没人收） |
| 临时消息投递到 MQ 且入队成功 | **ACK** |
| 持久消息投递到 MQ 并入队完成持久化 | **ACK** |
| 其它情况 | **NACK**（投递失败） |

`ack`/`nack` 属于 Publisher Confirm；`return` 属于 Publisher Return。**两者默认都关闭**。

### 2.2.1 开启确认

```yaml
spring:
  rabbitmq:
    publisher-confirm-type: correlated # 开启 publisher confirm 机制并设置 confirm 类型
    publisher-returns: true # 开启 publisher return 机制
```

`publisher-confirm-type` 三种模式：

| 值 | 含义 |
|---|---|
| `none` | 关闭 confirm |
| `simple` | 同步阻塞等待 MQ 回执 |
| `correlated` | **MQ 异步回调返回回执（推荐）** |

### 2.2.2 定义 ReturnCallback（全局一次）

每个 `RabbitTemplate` 只能配置**一个** `ReturnCallback`，所以在配置类里统一设置：

```java
@Slf4j
@AllArgsConstructor
@Configuration
public class MqConfig {
    private final RabbitTemplate rabbitTemplate;

    @PostConstruct
    public void init(){
        rabbitTemplate.setReturnsCallback(new RabbitTemplate.ReturnsCallback() {
            @Override
            public void returnedMessage(ReturnedMessage returned) {
                log.error("触发return callback,");
                log.debug("exchange: {}", returned.getExchange());
                log.debug("routingKey: {}", returned.getRoutingKey());
                log.debug("message: {}", returned.getMessage());
                log.debug("replyCode: {}", returned.getReplyCode());
                log.debug("replyText: {}", returned.getReplyText());
            }
        });
    }
}
```

关键点：`@PostConstruct` 保证在 `RabbitTemplate` 装配完成后立刻挂上回调。

### 2.2.3 定义 ConfirmCallback（每条消息一次）

每条消息的处理逻辑不同，因此 `ConfirmCallback` 在发消息时逐条定义——多传一个 `CorrelationData` 参数。

`CorrelationData` 两个核心内容：

- `id`：消息唯一标识，MQ 靠它区分不同消息的回执，避免混淆
- `SettableListenableFuture`：回执结果的 Future，可提前添加回调

```java
@Test
void testPublisherConfirm() {
    // 1.创建CorrelationData
    CorrelationData cd = new CorrelationData();
    // 2.给Future添加ConfirmCallback
    cd.getFuture().addCallback(new ListenableFutureCallback<CorrelationData.Confirm>() {
        @Override
        public void onFailure(Throwable ex) {
            // 2.1.Future发生异常时的处理逻辑，基本不会触发
            log.error("send message fail", ex);
        }
        @Override
        public void onSuccess(CorrelationData.Confirm result) {
            // 2.2.Future接收到回执的处理逻辑，参数中的result就是回执内容
            if(result.isAck()){ // true代表ack回执，false代表nack回执
                log.debug("发送消息成功，收到 ack!");
            }else{ // result.getReason() 返回nack时的异常描述
                log.error("发送消息失败，收到 nack, reason : {}", result.getReason());
            }
        }
    });
    // 3.发送消息
    rabbitTemplate.convertAndSend("hmall.direct", "q", "hello", cd);
}
```

### 2.2.4 三种测试结果（务必记住这张对应关系）

| 场景 | return callback | confirm 回执 |
|---|---|---|
| RoutingKey 错误（路由失败） | ✅ 触发 | ✅ **ack** |
| RoutingKey 正确 | ❌ 不触发 | ✅ ack |
| 交换机名称也错误 | ❌ 不触发 | ❌ **nack** |

**结论：`ack` 只代表"MQ 收到了"，不代表"消费者能收到"。想知道路由是否成功必须看 Return。**

---

# 三、MQ 的可靠性

## 3.1 数据持久化

默认情况下 MQ 数据都在内存，重启即消失。三件套都要持久化：

| 对象 | 控制台参数 | 说明 |
|---|---|---|
| 交换机 | `Durability` = `Durable` | `Transient` 即临时模式 |
| 队列 | `Durability` = `Durable` | 队列还有其他参数（如 Lazy 模式） |
| 消息 | `properties` 中设置 | 控制台发消息时配置 |

> ⚠️ **说明**：开启持久化 + 生产者确认后，MQ 会**在消息持久化以后才发送 ACK**，进一步保证可靠性。
> 但出于性能考虑，消息不是逐条落库，而是**每隔一段时间（约 100ms）批量持久化**，这会让 ACK 有延迟。**因此建议生产者确认全部采用异步方式。**

## 3.2 LazyQueue（惰性队列）

默认 RabbitMQ 把消息放内存以降低收发延迟，但以下情况会导致积压：

- 消费者宕机或网络故障
- 消息发送量激增，超过消费速度
- 消费者处理业务阻塞

积压后内存占用升高，触及内存预警上限时 RabbitMQ 会把内存消息刷到磁盘，这个行为叫 **PageOut**。PageOut 耗时且会**阻塞队列进程**，期间 RabbitMQ 不再处理新消息，生产者的所有请求都被阻塞。

3.6.0 起新增 Lazy Queues：

- 接收消息后**直接存入磁盘**而非内存
- 消费者要消费时才从磁盘读取加载到内存（懒加载）
- 支持数百万条消息存储

**3.12 版本之后 LazyQueue 已成为所有队列的默认格式**，官方推荐升级到 3.12+ 或把所有队列设为 LazyQueue。

### 3.2.1 控制台配置

添加队列时加参数 `x-queue-mode=lazy`。

> 课程文档此处写作 `x-queue-mod=lazy`（漏了 `e`），是笔误；**实际参数名是 `x-queue-mode`**。文档中代码注解那段写的就是 `x-queue-mode`，可对照。

### 3.2.2 代码配置（`@Bean`）

```java
@Bean
public Queue lazyQueue(){
    return QueueBuilder
            .durable("lazy.queue")
            .lazy() // 开启Lazy模式
            .build();
}
```

### 3.2.3 代码配置（注解）

```java
@RabbitListener(queuesToDeclare = @Queue(
        name = "lazy.queue",
        durable = "true",
        arguments = @Argument(name = "x-queue-mode", value = "lazy")
))
public void listenLazyQueue(String msg){
    log.info("接收到 lazy.queue的消息：{}", msg);
}
```

---

# 四、消费者的可靠性

消息投递给消费者 ≠ 被正确消费。可能出现的故障：

- 投递过程网络故障
- 消费者接收后突然宕机
- 消费者接收后处理异常

所以 RabbitMQ 必须知道消费者的处理状态，失败才能重投。**它怎么知道？靠消费者回执。**

## 4.1 消费者确认机制（Consumer Acknowledgement）

消费者处理完消息后向 RabbitMQ 发回执，三种取值：

| 回执 | 含义 | MQ 动作 |
|---|---|---|
| `ack` | 成功处理 | 从队列删除该消息 |
| `nack` | 处理失败 | **再次投递**消息 |
| `reject` | 处理失败并拒绝 | **从队列删除**该消息 |

`reject` 用得少（除非消息格式有问题，那是开发问题）。多数情况把业务代码用 `try/catch` 包住：成功返回 `ack`，失败返回 `nack`。

回执处理代码统一，因此 **SpringAMQP 帮我们实现了**，通过配置选择 ACK 模式：

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        acknowledge-mode: none # 或 manual / auto
```

| 模式 | 行为 | 评价 |
|---|---|---|
| `none` | 投递给消费者后**立刻 ack**，消息立即从 MQ 删除 | 非常不安全，不建议使用 |
| `manual` | 手动模式，自己在业务代码里调 API 发 `ack`/`reject` | 存在业务入侵，但更灵活 |
| `auto` | SpringAMQP 用 **AOP 环绕增强**消息处理逻辑：正常执行返回 `ack`；业务异常返回 `nack`；消息处理/校验异常返回 `reject` | **推荐** |


## 4.2 失败重试机制

问题：消费者异常后消息会不断 `requeue` 回队列再重投，一直失败就一直循环。极端情况下消息处理量飙升，给 MQ 带来无谓压力。

Spring 提供**消费者失败重试**：异常时先做**本地重试**，而不是无限制 requeue 回 MQ。

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        retry:
          enabled: true # 开启消费者失败重试
          initial-interval: 1000ms # 初始失败等待时长 1 秒
          multiplier: 1 # 下次等待时长 = multiplier * last-interval
          max-attempts: 3 # 最大重试次数
          stateless: true # true 无状态；false 有状态。业务含事务时改为 false
```

测试结果：

- 失败后消息**没有**重新回到 MQ 无限投递，而是在**本地重试 3 次**
- 重试 3 次后抛出 `AmqpRejectAndDontRequeueException`，控制台显示消息**被删除**——说明最终 SpringAMQP 返回的是 `reject`

**结论：**

- 开启本地重试后，抛异常不会 requeue 到队列，而是本地重试
- 达到最大次数后，Spring 返回 `reject`，**消息被丢弃**

> `stateless: true` 表示重试不携带上一次的状态（无状态重试）；如果业务里有事务，必须设为 `false`，否则重试会在事务外面执行。

## 4.3 失败处理策略（重试耗尽后怎么办）

本地重试耗尽就丢消息，对可靠性要求高的业务显然不合适。Spring 允许自定义**重试次数耗尽后**的处理策略，由 `MessageRecoverer` 接口定义，3 个实现：

| 实现 | 行为 |
|---|---|
| `RejectAndDontRequeueRecoverer` | 直接 `reject`，丢弃消息（**默认**） |
| `ImmediateRequeueMessageRecoverer` | 返回 `nack`，消息重新入队 |
| `RepublishMessageRecoverer` | 把失败消息**投递到指定交换机**（推荐，最优雅） |

`RepublishMessageRecoverer` 的思路：失败消息投递到一个专门存放异常消息的队列，后续**人工集中处理**。

1）定义处理失败消息的交换机和队列：

```java
@Bean
public DirectExchange errorMessageExchange(){
    return new DirectExchange("error.direct");
}
@Bean
public Queue errorQueue(){
    return new Queue("error.queue", true);
}
@Bean
public Binding errorBinding(Queue errorQueue, DirectExchange errorMessageExchange){
    return BindingBuilder.bind(errorQueue).to(errorMessageExchange).with("error");
}
```

2）定义 `RepublishMessageRecoverer`，关联队列和交换机：

```java
@Bean
public MessageRecoverer republishMessageRecoverer(RabbitTemplate rabbitTemplate){
    return new RepublishMessageRecoverer(rabbitTemplate, "error.direct", "error");
}
```

完整配置类（注意类上的条件注解——只在开启重试时才装配这套错误处理）：

```java
@Configuration
@ConditionalOnProperty(name = "spring.rabbitmq.listener.simple.retry.enabled", havingValue = "true")
public class ErrorMessageConfig {
    @Bean
    public DirectExchange errorMessageExchange(){
        return new DirectExchange("error.direct");
    }
    @Bean
    public Queue errorQueue(){
        return new Queue("error.queue", true);
    }
    @Bean
    public Binding errorBinding(Queue errorQueue, DirectExchange errorMessageExchange){
        return BindingBuilder.bind(errorQueue).to(errorMessageExchange).with("error");
    }
    @Bean
    public MessageRecoverer republishMessageRecoverer(RabbitTemplate rabbitTemplate){
        return new RepublishMessageRecoverer(rabbitTemplate, "error.direct", "error");
    }
}
```

## 4.4 业务幂等性

### 4.4.1 什么是幂等

数学定义：`f(x) = f(f(x))`，例如求绝对值函数。

程序中：**同一个业务，执行一次或多次对业务状态的影响是一致的。**

天然幂等的操作：根据 id 删除数据、查询数据、新增数据。
**不幂等**的典型：

- 取消订单恢复库存——多次恢复导致库存重复增加
- 退款业务——重复退款造成经济损失

重复执行的现实来源：页面卡顿频繁刷新导致表单重复提交、服务间调用重试、**MQ 消息的重复投递**。

**重复消费的经典事故序列**（务必理解这一段）：

1. 用户刚支付完成，消息投递到交易服务，交易服务把订单改为**已支付**
2. 因网络故障生产者没拿到确认，隔一段时间**重新投递**
3. 在新消息被消费之前，用户选择了**退款**，订单状态改为已退款
4. 退款完成后，新投递的消息才被消费，订单状态**又被改成已支付** → 业务异常

因此必须保证消息处理的幂等性。两种方案：

### 4.4.2 方案一：唯一消息 ID

思路：

1. 每条消息生成唯一 id，随消息投递给消费者
2. 消费者处理业务成功后把消息 id 保存到数据库
3. 下次收到相同消息，先查数据库判断是否存在，存在则放弃处理

实现很简单——SpringAMQP 的 `MessageConverter` **自带 MessageID 功能**，开启即可。以 Jackson 转换器为例：

```java
@Bean
public MessageConverter messageConverter(){
    // 1.定义消息转换器
    Jackson2JsonMessageConverter jjmc = new Jackson2JsonMessageConverter();
    // 2.配置自动创建消息id，用于识别不同消息，也可以在业务中基于ID判断是否是重复消息
    jjmc.setCreateMessageIds(true);
    return jjmc;
}
```

> 本工程 `hm-common/src/main/java/com/hmall/common/config/MqConfig.java:17` 只 `new Jackson2JsonMessageConverter()`，**没有开 `setCreateMessageIds(true)`**，所以当前项目走的是方案二。

### 4.4.3 方案二：业务状态判断（推荐）

基于业务本身的逻辑或状态判断是否重复。当前案例的业务是"把订单从未支付改为已支付"，那么**执行时判断订单状态是否为未支付**，不是则说明已处理过。

第一版（"先查后改"）：

```java
@Override
public void markOrderPaySuccess(Long orderId) {
    // 1.查询订单
    Order old = getById(orderId);
    // 2.判断订单状态
    if (old == null || old.getStatus() != 1) {
        // 订单不存在或者订单状态不是1，放弃处理
        return;
    }
    // 3.尝试更新订单
    Order order = new Order();
    order.setId(orderId);
    order.setStatus(2);
    order.setPayTime(LocalDateTime.now());
    updateById(order);
}
```

问题：**判断和更新是两步动作，极小概率下存在线程安全问题**（两个线程同时通过判断）。

第二版（合并成一条 SQL，**最优解**）：

```java
@Override
public void markOrderPaySuccess(Long orderId) {
    // UPDATE `order` SET status = ? , pay_time = ? WHERE id = ? AND status = 1
    lambdaUpdate()
            .set(Order::getStatus, 2)
            .set(Order::getPayTime, LocalDateTime.now())
            .eq(Order::getId, orderId)
            .eq(Order::getStatus, 1)
            .update();
}
```

等价的 SQL：

```sql
UPDATE `order` SET status = ? , pay_time = ? WHERE id = ? AND status = 1
```

**核心思想：把幂等判断下推到 `WHERE` 条件里。** `status = 1` 在 where 中充当乐观锁，条件不符则匹配不到数据，SQL 直接不执行。这是一条语句内的原子判断，天然线程安全。

> 对比：`OrderServiceImpl.markPayOrderSuccess`（pay-service）用 `.in(status, NOT_COMMIT, WAIT_BUYER_PAY)` 做同样的乐观锁，思路一致。

## 4.5 兜底方案

各种机制都用上了，也不能保证 100% 可靠。万一 MQ 通知真失败了呢？

**思想很简单：既然 MQ 通知不一定到，那么交易服务就自己主动去查询支付状态。** 即便支付服务的 MQ 通知失败，依然能通过主动查询保证订单状态一致。

难点：交易服务不知道用户什么时候支付。查太早（用户正在支付中）状态不对。

结论：**用定时任务定期查询**，例如每隔 20 秒查一次，判断支付状态，发现已支付就立刻把订单更新为已支付。

### 支付服务与交易服务订单状态一致性的完整答案

1. 支付服务在用户支付成功后，利用 MQ 消息通知交易服务，完成订单状态同步
2. 为保证 MQ 消息可靠性，采用**生产者确认、消费者确认、消费者失败重试**等策略
3. 最后在交易服务设置**定时任务**定期查询订单支付状态

→ 即便 MQ 通知失败，还有定时任务兜底，确保订单支付状态的**最终一致性**。

---

# 五、延迟消息

## 5.1 为什么需要延迟消息

电商场景：库存有限（电影院购票、高铁购票），下单立即扣减库存锁定资源。但用户若一直不付款，就会一直占用库存，商户利益受损。

所以：**对超过一定时间未支付的订单，应立刻取消订单并释放库存。** 例如超时 30 分钟，则在下单后第 30 分钟检查支付状态。

这种"一段时间以后才执行的任务"称为**延迟任务**。RabbitMQ 有两种实现方案：

- 死信交换机 + TTL
- 延迟消息插件

## 5.2 方案一：死信交换机 + TTL

### 5.2.1 什么是死信

队列中的消息满足下列情况**之一**，就成为**死信（dead letter）**：

- 消费者用 `basic.reject` 或 `basic.nack` 声明消费失败，且 `requeue` 参数设为 `false`
- 消息是一个过期消息，超时无人消费
- 要投递的队列**消息满了**，无法投递

如果队列通过 `dead-letter-exchange` 属性指定了一个交换机，队列中的死信就投递到该交换机——这个交换机叫**死信交换机（Dead Letter Exchange）**。若有队列与它绑定，死信最终进入那个队列。

死信交换机的三个作用：

1. 收集因处理失败而被拒绝的消息
2. 收集因队列满了而被拒绝的消息
3. 收集因 TTL（有效期）到期的消息

### 5.2.2 用 TTL + DLX 实现延迟

构造：

```
publisher → ttl.fanout ──→ ttl.queue（无消费者，设了死信交换机 hmall.direct）
                                    ↓ TTL 到期变死信，沿用原 RoutingKey
                              hmall.direct ──binding(blue)──→ direct.queue1 → consumer
```

流程（发送一条 RoutingKey=`blue`、TTL=5000ms 的消息）：

1. 消息进入 `ttl.queue`，由于没有消费者，无人消费
2. 5 秒后消息有效期到期，成为死信
3. 死信被重新投递到死信交换机 `hmall.direct`，**沿用之前的 RoutingKey `blue`**
4. `direct.queue1` 与 `hmall.direct` 绑定 key 是 `blue`，消息成功路由进队列
5. 消费者此时才收到消息——**已经是 5 秒以后**

> ⚠️ **注意**：尽管 `ttl.fanout` 不需要 RoutingKey，但消息变成死信投递到死信交换机时**会沿用之前的 RoutingKey**，只有这样才能让 `hmall.direct` 正确路由。

### 5.2.3 死信方案的致命缺陷（必考）

> RabbitMQ 的消息过期是**基于追溯方式**实现的：消息 TTL 到期后**不一定会被移除或投递到死信交换机**，而是**在消息恰好处于队首时才会被处理**。

因此**当队列中消息堆积很多时，过期消息可能不会被按时处理，设置的 TTL 时间不一定准确**。这是死信方案不如插件方案的根本原因（DLX 的队首阻塞问题）。

## 5.3 方案二：DelayExchange 插件

### 5.3.1 声明延迟交换机

基于注解（推荐，简洁）：

```java
@RabbitListener(bindings = @QueueBinding(
        value = @Queue(name = "delay.queue", durable = "true"),
        exchange = @Exchange(name = "delay.direct", delayed = "true"),
        key = "delay"
))
public void listenDelayMessage(String msg){
    log.info("接收到delay.queue的延迟消息：{}", msg);
}
```

基于 `@Bean`：

```java
@Slf4j
@Configuration
public class DelayExchangeConfig {

    @Bean
    public DirectExchange delayExchange(){
        return ExchangeBuilder
                .directExchange("delay.direct") // 指定交换机类型和名称
                .delayed() // 设置 delay 属性为 true
                .durable(true) // 持久化
                .build();
    }

    @Bean
    public Queue delayedQueue(){
        return new Queue("delay.queue");
    }

    @Bean
    public Binding delayQueueBinding(){
        return BindingBuilder.bind(delayedQueue()).to(delayExchange()).with("delay");
    }
}
```

**关键点：交换机必须带 `delayed=true` 属性，这是普通 direct 交换机和延迟交换机的唯一区别。**

### 5.3.3 发送延迟消息

必须通过消息头 `x-delay` 设定延迟时间，SpringAMQP 封装为 `setDelay()`：

```java
@Test
void testPublisherDelayMessage() {
    // 1.创建消息
    String message = "hello, delayed message";
    // 2.发送消息，利用消息后置处理器添加消息头
    rabbitTemplate.convertAndSend("delay.direct", "delay", message, new MessagePostProcessor() {
        @Override
        public Message postProcessMessage(Message message) throws AmqpException {
            // 添加延迟消息属性
            message.getMessageProperties().setDelay(5000);
            return message;
        }
    });
}
```

> ⚠️ **注意**：延迟消息插件内部维护一个本地数据库表，并用 Erlang Timers 功能实现计时。**如果延迟时间设置较长，堆积的延迟消息会非常多，带来较大 CPU 开销，且延迟时间存在误差。因此不建议设置延迟时间过长的延迟消息。**

## 5.4 两种方案对比

| | 死信交换机 + TTL | DelayExchange 插件 |
|---|---|---|
| 是否需装插件 | 否 | 是（版本需匹配） |
| 实现复杂度 | 高（要造一个无消费者队列 + 绑定 + 死信交换机） | 低（交换机加 `delayed=true`，发消息带 `x-delay`） |
| 时间准确性 | **差**——队列有堆积时只在队首消息到期时才处理，TTL 不准确 | 较好（仍有误差，且长延迟耗 CPU） |
| 适用场景 | 简单、消息量小、精度要求不高 | 推荐方案，尤其是"多次间隔探测"这类场景 |

---

# 六、落地：交易服务的订单状态同步

## 6.1 朴素思路与其问题

假如超时支付时间是 30 分钟，理论上下单时发一条延迟 30 分钟的消息，收到消息时校验并关闭订单。

问题：**大多数用户会在 1 分钟内完成支付，而消息要在 MQ 里白白停留 30 分钟，额外消耗 MQ 资源。**

## 6.2 优化思路：分多次探测

在下单后第 **10 秒、20 秒、30 秒、45 秒、60 秒、1 分 30 秒、2 分、…、30 分** 分别设置延迟消息；一旦提前发现订单已支付，后续检测即可取消。这样能有效避免 MQ 资源浪费。

对应工程代码里的延迟序列（`trade-service/.../OrderServiceImpl.java:100`）：

```java
MultiDelayMessage<Long> msg = MultiDelayMessage.of(
        order.getId(), 10000L, 10000L, 10000L, 15000L, 15000L, 30000L, 30000L);
```

累加后是 10s / 20s / 30s / 45s / 60s / 90s / 120s —— 与文档思路一致（后面还有兜底的定时任务接续到 30 分钟）。

## 6.3 消息载体：MultiDelayMessage

要多次发送延迟消息，需要先定义记录延迟时间的消息体。出于通用性考虑，定义到 `hm-common` 模块：

```java
@Data
public class MultiDelayMessage<T> {
    /**
     * 消息体
     */
    private T data;
    /**
     * 记录延迟时间的集合
     */
    private List<Long> delayMillis;

    public MultiDelayMessage(T data, List<Long> delayMillis) {
        this.data = data;
        this.delayMillis = delayMillis;
    }
    public static <T> MultiDelayMessage<T> of(T data, Long ... delayMillis){
        return new MultiDelayMessage<>(data, CollUtils.newArrayList(delayMillis));
    }

    /**
     * 获取并移除下一个延迟时间
     * @return 队列中的第一个延迟时间
     */
    public Long removeNextDelay(){
        return delayMillis.remove(0);
    }

    /**
     * 是否还有下一个延迟时间
     */
    public boolean hasNextDelay(){
        return !delayMillis.isEmpty();
    }
}
```

**设计精妙之处：延迟时间列表随消息一起传递，消费者每消费一次就 `removeNextDelay()` 弹出一个，再把剩余列表原样发回 MQ。**这样一条消息就串起了整条"多次探测"的链路，无需服务器记录状态。
