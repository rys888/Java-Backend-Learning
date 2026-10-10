
Spring AOP（面向切面编程）最典型的应用包括：**声明式事务管理、日志记录、权限校验、性能监控和缓存管理**。

其中，对于 Java 后端实习面试，**声明式事务** ** `@Transactional` ** **是最重要、最典型的应用场景**。

## **一、Spring AOP 的典型应用场景**

| **应用场景**        | **具体作用**                | **常见实现**            |
| --------------- | ----------------------- | ------------------- |
| **声明式事务 ⭐⭐⭐⭐⭐** | 在业务方法执行前开启事务，执行后提交或回滚   | `@Transactional`    |
| **日志记录 ⭐⭐⭐⭐⭐**  | 统一记录接口调用、请求参数、执行结果      | `@Aspect`、`@Around` |
| **权限校验 ⭐⭐⭐⭐⭐**  | 在业务方法执行前检查用户权限          | 自定义注解 + AOP         |

需要注意：这些功能不一定全部依赖 Spring AOP。例如，Web 层权限控制也可以通过 Filter、Interceptor 或 Spring Security 实现。

---

## **二、声明式事务：@Transactional ⭐⭐⭐⭐⭐**

这是 Spring AOP 最经典的应用。

假设创建订单需要完成两个操作：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {

        // 1. 创建订单
        orderMapper.insert(order);

        // 2. 扣减库存
        stockMapper.decreaseStock(productId);
    }
}
```

我们希望：

- 两个操作都成功，则提交事务。
- 如果出现符合回滚规则的异常，则回滚事务。

Spring 通过 AOP 代理实现事务管理，简化流程：

```text
调用 createOrder()
        ↓
    AOP 代理对象
        ↓
      开启事务
        ↓
     执行业务方法
        ↓
   ┌────┴────┐
   ↓         ↓
执行成功   发生需要回滚的异常
   ↓         ↓
提交事务    回滚事务
```

**好处：** 不需要在每个业务方法中手动编写事务开启、提交和回滚代码。

需要注意，`@Transactional` 默认主要对 `RuntimeException` 和 `Error` 进行回滚。

---

## **三、日志记录 ⭐⭐⭐⭐⭐**

假设我们希望记录所有 Service 方法的调用情况。

如果不使用 AOP，就需要在每个方法中重复编写日志代码。

使用 AOP：

```java
@Aspect
@Component
public class LogAspect {

    @Before("execution(* com.example.service.*.*(..))")
    public void log() {
        System.out.println("开始执行方法");
    }
}
```

执行流程：

```text
调用业务方法
      ↓
AOP 执行日志记录
      ↓
执行业务方法
```

这样就实现了**日志逻辑和业务逻辑的分离**。

实际项目中，还可以通过 `@Around` 记录请求参数、方法执行结果和执行时间，但应避免记录密码、Token 等敏感信息。

---

## Q：Spring AOP 有哪些典型的应用场景？


Spring AOP 主要用于将公共逻辑与业务逻辑分离，典型应用包括声明式事务、日志记录、权限校验、性能监控和缓存管理。

其中最典型的是 Spring 的声明式事务管理，例如 `@Transactional`，Spring 会通过 AOP 代理在业务方法执行前开启事务，并根据执行结果提交或回滚事务。

此外，在实际项目中，我们也可以通过自定义注解结合 AOP 实现权限校验，或者通过 `@Around` 环绕通知记录方法执行时间。

这些功能的共同特点是，不需要在每个业务方法中重复编写公共逻辑，从而降低代码耦合度，提高可维护性。
