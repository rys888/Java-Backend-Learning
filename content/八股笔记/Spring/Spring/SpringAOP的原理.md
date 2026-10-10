Spring AOP（面向切面编程）的核心原理是：**基于动态代理，在不修改原有业务代码的情况下，对目标方法进行增强。**

Spring AOP 主要涉及三个核心机制：

1. **动态代理**：通过 JDK 动态代理或 CGLIB 创建代理对象。
2. **BeanPostProcessor**：在 Spring Bean 创建过程中，为符合条件的 Bean 创建代理对象。
3. **拦截器链**：在调用目标方法时，按照顺序执行前置、环绕、后置等增强逻辑。

## **一、Spring AOP 的基本原理 ⭐⭐⭐⭐⭐**

假设有一个订单业务：

```java
@Service
public class OrderService {

    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

现在希望在执行 `createOrder()` 前后记录日志。

可以使用 AOP：

```java
@Aspect
@Component
public class LogAspect {

    @Around("execution(* com.example.service.OrderService.createOrder(..))")
    public Object log(ProceedingJoinPoint joinPoint) throws Throwable {

        System.out.println("方法执行前");

        Object result = joinPoint.proceed();

        System.out.println("方法执行后");

        return result;
    }
}
```

Spring 不需要修改 `OrderService` 的源代码，而是为它创建一个代理对象。

执行过程：

```text
          调用 createOrder()
                  │
                  ▼
            AOP 代理对象
                  │
                  ▼
            执行前置逻辑
                  │
                  ▼
            执行目标方法
                  │
                  ▼
            执行后置逻辑
                  │
                  ▼
               返回结果
```

**关键点：外部调用的是代理对象，而不是直接调用原始对象。**

代理对象负责执行增强逻辑，并在适当的时候调用目标方法。

---

## **二、Spring AOP 如何创建代理对象？⭐⭐⭐⭐⭐**

Spring AOP 主要使用两种动态代理技术。

### **1. JDK 动态代理**

JDK 动态代理基于接口实现。

例如：

```java
public interface OrderService {
    void createOrder();
}
```

```java
@Service
public class OrderServiceImpl implements OrderService {

    @Override
    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

Spring 可以通过 JDK 动态代理生成实现相同接口的代理对象。

```text
        OrderService 接口
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
OrderServiceImpl     JDK 代理对象
   （目标对象）             │
       ▲                  │
       └──── 调用目标方法 ──┘
```

```
UserService target = new UserServiceImpl();

UserService proxy = (UserService) Proxy.newProxyInstance(
    target.getClass().getClassLoader(),
    target.getClass().getInterfaces(),
    (proxyObj, method, args) -> {

        System.out.println("前置日志");

        Object result = method.invoke(target, args);

        System.out.println("后置日志");

        return result;
    }
);

proxy.login();
```

### **2. CGLIB 动态代理**

CGLIB 主要通过**生成目标类的子类**实现动态代理。

例如：

```java
public class OrderService {

    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

CGLIB 生成的代理对象，可以简化理解为：

```java
public class OrderServiceProxy extends OrderService {

    @Override
    public void createOrder() {

        System.out.println("方法执行前");

        super.createOrder();

        System.out.println("方法执行后");
    }
}
```

实际上，CGLIB 还涉及字节码生成和方法拦截等机制。

**需要注意：**

由于 CGLIB 依赖继承，因此不能代理 `final` 类，也无法通过重写增强 `final` 方法。

### **两种代理的区别**

|**对比**|**JDK 动态代理**|**CGLIB 动态代理**|
|---|---|---|
|实现原理|基于接口生成代理对象|通过继承生成子类|
|是否需要接口|需要|不需要|
|底层技术|Proxy、InvocationHandler|字节码生成、方法拦截|
|主要限制|主要增强接口方法|无法增强 final 方法|

在 Spring Framework 默认代理策略下，有合适的接口时通常使用 JDK 动态代理，否则使用 CGLIB。

不过，**Spring Boot 2.x/3.x 的常见默认配置倾向使用 CGLIB**。

---

## **五、Spring AOP 为什么会失效？⭐⭐⭐⭐⭐**

理解了动态代理，就能解释一个经典面试问题：

**为什么同一个类内部调用**  `@Transactional`  **方法，事务可能不生效？**

例如：

```java
@Service
public class OrderService {

    public void create() {
        this.saveOrder();
    }

    @Transactional
    public void saveOrder() {
        // 保存订单
    }
}
```

当外部通过 Spring 代理调用 `create()` 时：

```text
外部调用
   │
   ▼
Spring AOP 代理对象
   │
   ▼
目标对象 create()
   │
   ▼
this.saveOrder()
   │
   ▼
直接调用目标对象的方法
   │
   ▼
没有经过事务代理拦截
```

由于 `this.saveOrder()` 是目标对象内部的方法调用，通常不会重新经过 Spring AOP 代理。

因此，`saveOrder()` 上的 `@Transactional` 不会因为这次内部调用而单独触发事务增强。

**这就是 Spring AOP 自调用失效的原因。**

需要注意，如果外层 `create()` 已经开启事务，那么内部方法仍可能运行在已有事务中。

---

## **六、面试怎么回答？⭐⭐⭐⭐⭐**

如果面试官问：

**“Spring AOP 的底层实现原理是什么？”**

你可以这样回答：

Spring AOP 的核心原理是动态代理，主要通过 JDK 动态代理和 CGLIB 动态代理，在不修改原有业务代码的情况下对目标方法进行增强。

首先，Spring 在 Bean 创建过程中，会通过 BeanPostProcessor 相关机制判断当前 Bean 是否需要 AOP 增强。如果需要，就为其创建代理对象，并将代理对象交给 Spring 容器管理。

其中，JDK 动态代理主要基于接口实现，而 CGLIB 动态代理通过生成目标类的子类实现。

当外部调用代理对象的方法时，Spring 会通过方法拦截器链执行前置、环绕、后置等通知，并在适当的时候调用目标方法。

因此，Spring AOP 的本质就是通过动态代理拦截方法调用，实现日志记录、权限校验、声明式事务等公共功能。

---

### **七、最后记住这张流程图**

```text
Spring IoC 容器创建 Bean
           ↓
BeanPostProcessor 判断是否需要 AOP
           ↓
     创建动态代理对象
           ↓
     JDK Proxy / CGLIB
           ↓
      代理对象交给容器
           ↓
       外部调用方法
           ↓
      进入方法拦截器链
           ↓
        执行增强逻辑
           ↓
        执行目标方法
           ↓
          返回结果
```

**一句话总结：**

**Spring AOP 通过 BeanPostProcessor 创建动态代理对象，再通过拦截器链对目标方法进行增强。**

对于 Java 后端实习面试，你只需要牢牢记住三个关键词：

**BeanPostProcessor → 动态代理（JDK/CGLIB）→ 拦截器链。**