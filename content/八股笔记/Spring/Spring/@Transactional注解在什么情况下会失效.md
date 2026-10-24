
[[#Q：]]

`@Transactional` 是 Spring 提供的声明式事务注解，底层主要基于 **AOP 动态代理 + TransactionInterceptor（事务拦截器）** 实现。

简单来说，加了注解的业务方法并不是自己在管事务，外面还包了一层代理对象：代理对象在方法执行前开启事务，方法正常返回就提交，抛出异常就按回滚规则决定回滚还是提交。

所以理解事务失效，关键就是两点：**方法调用必须经过 Spring AOP 代理对象**；**异常必须满足事务回滚条件，并且能被事务拦截器感知**。下面列的那些场景，基本都能对应到这两条上。

## 一、@Transactional 常见的失效场景

### 1. 同一个类内部调用（最常考）

```java
@Service
public class OrderService {

    public void createOrder() {
        // 内部调用
        saveOrder();
    }

    @Transactional
    public void saveOrder() {
        // 插入订单
        // 更新库存
    }
}
```

调用过程：

```text
外部调用 createOrder()
        ↓
Spring 代理对象
        ↓
目标对象 createOrder()
        ↓
this.saveOrder()
        ↓
直接调用目标方法
        ↓
绕过 AOP 事务拦截器
        ↓
@Transactional 不生效
```

问题出在 `this.saveOrder()` 这一行。外面进来的 `createOrder()` 确实走了代理对象，但一旦进入目标对象内部，`this` 指向的就是目标对象本身，再调 `saveOrder()` 属于普通方法调用，事务拦截器根本没机会插进来。

解决方案是把 `saveOrder()` 拆到另一个 Spring Bean 中，注入进来再调：

```java
@Service
public class OrderService {

    @Autowired
    private OrderTransactionService transactionService;

    public void createOrder() {
        transactionService.saveOrder();
    }
}

@Service
public class OrderTransactionService {

    @Transactional
    public void saveOrder() {
        // 插入订单
        // 更新库存
    }
}
```

这样调用就重新经过 Spring 代理对象了。

---

### 2. 异常被 try-catch 捕获，没有继续抛出

```java
@Transactional
public void saveOrder() {
    try {
        orderMapper.insert(order);

        int a = 1 / 0;

    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

虽然发生了异常，但异常已经被 `catch` 捕获。Spring 事务拦截器看到的是方法正常返回，因此默认会提交事务。

⚠️ 注意：这里容易搞混——异常确实发生了，但拦截器感知不到，等于没发生，事务照样提交。

**解决方案：** 捕获异常后重新抛出，或者手动标记事务回滚。

```java
@Transactional
public void saveOrder() {
    try {
        orderMapper.insert(order);

        int a = 1 / 0;

    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}
```

还有一个细节：如果内部操作已经将事务标记为 rollback-only，即使外层捕获异常，事务仍可能回滚。

---

### 3. 方法不是 public

比如：

```java
@Service
public class OrderService {

    @Transactional
    private void saveOrder() {
        // 数据库操作
    }
}
```

Spring AOP 无法通过代理增强这个 `private` 方法。另外，不同代理方式对方法可见性的支持也不一样：

|**方法类型**|**JDK 动态代理**|**CGLIB 代理**|
|---|---|---|
|public|支持接口方法|支持|
|protected|不适用|Spring 6+ 默认可支持|
|包级私有|不适用|Spring 6+ 默认可支持|
|private|不支持|不支持|

面试里问到这里，直接答：**将 `@Transactional` 放在 public 方法上最稳妥。**

---

### 4. 方法被 final 修饰

```java
@Service
public class OrderService {

    @Transactional
    public final void saveOrder() {
        // 数据库操作
    }
}
```

如果 Spring 使用 CGLIB 代理，由于 `final` 方法不能被子类重写，因此无法对它进行事务增强。

但这里不能一刀切，**如果使用 JDK 动态代理，且该方法是接口方法，目标实现方法上的 `final` 并不必然阻止事务代理。** 所以不能简单地说所有 `final` 方法都会导致事务失效。

---

### 5. 对象不是 Spring 容器管理的

```java
OrderService service = new OrderService();

service.saveOrder();
```

虽然 `saveOrder()` 上有 `@Transactional`，但这里通过 `new` 创建的是普通 Java 对象。Spring 没有机会为它创建 AOP 代理，因此事务不会生效。

正确做法是让 Spring 管理对象：

```java
@Service
public class OrderService {

    @Transactional
    public void saveOrder() {
        // 数据库操作
    }
}
```

然后通过依赖注入获取 Bean。

---

### 6. 开启了新线程执行数据库操作

```java
@Transactional
public void saveOrder() {

    orderMapper.insert(order);

    new Thread(() -> {
        stockMapper.updateStock();
    }).start();
}
```

这里存在两个线程：

```text
主线程
  │
  ├── 开启 Spring 事务
  │
  └── 插入订单

新线程
  │
  └── 更新库存
```

Spring 的普通声明式事务通常通过 `ThreadLocal` 将事务资源绑定到当前线程，因此**事务上下文不会自动传播到新线程**。即使主线程事务回滚，也无法保证新线程中的数据库操作一起回滚。

使用 `@Async`、`CompletableFuture` 等异步方式时，也是同一个问题。

---

## Q：
`@Transactional` 的失效场景主要可以从 AOP 代理机制和事务回滚机制两个方面理解。

**第一，同类内部调用。** 比如通过 `this` 调用带有 `@Transactional` 的方法，由于没有经过 Spring 代理对象，所以事务增强不会生效。

**第二，异常被捕获。** 如果方法内部发生异常，但被 `try-catch` 捕获且没有重新抛出，事务拦截器可能认为方法正常执行，从而提交事务。

**第三，方法无法被代理。** 比如 private 方法无法被 Spring AOP 增强，CGLIB 也无法增强 final 方法。

**第四，对象没有交给 Spring 管理。** 如果通过 `new` 创建对象，就不会获得 Spring 的事务代理。

**第五，跨线程执行。** Spring 的事务上下文通常绑定在当前线程的 ThreadLocal 中，新线程不会自动继承原线程的事务。

所以排查事务失效时，顺序是：先确认方法是否经过 Spring 代理，再检查异常是否正确传播，最后看事务回滚规则和传播行为是否符合预期。

## 三、结合之前学过的 AOP，回顾这个核心流程

```text
调用 Spring Bean 的方法
          │
          ▼
     AOP 代理对象
          │
          ▼
    TransactionInterceptor
          │
          ├── 开启事务
          │
          ▼
       执行业务方法
          │
          ├── 正常返回 ──→ 提交事务
          │
          └── 抛出异常
                  │
                  ▼
           判断回滚规则
                  │
                  ├── 满足条件 → 回滚
                  │
                  └── 不满足 → 提交
```

把上面的失效场景往这张图上套，就很清楚了：

- 调用没走到 AOP 代理对象 → 同类内部调用、private 方法、final 方法（CGLIB）、`new` 出来的对象
- 异常没传出去 → try-catch 捕获后没有重新抛出
- 事务跨了线程 → 新线程拿不到主线程 ThreadLocal 里绑定的事务资源
