Spring 框架中使用了很多经典的**设计模式（Design Patterns）**，对于 Java 后端实习面试，重点掌握 **工厂模式、单例模式、代理模式、模板方法模式、观察者模式、适配器模式** 这 6 种即可。

其中，**工厂模式、单例模式和代理模式最重要**，因为它们分别对应 Spring 的 IoC 容器、Bean 管理和 AOP。

## **一、Spring 中常见的设计模式 ⭐⭐⭐⭐⭐**

|**设计模式**|**Spring 中的典型应用**|**作用**|
|---|---|---|
|**工厂模式** ⭐⭐⭐⭐⭐| `BeanFactory`、`FactoryBean` |创建和管理 Bean|
|**单例模式** ⭐⭐⭐⭐⭐|Spring 默认的 Singleton Bean|一个容器中同名 Bean 通常只有一个实例|
|**代理模式** ⭐⭐⭐⭐⭐|Spring AOP、`@Transactional` |不修改业务代码，实现方法增强|
|**模板方法模式** ⭐⭐⭐⭐| `JdbcTemplate`、`RedisTemplate` |封装通用流程，简化业务操作|
|**观察者模式** ⭐⭐⭐⭐| `ApplicationEventPublisher`、`@EventListener` |实现事件发布与监听|
|**适配器模式** ⭐⭐⭐⭐|Spring MVC 的 `HandlerAdapter` |适配不同类型的处理器|
|策略模式| `Resource`、`InstantiationStrategy` |根据不同场景选择不同实现|
|责任链模式|Spring Security 过滤器链、Spring AOP 拦截器链|多个处理器依次处理请求|

下面结合你学过的 Spring 知识理解。

---

## **二、工厂模式：BeanFactory ⭐⭐⭐⭐⭐**

**工厂模式的核心思想：对象不由使用者直接创建，而是交给工厂统一创建。**

普通 Java 开发：

```java
UserService userService = new UserService();
```

使用 Spring：

```java
@Autowired
private UserService userService;
```

我们不再需要手动创建 `UserService`，而是由 Spring IoC 容器负责创建和管理。

其中：

- `BeanFactory`：Spring IoC 容器的基础接口。
- `ApplicationContext`：扩展了 BeanFactory 的容器接口，提供更多功能。
- `FactoryBean`：特殊的工厂 Bean，可以自定义对象的创建过程。

例如：

```java
@Component
public class UserService {
}
```

Spring 会根据 BeanDefinition 等信息创建 `UserService` 对象。

**因此，Spring IoC 容器体现了工厂模式的思想。**

---

## **三、单例模式：Singleton Bean ⭐⭐⭐⭐⭐**

Spring 中 Bean 的默认作用域是 `singleton`。

```java
@Service
public class UserService {
}
```

假设：

```java
UserService user1 = context.getBean(UserService.class);
UserService user2 = context.getBean(UserService.class);

System.out.println(user1 == user2);
```

输出：

```text
true
```

说明两次获取的是同一个对象。

Spring 会将创建完成的单例 Bean 缓存在：

```java
singletonObjects
```

也就是我们前面学习的**一级缓存**。

需要注意：

**Spring 单例和传统单例模式有所区别。**

- 传统单例：通常强调一个类在特定类加载环境中只有一个实例。
- Spring 单例：通常强调一个 IoC 容器中，一个 Bean 定义对应一个共享实例。

如果存在两个独立的 Spring 容器，同一个 Bean 定义可以分别创建实例。

---

## **四、代理模式：Spring AOP ⭐⭐⭐⭐⭐**

这个就是我们前面学习的内容。

**代理模式的核心思想：通过代理对象控制对目标对象的访问，并添加额外功能。**

例如：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

Spring AOP 可以为 `OrderService` 创建代理对象。

```text
外部调用
    ↓
AOP 代理对象
    ↓
开启事务
    ↓
执行 createOrder()
    ↓
提交事务 / 异常时按规则回滚
```

Spring AOP 主要通过两种方式创建代理：

- **JDK 动态代理**：基于接口。
- **CGLIB 动态代理**：基于继承。

你前面学习的 Spring AOP、三级缓存兼容 AOP，都与代理模式有关。

---

## **五、模板方法模式：JdbcTemplate ⭐⭐⭐⭐**

**模板方法模式的核心思想：将通用流程封装起来，把需要变化的部分交给使用者实现。**

例如，传统 JDBC 操作数据库需要：

```text
获取数据库连接
      ↓
创建 SQL 执行对象
      ↓
执行 SQL
      ↓
处理结果
      ↓
释放资源
```

这些步骤存在大量重复代码。

Spring 提供了 `JdbcTemplate`：

```java
@Autowired
private JdbcTemplate jdbcTemplate;

public User getUser(Long id) {

    String sql = "SELECT * FROM user WHERE id = ?";

    return jdbcTemplate.queryForObject(
        sql,
        (rs, rowNum) -> {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setName(rs.getString("name"));
            return user;
        },
        id
    );
}
```

开发者只需要关心：

- SQL 怎么写。
- 查询结果如何映射为 Java 对象。

而数据库连接获取、SQL 执行、异常转换和资源释放等通用操作，由 `JdbcTemplate` 负责。

**补充：** 严格来说，`JdbcTemplate` 不完全是经典的继承式模板方法模式，它也大量使用回调机制来实现模板化处理。

你学过的 `RedisTemplate` 同样体现了封装通用操作流程的思想。

---

## **六、观察者模式：Spring 事件机制 ⭐⭐⭐⭐**

**观察者模式的核心思想：一个对象发生事件后，通知关注该事件的其他对象。**

Spring 提供了事件发布与监听机制。

例如，用户注册成功后发送欢迎消息。

**① 定义事件**

```java
public record UserRegisterEvent(Long userId) {
}
```

**② 发布事件**

```java
@Service
public class UserService {

    @Autowired
    private ApplicationEventPublisher publisher;

    public void register(Long userId) {

        System.out.println("用户注册成功");

        publisher.publishEvent(new UserRegisterEvent(userId));
    }
}
```

**③ 监听事件**

```java
@Component
public class UserEventListener {

    @EventListener
    public void handle(UserRegisterEvent event) {

        System.out.println("发送欢迎消息：" + event.userId());
    }
}
```

执行流程：

```text
用户注册
   ↓
发布 UserRegisterEvent
   ↓
Spring 事件机制
   ↓
UserEventListener 接收事件
   ↓
发送欢迎消息
```

这样，注册逻辑就不需要直接调用发送消息的业务代码。

需要注意，Spring 事件默认是同步执行的，并不等于 RabbitMQ 这样的消息队列。

---

## **七、适配器模式：HandlerAdapter ⭐⭐⭐⭐**

**适配器模式的核心思想：将不同接口或调用方式适配成统一的处理方式。**

在 Spring MVC 中，`DispatcherServlet` 需要调用不同类型的 Handler。

但不同 Handler 的调用方式可能不同。

因此，Spring MVC 引入了 `HandlerAdapter`。

```text
HTTP 请求
    ↓
DispatcherServlet
    ↓
HandlerMapping
    ↓
找到对应 Handler
    ↓
HandlerAdapter
    ↓
调用 Handler
    ↓
返回处理结果
```

例如：

```java
@RestController
public class UserController {

    @GetMapping("/user")
    public String getUser() {
        return "Eason";
    }
}
```

对于这种 `@RequestMapping` 风格的控制器方法，Spring MVC 通常使用 `RequestMappingHandlerAdapter` 完成调用。

**因此，HandlerAdapter 让 DispatcherServlet 不必关心不同 Handler 的具体调用细节。**

---

## Q：Spring 框架中使用了哪些设计模式？


Spring 框架中使用了很多经典的设计模式。

首先是**工厂模式**，Spring 通过 BeanFactory 等容器机制统一创建和管理 Bean，实现控制反转。

其次是**单例模式**，Spring 默认使用 singleton 作用域，同一个容器中同名 Bean 通常只有一个共享实例。

第三是**代理模式**，Spring AOP 通过 JDK 动态代理或 CGLIB 创建代理对象，实现事务管理、日志记录等方法增强。


（其实掌握这三个就可以应付面试了我个人觉得）
此外，Spring 还使用了模板方法模式，例如 JdbcTemplate 封装数据库操作的通用流程；观察者模式，例如 ApplicationEventPublisher 实现事件发布与监听；以及适配器模式，例如 Spring MVC 通过 HandlerAdapter 适配不同类型的 Handler。

这些设计模式提高了 Spring 框架的扩展性，也降低了业务代码之间的耦合度。