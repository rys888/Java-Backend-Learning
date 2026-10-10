
[[#Q：Spring 声明式事务的实现原理是什么？]]

Spring 声明式事务是 Java 后端面试的高频考点，它和我们前面学习的 **Spring AOP、动态代理、IoC 容器** 有很大关系。

**Spring 声明式事务的核心原理：基于 AOP 动态代理，在目标方法执行前开启事务，方法执行成功后提交事务，发生符合回滚规则的异常时回滚事务。**

但要注意：**AOP 负责拦截方法，真正的事务管理由**  `PlatformTransactionManager`  **完成。**

## **一、什么是声明式事务？⭐⭐⭐⭐⭐**

假设我们需要完成一个订单业务：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {

        // 1. 扣减库存
        stockMapper.reduceStock();

        // 2. 创建订单
        orderMapper.insertOrder();
    }
}
```

这里有两个数据库操作：

1. 扣减库存。
2. 创建订单。

我们希望这两个操作要么全部成功，要么全部回滚。

因此使用：

```java
@Transactional
```

Spring 就会为这个方法提供事务管理。

如果不使用声明式事务，我们可能需要手动编写：

```java
Connection connection = dataSource.getConnection();

try {
    connection.setAutoCommit(false);

    // 执行业务 SQL

    connection.commit();

} catch (Exception e) {

    connection.rollback();

    throw e;

} finally {
    connection.close();
}
```

而声明式事务将这些重复操作交给 Spring 管理。

---

## **二、Spring 声明式事务的实现原理 ⭐⭐⭐⭐⭐**

Spring 声明式事务主要涉及三个核心组件：

|**组件**|**作用**|
|---|---|
|**AOP 动态代理**|拦截带有事务增强的方法|
|**TransactionInterceptor**|执行事务增强逻辑|
|**PlatformTransactionManager**|真正管理事务的开启、提交和回滚|

其中，`TransactionInterceptor` 是理解声明式事务的关键。

### **1. Spring 创建事务代理对象**

假设：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        // 业务逻辑
    }
}
```

Spring 在创建 Bean 时，会识别相应的事务配置，并通过 AOP 机制为需要增强的 Bean 创建代理对象。

代理方式仍然是我们之前学习的：

- JDK 动态代理：基于接口。
- CGLIB 动态代理：基于继承。

因此，其他组件注入的 `OrderService` 可能实际上是一个代理对象。

```text
        OrderController
               │
               ▼
       OrderService 代理对象
               │
               ▼
        TransactionInterceptor
               │
               ▼
       OrderService 原始对象
```

### **2. TransactionInterceptor 拦截方法**

当我们调用：

```java
orderService.createOrder();
```

实际上会先进入代理对象的事务拦截逻辑。

简化执行流程：

```text
       调用 createOrder()
                │
                ▼
         AOP 代理对象
                │
                ▼
       TransactionInterceptor
                │
                ▼
          获取事务配置
                │
                ▼
          开启或加入事务
                │
                ▼
          执行业务方法
                │
         ┌──────┴──────┐
         ▼             ▼
       正常执行       发生异常
         │             │
         ▼             ▼
       提交事务      判断回滚规则
                       │
                       ▼
                   回滚或提交
```

注意：如果当前线程已经存在事务，Spring 还会根据事务传播行为决定是否加入已有事务，而不是每次都开启新事务。

### **3. PlatformTransactionManager 管理事务**

`TransactionInterceptor` 本身不直接操作数据库事务，而是调用事务管理器。

核心接口：

```java
public interface PlatformTransactionManager {

    TransactionStatus getTransaction(TransactionDefinition definition);

    void commit(TransactionStatus status);

    void rollback(TransactionStatus status);
}
```

三个方法分别用于：

- `getTransaction()`：根据事务定义获取事务，必要时开启新事务。
- `commit()`：提交事务。
- `rollback()`：回滚事务。

常见实现：

|**事务管理器**|**使用场景**|
|---|---|
| `DataSourceTransactionManager` |JDBC、MyBatis 等|
| `JpaTransactionManager` |Spring Data JPA、Hibernate|
| `JtaTransactionManager` |JTA 事务环境|

对于你使用的 **Spring Boot + MyBatis + MySQL** 项目，通常使用 `DataSourceTransactionManager`，在较新的 Spring 版本中也可能使用其子类 `JdbcTransactionManager`。

---

## **三、Spring 如何保证多个 SQL 属于同一个事务？⭐⭐⭐⭐⭐**

这里就涉及另一个重要知识点：

**ThreadLocal。**

我们知道，MySQL 的事务通常与数据库连接有关。

如果两个 SQL 使用不同的数据库连接，就无法简单地保证它们属于同一个本地事务。

因此，Spring 会通过 `TransactionSynchronizationManager` 管理当前线程绑定的事务资源。

简化理解：

```text
          当前业务线程
                │
                ▼
          ThreadLocal
                │
                ▼
        数据库连接 Connection
                │
        ┌───────┴───────┐
        ▼               ▼
    扣减库存 SQL     创建订单 SQL
        │               │
        └───────┬───────┘
                ▼
           同一个事务
```

执行过程：

1. Spring 事务管理器获取数据库连接。
2. 根据需要关闭自动提交，开启数据库事务。
3. 将连接相关资源绑定到当前线程。
4. MyBatis 等通过 Spring 的事务资源管理机制获取当前事务关联的连接。
5. 多个数据库操作使用同一事务连接。
6. 事务结束后提交或回滚，并清理线程绑定的资源。

因此，**Spring 通过事务管理器和 ThreadLocal 资源绑定机制，让同一线程中的多个数据库操作参与同一个事务。**

这里的 ThreadLocal 并不是直接保存所有事务数据，而是保存当前线程关联的资源和事务状态信息。

---

## **四、为什么 @Transactional 有时候会失效？⭐⭐⭐⭐⭐**

这也是面试最喜欢追问的地方。

### **1. 同类内部调用**

```java
@Service
public class OrderService {

    public void createOrder() {
        this.saveOrder();
    }

    @Transactional
    public void saveOrder() {
        // 保存订单
    }
}
```

调用：

```java
orderService.createOrder();
```

执行流程：

```text
外部调用
    ↓
AOP 代理对象
    ↓
目标对象 createOrder()
    ↓
this.saveOrder()
    ↓
没有重新经过 AOP 代理
    ↓
@Transactional 未单独生效
```

**原因：Spring 声明式事务通常基于代理实现，而** ** `this` ** **内部调用绕过了代理对象。**

### **2. 异常被捕获，没有继续抛出**

```java
@Transactional
public void createOrder() {

    try {
        orderMapper.insertOrder();

        int a = 1 / 0;

    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

这里虽然发生了异常，但是异常被捕获，没有继续向事务拦截器传播。

如果没有其他代码将事务标记为回滚，Spring 会认为方法正常结束，可能提交事务。

### **3. 异常不符合默认回滚规则**

```java
@Transactional
public void createOrder() throws IOException {

    throw new IOException("文件读取失败");
}
```

Spring 默认对以下异常回滚：

- `RuntimeException`
- `Error`

而普通受检异常默认不会触发回滚。

可以使用：

```java
@Transactional(rollbackFor = Exception.class)
```

指定更广泛的回滚规则。

### **4. 方法没有经过 Spring 管理的代理对象**

例如：

```java
OrderService service = new OrderService();

service.createOrder();
```

这里使用 `new` 手动创建对象，而不是从 Spring 容器获取代理对象。

因此不会自动获得 Spring AOP 事务增强。

此外，非 public 方法、final 方法等是否能够被事务增强，还与代理方式和 Spring 版本有关，不能简单认为所有情况都能生效。

---

## Q：Spring 声明式事务的实现原理是什么？

Spring 声明式事务主要基于 AOP 动态代理实现。

当 Spring 发现 Bean 中存在需要事务增强的方法时，会通过 AOP 机制创建代理对象。

当外部调用带有 `@Transactional` 的方法时，首先会经过代理对象，由 `TransactionInterceptor` 拦截方法调用。

随后，`TransactionInterceptor` 根据事务配置调用 `PlatformTransactionManager` 获取事务，并在事务上下文中执行目标方法。

如果方法正常执行，就提交事务；如果发生符合回滚规则的异常，就回滚事务。


因此，Spring 声明式事务的核心就是 **AOP 动态代理 + TransactionInterceptor + PlatformTransactionManager + ThreadLocal 事务资源管理机制**。

---

## **六、最后记住这张图**

```text
            @Transactional
                  │
                  ▼
          Spring AOP 动态代理
                  │
                  ▼
         TransactionInterceptor
                  │
                  ▼
       PlatformTransactionManager
                  │
                  ▼
          获取 / 开启事务
                  │
                  ▼
        ThreadLocal 绑定事务资源
                  │
                  ▼
            执行业务 SQL
                  │
           ┌──────┴──────┐
           ▼             ▼
        正常执行       符合规则的异常
           │             │
           ▼             ▼
        提交事务        回滚事务
                  │
                  ▼
           清理事务资源
```

**一句话总结：Spring 通过 AOP 代理拦截** ** `@Transactional` ** **方法，由** ** `TransactionInterceptor` ** **调用事务管理器完成事务控制，并通过 ThreadLocal 管理当前线程的事务资源。**

对于 Java 后端实习面试，建议重点掌握四个关键词：

**AOP 动态代理 → TransactionInterceptor → PlatformTransactionManager → ThreadLocal。**