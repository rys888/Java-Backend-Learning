
## 1. 业务场景与为什么要用消息队列

### 1.1 场景：优惠券秒杀下单

入口是 `VoucherOrderController` 里的一个接口：

```java
@PostMapping("seckill/{id}")
public Result seckillVoucher(@PathVariable("id") Long voucherId) {
    return voucherOrderService.seckillVoucher(voucherId);
}
```

秒杀券是店主通过 `POST /voucher/seckill` 创建的。`VoucherServiceImpl.addSeckillVoucher()` 在保存完数据库之后，会把库存预热到 Redis：

```java
stringRedisTemplate.opsForValue().set(SECKILL_STOCK_KEY + voucher.getId(), voucher.getStock().toString());
```

`SECKILL_STOCK_KEY` 就是 `seckill:stock:`。这个预热动作是后面 Lua 脚本能工作的前提。

### 1.2 改造后的完整时序

一次成功的秒杀请求会走这么一条链路：

```
用户点击「立即抢购」
   │
   ▼
POST /voucher-order/seckill/{voucherId}
   │
   ▼
VoucherOrderServiceImpl.seckillVoucher()
   │  ① RedisIdWorker 生成全局唯一订单号 orderId
   │  ② 执行 seckill.lua（在 Redis 里原子完成三件事）
   │       ├─ 库存 <= 0 ？返回 1 → Result.fail("库存不足")
   │       ├─ 用户已在 orderKey 集合里？返回 2 → Result.fail("不能重复下单")
   │       └─ 否则 库存 -1、sadd 用户 → 返回 0
   │
   ├─ r != 0 → 直接返回失败，到此结束，不产生任何消息
   │
   ▼  ③ r == 0，组装 VoucherOrder，用 RabbitTemplate 发消息
rabbitTemplate.convertAndSend(exchange, routingKey, voucherOrder, correlationData)
   │  ④ 同步等待 Broker 确认（最多 5 秒）
   │       ├─ 未确认 / 无法路由 → 回滚 Redis → Result.fail("下单失败，请重试")
   │       └─ 确认成功 → 继续
   ▼
返回 Result.ok(orderId)  ← 用户此刻已经拿到订单号了
   │
   │  ~~~~~~~~~~ 以下是异步的，和用户请求无关 ~~~~~~~~~~
   ▼
RabbitMQ: seckill.order.exchange --(seckill.order)--> seckill.order.queue
   │
   ▼
@RabbitListener 消费者 onOrderMessage()
   │  ⑤ Redisson 加锁 lock:order:{userId}
   │  ⑥ 查 tb_voucher_order 是否已有该用户该券的订单 → 有则幂等 ACK
   │  ⑦ DB 扣库存：update ... set stock = stock - 1 where voucher_id=? and stock > 0
   │  ⑧ 保存订单 save(voucherOrder)
   │  ⑨ 全部成功 → basicAck
   │     失败 → basicNack(requeue=false) → 死信队列
```

关键点：**用户请求在步骤 ④ 之后就返回了，真正的落库（步骤 ⑤~⑧）发生在另一个线程、甚至另一台机器上。** 这就是异步。

### 1.3 为什么这里需要消息队列

有三个理由，按重要性排序。

**第一个是削峰。** 秒杀的特点是流量在极短时间内涌进来，QPS 可能是平时的几百倍。但这些请求最终都要落到 MySQL 上：扣一次库存、插一条订单。MySQL 扛不住这种瞬时写入。加了队列之后，请求先被 Redis 快速过滤掉绝大部分（库存不足、重复下单的直接在 Lua 那一步就被拒了），真正需要落库的只有抢到资格的那一小批。这批消息堆在队列里，消费者按照自己的节奏慢慢消费，MySQL 的压力就被拉平了。

**第二个是异步解耦。** 用户其实不关心订单是什么时候写进数据库的，他只需要知道「我抢到了，订单号是多少」。所以把「判断资格」和「订单落库」拆开，接口只做前者。接口的响应时间从「一次 Redis 操作 + 一次 DB 事务」变成「一次 Redis 操作 + 一次消息投递」，用户感知更快。

**第三个是失败隔离。** 落库这一步如果失败（数据库抖动、锁冲突），不应该让用户的请求报错，也不应该让这个请求丢失。放进队列之后，失败的消息有地方待着，可以重试、可以进死信队列人工处理。

### 1.4 那为什么不用 JVM 里的阻塞队列

`VoucherOrderServiceImpl` 里注释掉的 `ArrayBlockingQueue<VoucherOrder> orderTasks = new ArrayBlockingQueue<>(1024 * 1024)` 就是这个思路。它能跑通，但在真实场景里有四个致命问题。

队列在 JVM 堆内存里，服务一重启，队列里没消费完的订单全没了，用户抢到了但订单不存在。队列也无法跨实例共享，服务部署两个节点，A 节点的请求进的队列只有 A 节点能消费，B 节点闲着也帮不上忙，起不到负载均衡的作用。容量上限写死在代码里，1024×1024 这个数字一旦被塞满，`add` 会直接抛异常或者阻塞住 Tomcat 线程。最后，消息状态无法观测，队列里积压了多少、消费到哪了，外部一无所知。

RabbitMQ 把队列搬到了独立的 Broker 进程里，上面四个问题一次解决。

---

## 2. 交换机、队列、routingKey 的设计

所有拓扑集中定义在 `RabbitMQConfig` 里。

### 2.1 拓扑全貌

| 角色 | 名称 | 类型与参数 |
|---|---|---|
| 业务交换机 | `seckill.order.exchange` | DirectExchange，`durable=true`、`autoDelete=false` |
| 业务队列 | `seckill.order.queue` | durable，带 `x-dead-letter-exchange` 和 `x-dead-letter-routing-key` |
| 业务绑定 | `seckill.order.queue` ← `seckill.order.exchange` | routingKey = `seckill.order` |
| 死信交换机 | `seckill.order.dlx.exchange` | DirectExchange，`durable=true`、`autoDelete=false` |
| 死信队列 | `seckill.order.dlx.queue` | durable，无额外参数 |
| 死信绑定 | `seckill.order.dlx.queue` ← `seckill.order.dlx.exchange` | routingKey = `seckill.order.dlx` |

画成图就是：

```
生产者
  │  routingKey = "seckill.order"
  ▼
seckill.order.exchange  (direct)
  │
  │  binding: seckill.order
  ▼
seckill.order.queue  ──消费失败/basicNack(requeue=false)──┐
  │                                                      │
  │  x-dead-letter-exchange = seckill.order.dlx.exchange │
  │  x-dead-letter-routing-key = seckill.order.dlx       │
  ▼                                                      ▼
消费者                                            seckill.order.dlx.exchange (direct)
                                                          │  binding: seckill.order.dlx
                                                          ▼
                                                  seckill.order.dlx.queue
                                                  （人工排查用）
```

### 2.2 为什么选 Direct 交换机

RabbitMQ 有四种常用交换机类型，选 Direct 的理由要从这个业务的**路由需求**倒推。

Fanout 是无脑广播，发给所有绑定的队列，完全不看 routingKey。这个场景里只有一种消息（秒杀订单），也只有一个下游要处理，广播是浪费。

Topic 支持通配符匹配（`seckill.order.*` 这种），适合「多种消息类型、多个消费者按模式订阅」的场景。这里只有一个路由键，用 Topic 的匹配能力纯属杀鸡用牛刀，还多了一层模式匹配的开销和出错的可能。

Headers 按消息头匹配，性能比 Direct 差，而且这个业务没有任何按 header 路由的需求。

Direct 是精确匹配 routingKey，一个 routingKey 对应一个（或一组）队列。这个业务的需求恰好就是最简单的：**一种消息，一个队列，精确投递**。Direct 语义最清晰，性能也最好。

还有一个理由：**死信队列的路由也用 Direct**。死信的路由规则是「队列的 `x-dead-letter-routing-key` 去匹配 DLX 的绑定」，本质是一次精确匹配，Direct 正好对上。

如果以后要扩展，比如「订单落库」和「发短信通知」都要消费同一条秒杀成功消息，那时候再考虑 Topic 或者给同一个队列加多个绑定。现在没必要提前设计。

### 2.3 durable 与持久化

三个地方都做了持久化声明，缺一不可。

`DirectExchange(name, true, false)` 的第二个参数是 `durable=true`，第三个是 `autoDelete=false`。交换机持久化，Broker 重启后交换机还在。

`QueueBuilder.durable(SECKILL_ORDER_QUEUE)` 队列持久化，Broker 重启后队列还在。用 `QueueBuilder` 而不是 `new Queue(name)` 是因为要挂死信参数，只有 Builder 有 `withArgument`。

消息本身的持久化不用显式配。Spring AMQP 的 `MessageProperties` 默认投递模式就是 `PERSISTENT`（我反编译 `spring-amqp-2.2.18` 确认过，静态初始化块里 `DEFAULT_DELIVERY_MODE = MessageDeliveryMode.PERSISTENT`）。所以 `convertAndSend` 发出的消息默认就是落盘的。

这里要纠正一个常见误解：队列持久化 ≠ 消息持久化。如果消息是非持久的，队列再持久化，Broker 重启后队列还在但消息没了。反过来消息持久化但队列不持久化，重启后队列没了消息也就跟着没了。两边都得做。

### 2.4 死信队列的参数

```java
QueueBuilder.durable(SECKILL_ORDER_QUEUE)
        .withArgument("x-dead-letter-exchange", SECKILL_ORDER_DLX_EXCHANGE)
        .withArgument("x-dead-letter-routing-key", SECKILL_ORDER_DLX_ROUTING_KEY)
        .build()
```

这两个参数的含义是：**当这个队列里的消息被 nack/reject 且 `requeue=false`，或者消息 TTL 过期，或者队列长度超限时，把它转发到 `seckill.order.dlx.exchange`，并把 routingKey 改写成 `seckill.order.dlx`。**

改写 routingKey 这一步容易漏。如果不设 `x-dead-letter-routing-key`，RabbitMQ 会沿用消息**原来的** routingKey，也就是 `seckill.order`。那这条死信到了 DLX 之后，就会去找 routingKey 为 `seckill.order` 的绑定，而 DLX 上只有 `seckill.order.dlx` 的绑定，匹配不上，消息会被直接丢掉。所以两个参数必须成对出现。

### 2.5 为什么用 Java Config 集中声明，而不是 `@RabbitListener` 上声明

Spring AMQP 提供两种声明拓扑的方式。

第一种是集中式：用 `@Bean` 定义 `Exchange`、`Queue`、`Binding`，交给 Spring Boot 自动装配的 `RabbitAdmin` 在应用启动连上 Broker 时自动声明。当前代码用的就是这种。

第二种是分散式：在 `@RabbitListener` 上用 `@QueueBinding`、`@Queue`、`@Exchange` 注解，让监听器自己把拓扑声明出来。长这样：

```java
@RabbitListener(bindings = @QueueBinding(
        value = @Queue(name = "seckill.order.queue", durable = "true"),
        exchange = @Exchange(name = "seckill.order.exchange", type = ExchangeTypes.DIRECT),
        key = "seckill.order"
))
```

选集中式的原因有三个。生产端需要知道 exchange 和 routingKey，消费端需要知道 queue，如果声明散在监听器上，生产端就得硬编码字符串，两边容易写歪。集中式把名字收成 `public static final` 常量，生产端消费端都引用同一个常量，写错编译器会拦。死信队列的绑定关系写在同一个文件里，拓扑一眼能看全，不用在多个监听器之间拼凑。还有一点，死信队列本来就没有监听器（它是给人看的），用 `@QueueBinding` 反而没地方写。

代码里 `@RabbitListener(queues = RabbitMQConfig.SECKILL_ORDER_QUEUE)` 直接引用了队列名常量，队列和绑定关系由 `RabbitMQConfig` 负责，这个分工是清楚的。

---

## 3. 生产者代码

生产者就是 `VoucherOrderServiceImpl.seckillVoucher()`。完整代码：

```java
@Override
public Result seckillVoucher(Long voucherId) {
    Long userId = UserHolder.getUser().getId();
    long orderId = redisIdWorker.nextId("order");
    // 1.执行lua脚本
    Long result = stringRedisTemplate.execute(
            SECKILL_SCRIPT,
            Collections.emptyList(),
            voucherId.toString(), userId.toString()
    );
    int r = result.intValue();
    // 2.判断结果是否为0
    if (r != 0) {
        // 2.1.不为0 ，代表没有购买资格
        return Result.fail(r == 1 ? "库存不足" : "不能重复下单");
    }
    VoucherOrder voucherOrder = new VoucherOrder();
    voucherOrder.setId(orderId);
    voucherOrder.setUserId(userId);
    voucherOrder.setVoucherId(voucherId);
    try {
        CorrelationData correlationData = new CorrelationData(String.valueOf(orderId));
        rabbitTemplate.convertAndSend(
                RabbitMQConfig.SECKILL_ORDER_EXCHANGE,
                RabbitMQConfig.SECKILL_ORDER_ROUTING_KEY,
                voucherOrder,
                correlationData
        );
        CorrelationData.Confirm confirm = correlationData.getFuture().get(5, TimeUnit.SECONDS);
        if (!confirm.isAck()) {
            throw new AmqpException("秒杀订单消息未获得 RabbitMQ 确认：" + confirm.getReason());
        }
        if (correlationData.getReturnedMessage() != null) {
            throw new AmqpException("秒杀订单消息无法路由到队列");
        }
    } catch (Exception e) {
        log.error("秒杀订单消息发送失败，voucherId={}，userId={}，orderId={}", voucherId, userId, orderId, e);
        rollbackSeckill(voucherId, userId);
        return Result.fail("下单失败，请重试");
    }
    // 3.返回订单id
    return Result.ok(orderId);
}
```

### 3.1 什么时候发送

发送时机卡在 **Lua 脚本返回 0 之后**。返回 1（库存不足）或者 2（重复下单）都不会走到发送逻辑，直接 `Result.fail` 返回。这个顺序很重要：先把没有资格的请求挡在 Redis 里，只有真正抢到名额的请求才会产生一条 MQ 消息。这样消息量被压到了和实际库存同一个数量级，而不是和请求量同一个数量级。

注意 `orderId` 是在执行 Lua **之前**就生成好的（第 166 行）。这一点和改造前一致，订单号由 `RedisIdWorker` 生成，是全局唯一的，不依赖数据库自增。

### 3.2 发送的内容

发的是一个 `VoucherOrder` 对象。真正会序列化进消息体的只有三个字段，因为 `application.yaml` 里开了 `spring.jackson.default-property-inclusion: non_null`，null 字段会被 Jackson 直接丢掉：

```json
{
  "id": 1234567890123456789,
  "userId": 1010,
  "voucherId": 5
}
```

`payType`、`status`、`createTime` 这些都是 null，不进消息体。落库的时候靠数据库的默认值来补（`hmdp.sql` 里 `pay_type` 和 `status` 都有 `DEFAULT`，`create_time` 有 `DEFAULT CURRENT_TIMESTAMP`）。

消息除了 body 还有 header。`Jackson2JsonMessageConverter` 会自动加上 `content_type: application/json`，以及一个关键的 `__TypeId__: com.hmdp.entity.VoucherOrder`。消费端就是靠这个 `__TypeId__` 把 JSON 反序列化回 `VoucherOrder` 对象的。

### 3.3 调用了什么 API

核心是一个方法：

```java
rabbitTemplate.convertAndSend(exchange, routingKey, object, correlationData)
```

四个参数分别是业务交换机名、路由键、消息体对象、以及一个 `CorrelationData`。

`CorrelationData` 的构造参数传的是订单号字符串。它的作用是给这条消息挂一个业务上的唯一标识，让后面异步到来的「确认」和「退回」回调能够找到是哪条消息的结果。不传 `CorrelationData` 的话，`publisher-confirm-type: correlated` 这个确认机制就没法用了。

### 3.4 为什么要把 confirm 同步等待出来

`convertAndSend` 本身是异步的，发出去就返回，它不保证 Broker 收到了。所以后面跟了三步校验。

```java
CorrelationData.Confirm confirm = correlationData.getFuture().get(5, TimeUnit.SECONDS);
```

这一行**阻塞当前线程**，最长等 5 秒，等 Broker 的确认。`publisher-confirm-type: correlated` 打开之后，Broker 对每条消息回一个 ack 或 nack，Spring AMQP 把它塞进 `CorrelationData` 内部的 `SettableListenableFuture`。`.get(5, SECONDS)` 就是把那个 future 取出来同步等。

`confirm.isAck()` 为 false 说明 Broker 明确拒绝了这条消息（比如内部错误、队列满了触发拒绝），直接抛异常。

```java
if (correlationData.getReturnedMessage() != null) {
    throw new AmqpException("秒杀订单消息无法路由到队列");
}
```

这一步检查的是「消息到了交换机，但交换机找不到匹配的队列」。这种情况要先把 `setMandatory(true)` 打开（`RabbitMQConfig.init()` 里做了），Broker 才会把无法路由的消息退回给生产者，而不是默默丢掉。`setReturnCallback` 收到退回消息后把它挂在 `CorrelationData` 上，这里就能读到。

关于这两步的执行顺序，有个细节值得知道：RabbitMQ 对无法路由的 mandatory 消息，会先发 `basic.return` 再发 `basic.ack`，两者在同一条 channel 上是有序的。所以 future 完成的时候，`getReturnedMessage()` 一般已经写好了，这个判断能生效。但这依赖于 Broker 的发送顺序，属于实现细节而非接口约定，心里有数就行。

### 3.5 发送失败怎么办

`catch` 块里做两件事。

先调 `rollbackSeckill(voucherId, userId)`，把 Redis 里刚才 Lua 脚本扣掉的库存加回去、把用户的下单标记移除：

```java
private void rollbackSeckill(Long voucherId, Long userId) {
    try {
        stringRedisTemplate.execute(
                SECKILL_ROLLBACK_SCRIPT,
                Collections.emptyList(),
                voucherId.toString(), userId.toString()
        );
    } catch (Exception e) {
        log.error("回滚秒杀资格失败，voucherId={}，userId={}", voucherId, userId, e);
    }
}
```

回滚用的是 `seckillRollback.lua`，库存 +1 和 `srem` 移除用户标记这两步也放在 Lua 里保证原子：

```lua
redis.call('incrby', stockKey, 1)
redis.call('srem', orderKey, userId)
```

回滚做完，接口返回 `Result.fail("下单失败，请重试")`。用户看到的是「下单失败」，但 Redis 里的库存和标记已经复原了，用户可以重新抢，不会因为一次 Broker 抖动就永久损失一个名额。

这里要诚实指出一点：回滚本身也被包在 `try-catch` 里，如果回滚再失败，只打日志不抛出。也就是说存在「Redis 库存扣了、消息没发出去、回滚也没成功」的极小概率窗口，这个名额就丢了。这是第 5 节和第 7 节会继续讨论的问题。

### 3.6 消息转换器

`RabbitMQConfig` 里定义了：

```java
@Bean
public Jackson2JsonMessageConverter jackson2JsonMessageConverter(ObjectMapper objectMapper) {
    return new Jackson2JsonMessageConverter(objectMapper);
}
```

Spring Boot 的 `RabbitTemplateConfigurer` 会自动把这个唯一的 `MessageConverter` Bean 装配到 `RabbitTemplate` 上，所以 `convertAndSend` 收到 `VoucherOrder` 对象时会走 JSON 序列化，而不是 Java 原生序列化。

用 JSON 而不是 JDK 序列化的理由：消息体在 RabbitMQ 管理界面里能直接看懂，方便排查；跨语言兼容，以后 Python 或者 Go 的服务也能消费；不受类结构变更影响（JDK 序列化改了 `serialVersionUID` 就反序列化失败）。代价是消息体积略大，以及需要消费端能解析出对应的类。

---

## 4. 消费者代码

### 4.1 `@RabbitListener` 声明与拓扑的关系

```java
@RabbitListener(queues = RabbitMQConfig.SECKILL_ORDER_QUEUE)
public void onOrderMessage(@Payload VoucherOrder voucherOrder, Channel channel, Message message) throws IOException {
```

注解里只写了 `queues`，队列名是 `RabbitMQConfig.SECKILL_ORDER_QUEUE` 这个常量。队列本身和绑定关系都由 `RabbitMQConfig` 里的 `@Bean` 声明，应用启动时 `RabbitAdmin` 会自动去 Broker 上创建（已存在且参数一致就跳过）。

也就是说：**队列、交换机、绑定的声明责任在配置类，监听器只负责订阅**。这和 2.5 节讲的集中式声明是一致的。

方法参数有三个，Spring AMQP 会分别注入。

第一个 `@Payload VoucherOrder voucherOrder` 是消息体。`@Payload` 其实可以省略（第一个参数默认就是 payload），写上是让意图更明确。它由 `Jackson2JsonMessageConverter` 根据 `__TypeId__` 头反序列化得到。

第二个 `Channel channel` 是当前消费的 AMQP channel，手动 ack 就靠它。

第三个 `Message message` 是原始消息对象，这里只用它取 deliveryTag。`deliveryTag` 是 Broker 给这条消息在当前 channel 上的编号，ack/nack 时要带回去。

### 4.2 消费方法逐行讲

```java
long deliveryTag = message.getMessageProperties().getDeliveryTag();
try {
    OrderHandleResult result = createVoucherOrder(voucherOrder);
    if (result == OrderHandleResult.ACK) {
        // 处理成功或幂等重复下单，确认消息
        channel.basicAck(deliveryTag, false);
    } else {
        // 无法恢复的错误（库存不足/等待拿锁超时）：不 requeue，直接进死信队列
        channel.basicNack(deliveryTag, false, false);
    }
} catch (Exception e) {
    // 处理过程抛异常：不 requeue，进死信队列，避免无限重投打死消费者
    log.error("秒杀订单处理异常，orderId={}，进入死信队列", voucherOrder.getId(), e);
    channel.basicNack(deliveryTag, false, false);
}
```

先取出 deliveryTag。然后调 `createVoucherOrder` 做真正的业务，它返回一个两态枚举：

```java
private enum OrderHandleResult {
    ACK,          // 处理成功或幂等重复，确认消息
    DEAD_LETTER   // 无法恢复（库存不足/等待拿锁超时），进死信队列
}
```

返回 `ACK` 就 `basicAck(deliveryTag, false)`，第二个参数 `false` 表示只确认这一条、不批量确认。消息从队列里彻底删除。

返回 `DEAD_LETTER` 就 `basicNack(deliveryTag, false, false)`。三个参数是 deliveryTag、是否批量、**是否重新入队**。最后一个是 `false`，这是整个可靠性设计的核心决策。

如果这里写 `true`，消息会被重新放回队列头部，然后立刻又被这个消费者拿到，又失败，又放回去。这是一个死循环，会把消费者线程彻底卡死，队列里的其它消息永远排在它后面出不来。所以处理不了的消息必须 `requeue=false`，让它去死信队列。

`catch` 块的处理和 `DEAD_LETTER` 一样，也是 `basicNack(..., false, false)`。`createVoucherOrder` 里任何没被预期的异常（数据库连不上、SQL 报错、序列化问题）都会落到这里，同样不重投，进死信。

整个消费者**没有任何一处使用 `requeue=true`**，这是刻意的。

### 4.3 `createVoucherOrder` 内部逻辑

```java
private OrderHandleResult createVoucherOrder(VoucherOrder voucherOrder) {
    Long userId = voucherOrder.getUserId();
    Long voucherId = voucherOrder.getVoucherId();
    // 创建锁对象
    RLock redisLock = redissonClient.getLock("lock:order:" + userId);
    boolean isLock;
    try {
        isLock = redisLock.tryLock(2, 10, TimeUnit.SECONDS);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        return OrderHandleResult.DEAD_LETTER;
    }
    if (!isLock) {
        log.error("获取订单锁超时，进入死信队列，userId={}", userId);
        return OrderHandleResult.DEAD_LETTER;
    }

    try {
        // 5.1.查询订单
        int count = query().eq("user_id", userId).eq("voucher_id", voucherId).count();
        // 5.2.判断是否存在
        if (count > 0) {
            log.warn("用户已下单，幂等确认，userId={}，voucherId={}", userId, voucherId);
            return OrderHandleResult.ACK;
        }

        // 6.扣减库存
        boolean success = seckillVoucherService.update()
                .setSql("stock = stock - 1")
                .eq("voucher_id", voucherId).gt("stock", 0)
                .update();
        if (!success) {
            log.error("库存不足，进入死信队列，voucherId={}", voucherId);
            return OrderHandleResult.DEAD_LETTER;
        }

        // 7.创建订单
        save(voucherOrder);
        return OrderHandleResult.ACK;
    } finally {
        redisLock.unlock();
    }
}
```

拆开看。

**加锁。** 锁的粒度是 `lock:order:{userId}`，也就是按用户加锁。为什么需要锁？因为同一个用户的同一条消息理论上可能被投递两次（至少一次投递语义），而且 `prefetch` 和并发消费的存在让两次处理可能真正并行。按用户加锁能保证同一个用户的下单逻辑串行执行。

`tryLock(2, 10, TimeUnit.SECONDS)` 的两个时间参数含义不同。第一个 `2` 是等待时间，最多等 2 秒去抢锁；第二个 `10` 是租约时间，拿到锁之后 10 秒自动过期。

第二个参数设成大于 0 会**关闭 Redisson 的看门狗（watchdog）**。看门狗的作用是自动续期，如果不开租约，Redisson 会每隔 `leaseTime/3` 续一次，只要线程活着锁就不会过期。开了租约，锁到点就强制释放。这里选后者，是为了给「持有锁的线程挂死」这种情况一个上界：最多卡 10 秒，锁一定会被释放，整个队列不会因为一条消息堵死。

拿到锁失败（等 2 秒还没等到）就返回 `DEAD_LETTER`。能等 2 秒还拿不到，说明持锁的那个消费者不正常，交给人工看比无限等待更合适。

`InterruptedException` 单独处理，并且调用了 `Thread.currentThread().interrupt()` 把中断标志恢复回去，这是个好习惯，不然中断信号会被吞掉。

**幂等查重。** `query().eq("user_id", userId).eq("voucher_id", voucherId).count()` 查这个用户对这个券有没有已经存在的订单。有的话返回 `ACK`，也就是确认并丢弃这条重复消息。这是幂等性的第一道实现。

**扣库存。** 

```java
.setSql("stock = stock - 1")
.eq("voucher_id", voucherId).gt("stock", 0)
```

生成的 SQL 大致是 `UPDATE tb_seckill_voucher SET stock = stock - 1 WHERE voucher_id = ? AND stock > 0`。`AND stock > 0` 这个条件放在 SQL 里，而不是先查再判断，利用的是数据库行锁保证「判断和扣减」原子。返回 `false` 说明影响行数为 0，也就是库存已经没了。

这里返回的是 `DEAD_LETTER` 而不是重试。原因是：这个消息能被发出来，说明 Redis 判定库存是够的；现在 DB 判定不够，说明 **Redis 库存和 DB 库存已经不一致了**。这不是重试能解决的问题，是要人工对账的，所以进死信。

**保存订单。** 最后 `save(voucherOrder)` 插入订单，返回 `ACK`。

**释放锁** 放在 `finally` 里，保证任何路径都会解锁。

### 4.4 容器工厂与手动 ack

```java
@Bean
public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory(
        ConnectionFactory connectionFactory,
        SimpleRabbitListenerContainerFactoryConfigurer configurer) {
    SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
    configurer.configure(factory, connectionFactory);
    ConditionalRejectingErrorHandler errorHandler = new ConditionalRejectingErrorHandler();
    errorHandler.setRejectManual(true);
    factory.setErrorHandler(errorHandler);
    return factory;
}
```

Bean 名字 `rabbitListenerContainerFactory` 是关键。`@RabbitListener` 没有指定 `containerFactory` 时，就是按这个名字去找容器的。Spring Boot 的默认容器工厂带了 `@ConditionalOnMissingBean`，我们自己定义之后就由这个接管。

`configurer.configure(factory, connectionFactory)` 这一行的作用是把 `application.yaml` 里的 `spring.rabbitmq.listener.simple.*` 配置应用到工厂上，也就是：

```yaml
listener:
  simple:
    acknowledge-mode: manual
    prefetch: 1
    retry:
      enabled: false
```

`acknowledge-mode: manual` 是手动 ack 的开关。配上它之后，Spring AMQP 不再自动确认消息，ack 完全由我们的代码决定。这是 4.2 节里 `basicAck`/`basicNack` 能生效的前提。

`prefetch: 1` 表示每个消费者一次最多预取 1 条未确认的消息。为什么要设成 1？因为消费者的处理是「加锁 → 查库 → 扣库存 → 插订单」这种偏重的操作，如果 prefetch 设很大，一个消费者会一次抓一大批消息在本地缓存里，这些消息无法被其它消费者分担，负载就歪了。设成 1 让消息在消费者之间均匀流转，也顺带降低了同一用户消息并发处理的概率。代价是吞吐量下降，每次都要等 Broker 推下一条。

`retry.enabled: false` 关掉 Spring AMQP 的自动重试。默认的重试机制（`RetryTemplate` 加 recoverer）在手动 ack 模式下的行为很容易踩坑：它重试若干次之后，默认的 `RejectAndDontRequeueRecoverer` 并不会真正给消息做 nack，结果就是消息一直处于 unacked 状态、消费者卡在那里不动。所以这里干脆关掉自动重试，把「要不要重投、怎么处理失败」的决定权全部交给监听器里的显式 ack/nack。

### 4.5 `ConditionalRejectingErrorHandler` 兜的是什么

监听器方法体内部的异常被 `try-catch` 全接住了，走不到 Spring 的错误处理器。那这个 `errorHandler` 还有用吗？有，它兜的是**方法体之前**的异常。

最典型的是反序列化失败：消息体不是合法 JSON、或者 `__TypeId__` 指向的类不存在。这时候 Spring AMQP 在调用 `onOrderMessage` 之前就抛异常了，我们的 `try-catch` 根本没机会执行。
我反编译 `spring-rabbit-2.2.18` 确认了这条链路的行为：

`ConditionalRejectingErrorHandler.handleError()` 判断异常是「致命」的之后，会抛出：

```java
new AmqpRejectAndDontRequeueException("Error Handler converted exception to fatal", rejectManual, throwable)
```

这个异常的布尔标志就是 `rejectManual` 字段。然后容器的 `BlockingQueueConsumer.rollbackOnExceptionIfNecessary()` 里判断要不要 nack：

```
nack = !acknowledgeMode.isAutoAck() && (!acknowledgeMode.isManual() || ContainerUtils.isRejectManual(throwable))
```

翻译成人话：**在手动 ack 模式下，容器只有在异常携带 `rejectManual=true` 时才会主动 nack。**

这正是代码里 `errorHandler.setRejectManual(true)` 的意义所在。nack 的时候 `requeue` 参数由 `ContainerUtils.shouldRequeue()` 决定，对 `AmqpRejectAndDontRequeueException` 返回 `false`，于是消息同样走死信。

顺带说一个反编译发现的小细节：**在 2.2.18 里 `rejectManual` 字段的默认值本来就是 `true`**（构造器里 `iconst_1; putfield rejectManual`）。所以 `setRejectManual(true)` 在功能上是冗余的。不过写出来能表明意图，而且如果哪天升到默认值为 `false` 的版本，这行代码就成了关键的保险。我倾向于保留。

### 4.6 ack / nack 决策汇总

| 场景 | 返回值/动作 | 消息去向 |
|---|---|---|
| 订单创建成功 | `ACK` → `basicAck` | 从队列删除 |
| 用户已有订单（重复投递） | `ACK` → `basicAck` | 从队列删除（幂等丢弃） |
| 等锁 2 秒超时 | `DEAD_LETTER` → `basicNack(requeue=false)` | 死信队列 |
| 线程被中断 | `DEAD_LETTER` → `basicNack(requeue=false)` | 死信队列 |
| DB 扣库存影响行数为 0 | `DEAD_LETTER` → `basicNack(requeue=false)` | 死信队列 |
| 处理过程抛任意异常 | `catch` → `basicNack(requeue=false)` | 死信队列 |
| 反序列化失败等（方法体之前） | 容器 `ConditionalRejectingErrorHandler` | 死信队列 |

---
## 5. 消息可靠性方案

消息可能丢在三个地方，得分开处理。

### 5.1 生产端不丢

风险是「Lua 已经扣了 Redis 库存，但消息没到 Broker」。

对策分两层。第一层是 `publisher-confirm-type: correlated`，Broker 收到消息后回 ack/nack，代码用 `correlationData.getFuture().get(5, TimeUnit.SECONDS)` 同步等这个结果。等到了且 `isAck()` 为 true 才算发送成功。

第二层是 `publisher-returns: true` 加 `rabbitTemplate.setMandatory(true)`。这两项解决的是「消息到了交换机但没有队列接收」的情况。只开 confirm 是不够的，因为从 Broker 的角度看，一条无法路由的消息它「收到并处理了」，一样会回 ack，但消息实际上被丢掉了。必须开 mandatory + return 回调才能捕获。

两个回调都记录在 `RabbitMQConfig.init()` 里：

```java
@PostConstruct
public void init() {
    rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
        if (!ack) {
            log.error("秒杀订单消息发送失败，correlationData={}，cause={}", correlationData, cause);
        }
    });
    rabbitTemplate.setReturnCallback((message, replyCode, replyText, exchange, routingKey) ->
            log.error("秒杀订单消息路由失败，replyCode={}，replyText={}，exchange={}，routingKey={}",
                    replyCode, replyText, exchange, routingKey));
    rabbitTemplate.setMandatory(true);
}
```

任一环节失败，`seckillVoucher` 的 `catch` 就会触发，做两件事：回滚 Redis（`rollbackSeckill`），返回失败给用户。用户重试即可。

**这里遗留一个窗口。** 如果应用在「Lua 执行完」和「发送消息」之间崩溃（进程被 kill、机器断电），catch 块也不会执行，回滚不会发生。结果是 Redis 库存 -1、用户标记已写入，但既没有消息也没有订单，这个名额永久丢失。这是把 `xadd` 从 Lua 里搬出来必然产生的代价，靠应用层代码没法完全消除。第 7 节会给出对策建议。

### 5.2 Broker 端不丢

靠 2.3 节讲的持久化三件套：交换机 durable、队列 durable、消息 persistent。三者齐备，Broker 正常重启不会丢消息。

要注意这只覆盖「正常重启」。如果 Broker 磁盘损坏、或者队列是非镜像/非仲裁的单点，机器彻底挂了仍然会丢。生产环境需要用仲裁队列（Quorum Queue）或者镜像队列做副本。当前代码用的是普通队列，在本地开发场景够用。

### 5.3 消费端不丢

`acknowledge-mode: manual` 意味着消息只有在代码显式 `basicAck` 之后才会从队列删除。消费过程中进程崩溃，消息处于 unacked 状态，channel 断开后 Broker 会自动把它重新投递给其它消费者。这是「至少一次投递」语义的来源。

代价就是**必然出现重复消费**。同一条消息可能被处理两次，这不是 bug，是 at-least-once 的固有特性。所以消费端必须幂等。

处理失败的消息不会丢，会走 `basicNack(requeue=false)` 进死信队列，`seckill.order.dlx.queue` 会把它们存着。

### 5.4 幂等性

代码里实现了两层。

**第一层是业务查重。** 处理前先查 `tb_voucher_order` 里有没有 `(user_id, voucher_id)` 的记录，有就直接 `ACK` 丢弃。配合 Redisson 的按用户锁，同一个用户的并发重复消息会被串行化，第二个进来时一定能看到第一个写下的订单。

**第二层是数据库唯一索引。** 这是最后一道防线，前面所有判断都可能因为并发时序而失效，数据库的唯一约束是最终保证。**但是——** 我查了 `src/main/resources/db/hmdp.sql` 第 247 到 259 行，`tb_voucher_order` 只定义了 `PRIMARY KEY (id)`，**没有** `(user_id, voucher_id)` 的唯一索引。同时改造前的交付报告里把唯一索引描述成了「最后一道防线」，这跟实际的 schema 对不上。这是一个真实存在的缺口，第 7 节给了修复 SQL。

补充一点：即使加上了唯一索引，当前代码也有个小问题。索引冲突会抛 `DuplicateKeyException`，被 `catch` 捕获后走 `basicNack(requeue=false)` 进死信。但这种情况其实是幂等重复，应该 `ACK`，进死信反而会污染死信队列。建议在 `catch` 里单独识别 `DuplicateKeyException` 并返回 `ACK`。

### 5.5 死信队列

死信队列目前**只是一个队列，没有消费者**。消息进去之后就停在那里等人处理。生产环境需要配监控和告警，比如：

```bash
# 查看死信队列积压数量
rabbitmqctl list_queues name messages
```

或者在管理界面（`http://localhost:15672`，需启用 `rabbitmq_management` 插件）里直接看。积压数量大于 0 就该告警。

死信队列里的每一条消息都对应一个需要人工介入的业务异常：Redis 库存与 DB 库存不一致、锁竞争异常、代码 bug。处理完可以用管理界面的 "Move messages" 或者 shovel 插件把消息挪回业务队列重投。

---
## 6. 与 Redis 消息队列的对比

### 6.1 对比表

| 维度            | Redis Stream                | RabbitMQ                         |
| ------------- | --------------------------- | -------------------------------- |
| 消息存储          | 内存为主，受 `maxmemory` 限制       | 磁盘，内存只是缓存，可堆积                    |
| 堆积能力          | 差，积压会撑爆内存触发淘汰               | 强，可换页到磁盘                         |
| 生产端确认         | 无。`XADD` 返回成功只代表写进内存        | publisher confirm（ack/nack）      |
| 路由能力          | 无交换机概念，消费者按 key 订阅          | direct/topic/fanout/headers 四种路由 |
| 死信机制          | 需自己用 pending 列表实现           | 原生 DLX，队列参数一配就有                  |
| 消费端限流         | 无内建 prefetch                | prefetch 精确认，按消费者控制              |
| 失败重试          | 自己写                         | 可配 `RetryTemplate`、退避策略          |
| 消息 TTL / 延迟队列 | 需自己实现                       | 原生支持                             |
| 管理界面          | 需要自己搭或用 redis-cli           | 官方 Management 插件，可视化             |
| 生态与多语言        | 客户端支持广但消息语义要自己封装            | AMQP 标准协议，客户端成熟                  |
| 吞吐量           | 极高，单机可达十万级 QPS              | 万级 QPS                           |
| 单条延迟          | 亚毫秒                         | 通常毫秒级                            |
| 部署成本          | 项目本来就有 Redis                | 需要额外部署和维护一个 Broker               |
| 与 Spring 集成   | 手写 `StringRedisTemplate` 调用 | `@RabbitListener` 声明式，自动装配       |
