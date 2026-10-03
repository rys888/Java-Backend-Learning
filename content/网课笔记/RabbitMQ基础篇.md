# RabbitMQ 基础篇 

## 主线

```
同步调用的三个问题 → 异步调用 + MQ 三个角色 → RabbitMQ 核心概念
        ↓
SpringAMQP：RabbitTemplate 发、@RabbitListener 收
        ↓
五种模型：简单队列 → WorkQueue → Fanout → Direct → Topic
        ↓
自动声明队列/交换机 + JSON 消息转换器
        ↓
业务落地：支付成功异步通知交易服务
```

---

## 一、为什么用 MQ

同步调用（OpenFeign 链式调用）的三个问题：

| 问题 | 表现 | 原因 |
|---|---|---|
| 拓展性差 | 支付成功后每多一件事，支付代码就要改一次 | 主业务被迫感知旁支业务，违反开闭原则 |
| 性能下降 | 总耗时 = 所有远程调用耗时之和 | 同步调用阻塞等待 |
| 级联失败 | 交易服务或通知服务挂了，事务回滚，支付失败 | 非核心业务连累核心业务 |

第三条最要命：钱都扣了，没道理因为短信发不出去就退回去。这类旁支业务不该放进核心事务。

异步调用用消息通知代替直接调用，角色变成三个：消息发送者（publisher）、消息 Broker（管理、暂存、转发消息）、消息接收者（consumer）。改造后支付服务只做扣款和改流水状态，发一条消息给 Broker，交易、通知、积分各自订阅处理。

好处是耦合低、总耗时只算核心业务、加新业务不用改支付代码、下游挂了也不影响支付。代价是完全依赖 Broker 的可靠性，链路从一条调用栈变成一条消息流，排查问题更麻烦。

选型上课堂用 RabbitMQ，国内用得最多，可用性、可靠性、吞吐、延迟都比较均衡。Kafka 吞吐最高，RocketMQ 吞吐和可靠性兼顾，追求低延迟可以选 RabbitMQ 或 Kafka。

---

## 二、RabbitMQ 核心概念

| 概念 | 说明 |
|---|---|
| publisher | 生产者，发消息的一方 |
| consumer | 消费者，收消息的一方 |
| queue | 队列，存储消息。消息在队列里等着被消费 |
| exchange | 交换机，负责路由。生产者把消息发给交换机，由它决定投到哪个队列 |
| virtual host | 虚拟主机，数据隔离单位。每个 vhost 有自己的 exchange 和 queue |

一句话记住：交换机只管路由不存消息，队列只管存储不认路由，两者靠 Binding 绑定。

在控制台上做过一次验证：直接往没有绑定队列的交换机发消息，消息丢了；建好队列但没绑定，消息还是到不了；绑定之后才进队列。这正好反证了上面那句话。

两个端口别搞混：`5672` 是代码里收发消息的通信端口，`15672` 是浏览器上的管理控制台。yml 里写成 15672 会直接连接异常。

多项目共用一套集群时，给每个项目建独立账号和独立 virtual host，代码里用 `virtual-host` 选定自己的环境。

---

## 三、SpringAMQP

加 `spring-boot-starter-amqp` 依赖后，自动装配会创建好 `ConnectionFactory`、`RabbitTemplate`、`AmqpAdmin` 和 `SimpleRabbitListenerContainerFactory`，配置写好地址就能直接注入使用。

publisher 和 consumer 两端的 yml 一样：

```yaml
spring:
  rabbitmq:
    host: 192.168.150.101 # 虚拟机 IP
    port: 5672            # 通信端口，不是 15672
    virtual-host: /hmall
    username: hmall
    password: 123
```

### 3.1 最简单模型：直接发到队列

publisher 端：

```java
@SpringBootTest
public class SpringAmqpTest {
    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Test
    public void testSimpleQueue() {
        rabbitTemplate.convertAndSend("simple.queue", "hello, spring amqp!");
    }
}
```

consumer 端：

```java
@Component
public class SpringRabbitListener {
    @RabbitListener(queues = "simple.queue")
    public void listenSimpleQueueMessage(String msg) {
        System.out.println("消费者接收到消息：【" + msg + "】");
    }
}
```

几个必须弄清楚的点：

- `convertAndSend` 里的 convert，指先用 `MessageConverter`（默认 `SimpleMessageConverter`）把 Java 对象转成 AMQP 的 `Message` 再发出去。
- 只传队列名也能发出去，是因为内部用了默认交换机（名字是空字符串 `""`）。每个队列都会自动绑定到它，bindingKey 等于队列名，routingKey 就是队列名。所谓"直接发队列"本质还是走了交换机，只是被隐藏了。这种用法一般只在测试里出现。
- `@SpringBootTest` 会启动完整容器，不写就注入不了 `RabbitTemplate`。
- `@RabbitListener` 由 `RabbitListenerAnnotationBeanPostProcessor` 包装成 `MessageListener`，容器启动后建连接、订阅队列，消息到了由容器自己的线程回调方法。参数类型决定反序列化成什么，发什么类型就得用什么类型接。
- 队列必须先存在，不然消费者启动就报错，这个问题交给 3.4 的自动声明解决。
- 方法抛异常默认会 requeue 重试，可能死循环刷日志。
- 消费者线程不是 Web 请求线程，`UserContext` 里的 ThreadLocal 取不到值。

### 3.2 WorkQueue：能者多劳

核心是把多个消费者绑到同一个队列，一起消费。适用于消息处理耗时、生产速度大于消费速度的场景。

```java
// 发送：连续发 50 条模拟堆积
for (int i = 0; i < 50; i++) {
    rabbitTemplate.convertAndSend("work.queue", "hello, message_" + i);
    Thread.sleep(20);
}
```

```java
// 接收：两个消费者监听同一个队列
@RabbitListener(queues = "work.queue")
public void listenWorkQueue1(String msg) throws InterruptedException {
    System.out.println("消费者1接收到消息：【" + msg + "】");
    Thread.sleep(20);   // 模拟每秒处理 50 条
}

@RabbitListener(queues = "work.queue")
public void listenWorkQueue2(String msg) throws InterruptedException {
    System.err.println("消费者2接收到消息：【" + msg + "】");
    Thread.sleep(200);  // 模拟每秒处理 5 条
}
```

按默认设置跑，两个消费者各拿 25 条。队列是轮询分发，一条一条轮流给，不看消费者处理能力，快的干完就空闲，慢的还在慢慢磨。

在 consumer 的 yml 里加一行：

```yaml
spring:
  rabbitmq:
    listener:
      simple:
        prefetch: 1 # 处理完一条并 ack 之后，才拿下一批
```

再跑一次，消费者1 处理 44 条、消费者2 只有 6 条，总耗时还是一秒左右。

prefetch 是消费者的预取数量，指未 ack 之前最多同时持有几条未确认消息。Spring AMQP 的 simple 容器默认 250，等于一次把一堆消息揽到怀里，队列以为它很能干就不再给别人；设成 1 就是处理完再拿，队列能把新消息派给空闲的消费者。

小结：多个消费者绑同一个队列时，同一条消息只会被一个消费者处理；用 prefetch 控制预取数量来实现能者多劳。

### 3.3 交换机与三种路由模型

引入交换机后，publisher 不再发给队列而是发给交换机，queue 必须和交换机绑定，consumer 不变。交换机只负责转发，没有队列绑定或者没有符合规则的队列，消息就丢了。

| 类型 | 路由规则 |
|---|---|
| Fanout | 广播，投给所有绑定到它的队列 |
| Direct | 按 RoutingKey 完全一致匹配 |
| Topic | RoutingKey 支持通配符，比 Direct 灵活 |
| Headers | 按消息头匹配，用得少 |

**Fanout**

```java
// 发送：Fanout 忽略 routingKey，传 "" 即可
// 不能传 null，会抛 IllegalArgumentException
rabbitTemplate.convertAndSend("hmall.fanout", "", "hello, everyone!");
```

```java
@RabbitListener(queues = "fanout.queue1")
public void listenFanoutQueue1(String msg) {
    System.out.println("消费者1接收到Fanout消息：【" + msg + "】");
}

@RabbitListener(queues = "fanout.queue2")
public void listenFanoutQueue2(String msg) {
    System.out.println("消费者2接收到Fanout消息：【" + msg + "】");
}
```

一条消息两个消费者都收到，这点和 WorkQueue 正相反。

**Direct**

队列绑定时要指定 bindingKey，发送时要指定 routingKey，两者完全一致队列才收。假设 `direct.queue1` 绑了 `blue` 和 `red`，`direct.queue2` 绑了 `yellow` 和 `red`：

```java
rabbitTemplate.convertAndSend("hmall.direct", "red", "红色警报！");
// red 两个队列都绑了 → 两个消费者都收到

rabbitTemplate.convertAndSend("hmall.direct", "blue", "虚惊一场！");
// blue 只有 direct.queue1 绑了 → 只有消费者1收到
```

多个队列用同一个 key 时，效果就和 Fanout 差不多了。

**Topic**

同样按 RoutingKey 路由，区别是绑定用的 BindingKey 可以写通配符。BindingKey 由多个单词组成，用 `.` 分隔。

| 通配符 | 含义 |
|---|---|
| `#` | 匹配零个或多个词 |
| `*` | 匹配恰好一个词 |

`item.#` 能匹配 `item.spu.insert` 和 `item.spu`，`item.*` 只能匹配 `item.spu`。

假设 routingKey 有 `china.news`、`china.weather`、`japan.news`、`japan.weather`：`topic.queue1` 绑 `china.#`，能收到两条中国的；`topic.queue2` 绑 `#.news`，能收到两条新闻。发一条 `china.news`，两个队列都匹配，两个消费者都收到。

```java
rabbitTemplate.convertAndSend("hmall.topic", "china.news", "喜报！孙悟空大战哥斯拉，胜!");
```

用哪个交换机看需求：消息要无条件被多个队列收到就 Fanout；有条件、但条件是几个固定 key 就 Direct；条件带层级、需要用通配符就 Topic。

### 3.4 声明队列和交换机

控制台手动建的问题是，队列和交换机由程序员定义，上线却要运维创建，中间靠文档传递，很容易出错。推荐让程序启动时检查并自动创建。

三种方式：控制台手动（不推荐）；配置类里声明 `Queue`、`Exchange`、`Binding` 三个 Bean（直观但啰嗦）；`@RabbitListener` 配合 `@QueueBinding` 注解声明（最简洁，推荐）。

配置类方式：

```java
@Configuration
public class FanoutConfig {
    @Bean
    public FanoutExchange fanoutExchange() {
        return new FanoutExchange("hmall.fanout");
    }

    @Bean
    public Queue fanoutQueue1() {
        return new Queue("fanout.queue1");
    }

    @Bean
    public Binding bindingQueue1(Queue fanoutQueue1, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(fanoutQueue1).to(fanoutExchange);
    }
    // 第二个队列同理
}
```

`RabbitAdmin` 会扫描容器里所有 `Queue`、`Exchange`、`Binding` 类型的 Bean，连接建立后自动向 Broker 声明，所以 Bean 名字不重要，类型才重要。Binding 方法的参数是按类型注入的，参数名只影响可读性。Fanout 绑定不需要 key，`bind().to()` 就结束了。

Direct 的痛点在于每个 key 都要写一个 Binding Bean，4 个 key 就是 4 个 Bean，注解方式就是为解决这个出现的：

```java
@RabbitListener(bindings = @QueueBinding(
    value = @Queue(name = "direct.queue1"),
    exchange = @Exchange(name = "hmall.direct", type = ExchangeTypes.DIRECT),
    key = {"red", "blue"}
))
public void listenDirectQueue1(String msg) {
    System.out.println("消费者1接收到direct.queue1的消息：【" + msg + "】");
}

@RabbitListener(bindings = @QueueBinding(
    value = @Queue(name = "topic.queue1"),
    exchange = @Exchange(name = "hmall.topic", type = ExchangeTypes.TOPIC),
    key = "china.#"
))
public void listenTopicQueue1(String msg) {
    System.out.println("消费者1接收到topic.queue1的消息：【" + msg + "】");
}
```

两个方法就干完了原来一整个配置类的活。

常用属性速查：

| 注解 | 属性 | 说明 |
|---|---|---|
| `@Queue` | `name` / `value` | 队列名，两者等价 |
| | `durable` | 是否持久化，默认 true |
| | `exclusive` | 是否排他，默认 false |
| | `autoDelete` | 没有消费者时是否自动删除，默认 false |
| | `arguments` | 额外参数，如死信、TTL、队列长度限制 |
| `@Exchange` | `name` / `value` | 交换机名 |
| | `type` | `ExchangeTypes.DIRECT` / `TOPIC` / `FANOUT` / `HEADERS` |
| | `durable` | 是否持久化，默认 true |
| | `delayed` | 是否延迟交换机，需要插件 |
| `@QueueBinding` | `key` | 绑定 key，数组形式可以写多个 |

如果 Broker 上已经存在同名但属性不同的队列（比如原来 durable=false，现在声明成 true），启动会报 `406 PRECONDITION_FAILED`，先删掉旧队列或者把属性对齐。

### 3.5 消息转换器

`RabbitTemplate` 收的是 `Object`，发送时序列化成字节，接收时再反序列化回来，默认用 JDK 序列化。问题是数据体积大、有反序列化攻击风险、控制台里看到的是一堆 `rO0ABXNy...` 乱码。

改用 JSON。两端都要加依赖，如果项目里引了 `spring-boot-starter-web` 就不用再加，它已经带了 Jackson：

```xml
<dependency>
    <groupId>com.fasterxml.jackson.dataformat</groupId>
    <artifactId>jackson-dataformat-xml</artifactId>
    <version>2.9.10</version>
</dependency>
```

再在两端的启动类里加 Bean：

```java
@Bean
public MessageConverter messageConverter() {
    Jackson2JsonMessageConverter converter = new Jackson2JsonMessageConverter();
    // 自动生成消息 id，将来做幂等判断时能识别重复消息
    converter.setCreateMessageIds(true);
    return converter;
}
```

Bean 的类型必须写成 `MessageConverter`，自动装配会把它同时用到 `RabbitTemplate` 和监听容器工厂上，收发都是 JSON。两端都要配，一端 JDK 一端 JSON 会直接反序列化失败。发送方发 Map，接收方就得用 `Map<String, Object>` 接；发自定义对象则要有无参构造器。

```java
@RabbitListener(queues = "object.queue")
public void listenObjectQueue(Map<String, Object> msg) {
    System.out.println("消费者接收到object.queue消息：【" + msg + "】");
}
```

`Jackson2JsonMessageConverter` 真正依赖的是 `jackson-databind`，上面的 `jackson-dataformat-xml` 只是把它传递依赖带进来了，直接引 `jackson-databind` 更规范。

---

## 四、业务改造：支付成功异步通知交易服务

把"支付成功后用 OpenFeign 调交易服务改订单状态"改成"发一条 MQ 消息"。

| 项 | 值 |
|---|---|
| 交换机 | `pay.topic`（topic 类型） |
| 队列 | `mark.order.pay.queue` |
| BindingKey / RoutingKey | `pay.success` |
| 消息内容 | 订单 id |

消费端（trade-service）：

```java
@Component
@RequiredArgsConstructor
public class PayStatusListener {

    private final IOrderService orderService;

    @RabbitListener(bindings = @QueueBinding(
            value = @Queue(name = "mark.order.pay.queue", durable = "true"),
            exchange = @Exchange(name = "pay.topic", type = ExchangeTypes.TOPIC),
            key = "pay.success"
    ))
    public void listenPaySuccess(Long orderId) {
        orderService.markOrderPaySuccess(orderId);
    }
}
```

队列、交换机、绑定三种声明一行注解全搞定。`durable = "true"` 表示队列持久化，Broker 重启后还在，持久化队列配持久化消息才真不丢。生产端发 `Long`，接收参数就必须是 `Long`。

生产端（pay-service）在 `tryPayOrderByBalance` 里把原来的 Feign 调用换掉：

```java
try {
    rabbitTemplate.convertAndSend("pay.topic", "pay.success", po.getBizOrderNo());
} catch (Exception e) {
    log.error("支付成功的消息发送失败，支付单id：{}，交易单id：{}", po.getId(), po.getBizOrderNo(), e);
}
```

改完的差别：从强依赖交易服务可用变成只依赖 MQ 可用；发消息近乎瞬时，不用等下游响应；交易服务挂了消息还在队列里等着，恢复后接着消费，不会再回滚支付。

这段代码留了两个基础篇式的妥协，高级篇会解决：

一是 `try/catch` 把发送异常吞掉了。为了不让通知失败回滚支付这个核心业务，这么做是对的，代价是消息真发不出去时没人知道，订单会一直停在待支付。高级篇用发送方确认加重试，或者延迟消息兜底。

二是发消息在事务提交之前。消息发出去之后事务回滚，就会出现交易服务改了订单状态、支付单没改的不一致。规范做法是用事务同步器在提交后再发消息，或者用本地消息表。

实际 hmall 代码里 `PayStatusListener` 还做了幂等处理，把无条件更新换成了带 `status = 1` 条件的更新，重复消费也不会出错。

---

## 五、练习要点

**MQ 配置抽取到 Nacos**：每个服务的 `bootstrap.yaml` 里在 `shared-configs` 加一条 `shared-mq.yaml`，内容就是那段 `spring.rabbitmq.*`。

**下单后异步清理购物车**：交换机 `trade.topic`，队列 `cart.clear.queue`，key 是 `order.create`，消息体是商品 id 集合。

```java
try {
    rabbitTemplate.convertAndSend(
            MqConstants.TRADE_EXCHANGE_NAME, MqConstants.ORDER_CREATE_KEY, itemIds);
} catch (AmqpException e) {
    log.error("清理购物车的消息发送异常", e);
}
```

```java
@RabbitListener(bindings = @QueueBinding(
        value = @Queue(name = "cart.clear.queue"),
        exchange = @Exchange(name = MqConstants.TRADE_EXCHANGE_NAME, type = ExchangeTypes.TOPIC),
        key = MqConstants.ORDER_CREATE_KEY
))
public void listenOrderCreate(List<Long> itemIds) {
    cartService.removeByItemIds(itemIds);
}
```

消息体是 `List<Long>`，接收参数也得是 `List<Long>`。

**登录用户信息怎么传**：异步调用不走 Web 请求线程，`UserContext` 里的 ThreadLocal 取不到值。笨办法是在消息体里带上用户、消费者再取出来，麻烦而且体验不统一。优雅做法是用 `MessagePostProcessor` 往消息 header 里塞：

```java
// 发送端：发出前把用户写进 header
rabbitTemplate.setBeforePublishPostProcessors(message -> {
    Long userId = UserContext.getUser();
    if (userId != null) {
        message.getMessageProperties().setHeader("user-info", userId);
    }
    return message;
});

// 接收端：收到后从 header 取出来放回 UserContext
rabbitListenerContainerFactory.setAfterReceivePostProcessors(message -> {
    Long userId = message.getMessageProperties().getHeader("user-info");
    if (userId != null) {
        UserContext.setUser(userId);
    }
    return message;
});
```

配好之后业务代码里照旧 `UserContext.getUser()`，用 MQ 的人完全无感。

**哪些业务适合改异步**：非核心链路（短信、积分、日志）、实时性要求低、能接受最终一致性、一个事件触发多个下游动作。需要立刻拿返回值做判断的（比如扣库存前要先知道够不够）和强一致的不能改。

---

## 六、速查

概念类：

| 要点 | 说明 |
|---|---|
| 交换机不存储消息 | 没有匹配的队列，消息直接丢 |
| 队列必须绑定交换机 | 只建队列不绑定，消息到不了 |
| 默认交换机 | 名字是 `""`，每个队列自动绑定，bindingKey 等于队列名 |
| virtual host | 数据隔离单位，yml 里配 `virtual-host` |
| 端口 | 5672 通信，15672 控制台 |

代码易错点：

| 易错点 | 正确做法 |
|---|---|
| yml port 写成 15672 | 通信端口是 5672 |
| `convertAndSend` 传 null routingKey | 传 `""` |
| 发 `Long` 收 `String` | 类型必须一致 |
| 只在一端配 JSON 转换器 | 两端都要配 |
| 自定义对象接收报错 | 对象要有无参构造器 |
| `@Bean` 声明队列没生效 | 检查 Bean 类型是不是 `Queue` / `Exchange` / `Binding` |
| 注解声明报 406 | Broker 上已有同名但属性不同的队列，先删掉 |
| Direct 写了一堆 Binding Bean | 改用 `@QueueBinding` |

WorkQueue：

| 要点 | 说明 |
|---|---|
| 同一条消息只被一个消费者处理 | 这是和 Fanout 的本质区别 |
| 默认轮询分发 | 不看处理能力，快的空闲慢的堆积 |
| `prefetch: 1` | 处理完一条再拿一条，能者多劳 |
| 默认 prefetch | Spring AMQP simple 容器是 250 |

基础篇留下的问题，正是高级篇的内容：

| 基础篇写法 | 遗留问题 | 高级篇解法 |
|---|---|---|
| try/catch 吞掉发送异常 | 消息可能真丢了，无人知晓 | 发送方确认 + 重试 |
| 消费者抛异常默认 requeue | 可能死循环刷日志 | 消费者确认 + 失败重试 + 死信队列 |
| 事务中直接发消息 | 事务回滚与消息不一致 | 事务同步器 / 本地消息表 |
| 队列和消息持久化 | 极端情况仍可能丢 | 惰性队列、镜像队列、仲裁队列 |
| 订单超时自动取消 | 基础篇没讲 | 延迟消息 + 延迟交换机插件 |
| 消息重复消费 | 没有幂等保障 | 幂等设计（messageId、状态条件更新） |
| 登录用户信息传递 | 传递麻烦 | `MessagePostProcessor` 传 header |

---

*精简自课程文档《MQ基础》（原文 1307 行），保留核心概念、五种模型、关键代码和易错点。*
