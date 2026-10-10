Spring 框架最核心的两个思想是：**IoC（控制反转）和 AOP（面向切面编程）**。

其中，**IoC 负责管理对象、降低对象之间的耦合度；AOP 负责将公共逻辑与业务逻辑分离，减少重复代码。**

这两个思想也是 Spring 面试最重要的基础知识。

## **一、IoC：控制反转 ⭐⭐⭐⭐⭐**

IoC（Inversion of Control）的核心思想是：

**将对象的创建、依赖关系维护和生命周期管理交给 Spring 容器，而不是由程序员手动管理。**

### **1. 没有 Spring 时**

假设我们开发一个订单模块：

```java
public class OrderService {

    private OrderMapper orderMapper = new OrderMapperImpl();

    public void createOrder() {
        orderMapper.insert();
    }
}
```

这里存在一个问题：

`OrderService` 需要自己创建 `OrderMapperImpl` 对象。

如果以后更换实现类，就需要修改 `OrderService` 的代码。

这意味着两个类之间的耦合度比较高。

### **2. 使用 Spring IoC**

```java
@Service
public class OrderService {

    private final OrderMapper orderMapper;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }

    public void createOrder() {
        orderMapper.insert();
    }
}
```

现在：

- `OrderService` 由 Spring 容器创建和管理。
- `OrderMapper` 由 Spring 容器管理。
- Spring 自动将 `OrderMapper` 注入 `OrderService`。

整个过程：

```text
          Spring IoC 容器
                 │
        ┌────────┴────────┐
        ▼                 ▼
   OrderService       OrderMapper
        │                 ▲
        └──── 依赖注入 ────┘
```

**为什么叫控制反转？**

因为对象创建和依赖管理的控制权发生了转移：

```text
传统开发：

程序员 → 创建对象 → 管理依赖


Spring：

Spring 容器 → 创建对象 → 注入依赖
```

这就是控制反转。

### **3. IoC 和 DI 的关系**

这两个概念经常一起出现。

- **IoC（控制反转）**：一种设计思想，将对象管理权交给容器。
- **DI（依赖注入）**：实现 IoC 的主要方式，由容器为对象注入依赖。

**一句话：IoC 是思想，DI 是实现方式。**

---

## **二、AOP：面向切面编程 ⭐⭐⭐⭐⭐**

AOP（Aspect-Oriented Programming）的核心思想是：

**将日志记录、权限校验、事务管理等公共逻辑从业务代码中抽离出来，实现公共逻辑与业务逻辑的解耦。**

### **1. 没有 AOP 时**

假设我们有两个业务方法：

```java
public void createOrder() {
    System.out.println("记录日志");

    // 创建订单
}

public void cancelOrder() {
    System.out.println("记录日志");

    // 取消订单
}
```

可以发现：

两个方法都需要记录日志。

如果有 100 个业务方法，就可能需要重复编写 100 次日志代码。

### **2. 使用 Spring AOP**

我们可以把日志逻辑抽离出来：

```java
@Aspect
@Component
public class LogAspect {

    @Before("execution(* com.example.service.OrderService.*(..))")
    public void log() {
        System.out.println("记录日志");
    }
}
```

业务代码只需要关注自己的核心功能：

```java
@Service
public class OrderService {

    public void createOrder() {
        // 创建订单
    }

    public void cancelOrder() {
        // 取消订单
    }
}
```

执行流程：

```text
        调用业务方法
             │
             ▼
       Spring AOP 代理
             │
             ▼
         执行日志逻辑
             │
             ▼
         执行业务逻辑
```

这样就实现了：

**业务代码负责业务，公共逻辑交给 AOP。**

### **3. AOP 的底层原理**

Spring AOP 主要通过动态代理实现：

- JDK 动态代理
- CGLIB 代理

例如，我们经常使用的：

```java
@Transactional
public void createOrder() {
    // 创建订单
    // 扣减库存
}
```

Spring 声明式事务通常也是通过 AOP 代理实现的。

代理对象会在执行目标方法前开启事务，并在方法执行结束后根据结果提交或回滚事务。

---

## **三、IoC 和 AOP 有什么区别？**

|**对比**|**IoC**|**AOP**|
|---|---|---|
|核心思想|控制反转|面向切面编程|
|解决的问题|对象创建和依赖管理|公共逻辑重复、业务代码耦合|
|主要实现|Spring 容器、DI|动态代理|
|常见应用| `@Component`、`@Service`、依赖注入| `@Aspect`、`@Transactional` |
|核心价值|降低对象之间的耦合|降低公共逻辑与业务逻辑的耦合|

两者之间还有一个联系：

**Spring AOP 通常建立在 IoC 容器的基础上，由 Spring 容器创建和管理代理 Bean。**

---

## **四、面试怎么回答？⭐⭐⭐⭐⭐**

如果面试官问：

**“Spring 的核心思想是什么？”**

你可以这样回答：

Spring 的核心思想主要是 IoC 和 AOP。

首先，IoC 是控制反转，指的是将对象的创建、依赖关系维护和生命周期管理交给 Spring 容器，而不是由程序员手动管理。Spring 主要通过 DI，也就是依赖注入，来实现 IoC，从而降低对象之间的耦合度。

其次，AOP 是面向切面编程，主要用于将日志记录、权限校验、事务管理等公共逻辑从业务代码中抽离出来，实现业务逻辑与公共逻辑的解耦。Spring AOP 底层主要通过 JDK 动态代理和 CGLIB 实现。

因此，IoC 主要解决对象管理和依赖问题，而 AOP 主要解决公共逻辑与业务逻辑的解耦问题。

### **最后记住一句话**

**IoC 管理对象，AOP 增强方法。**

更准确地说：

- **IoC：把对象交给 Spring 管。**
- **DI：Spring 把依赖注入对象。**
- **AOP：在不侵入核心业务代码的情况下，通过代理增强方法。**

这三个概念理解清楚，就掌握了 Spring 框架最核心的设计思想。