IoC 和 AOP 是 Spring 的两个核心思想，但两者的底层实现机制完全不一样。

**IoC 是控制反转**，它是一种创建和获取对象的技术思想。传统开发方式是直接用 `new` 关键字创建对象，用 IoC 的方式就不自己 new 了，而是让 IoC 容器帮忙实例化对象、维护对象之间的依赖关系，依赖注入（DI）就是实现这种思想的一种方式。对象不用自己管依赖，都交给容器，对象之间的耦合度自然就降下来了。

**AOP 是面向切面编程**，作用是把那些与业务无关、却为业务模块所共同调用的逻辑封装起来，减少系统的重复代码，降低模块间的耦合度。Spring AOP 基于动态代理实现：被代理对象实现了接口，Spring AOP 默认会使用 JDK Proxy 创建代理对象；没有实现接口，则会使用 CGLIB 生成被代理对象的子类作为代理。注意：自 Spring Boot 2.0 起，默认配置改为倾向使用 CGLIB 代理。

所以最核心的概括就是两句话：**IoC 主要通过反射、依赖注入和 Bean 生命周期管理实现；AOP 主要通过动态代理实现，包括 JDK 动态代理和 CGLIB 动态代理。** 不过这只是最核心的概括，面试里如果被追问底层原理，还需要讲到 Spring 容器和 Bean 后置处理器。

---

## **一、IoC 是通过什么机制实现的？⭐⭐⭐⭐⭐**

IoC（控制反转）的核心是：**将对象的创建、依赖注入和生命周期管理交给 Spring 容器。** Spring IoC 的实现主要涉及三个机制。

### **1. 反射机制：创建 Bean 对象**

```java
@Service
public class UserService {

    public void login() {
        System.out.println("用户登录");
    }
}
```

Spring 启动时，会通过组件扫描等方式发现 `@Service` 注解标记的类，然后利用反射机制创建对象。简化理解：

```java
Class<?> clazz = Class.forName("com.example.UserService");

Object bean = clazz.getDeclaredConstructor().newInstance();
```

`Class.forName()` 先根据全限定类名拿到对应的 Class 对象，`getDeclaredConstructor()` 取到无参构造器，最后 `newInstance()` 才真正把对象创建出来。这里需要注意，Spring 并不是简单地对所有 Bean 都执行这段反射代码，实际创建 Bean 时还可能走工厂方法、构造器解析等方式。**反射是 Spring 创建和操作 Bean 的重要底层技术。**

### **2. 依赖注入：维护 Bean 之间的依赖关系**

```java
@Service
public class OrderService {

    private final OrderMapper orderMapper;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }
}
```

Spring 创建 `OrderService` 时，会发现它需要一个 `OrderMapper` 对象，于是先去容器里把这个依赖找出来，再通过构造器传进去：

```text
Spring IoC 容器
      │
      ▼
解析 OrderService 的依赖
      │
      ▼
查找 OrderMapper Bean
      │
      ▼
创建 OrderService
      │
      ▼
通过构造器注入 OrderMapper
```

Spring 支持构造器注入、Setter 注入、字段注入等方式。其中字段注入通常是通过反射给成员变量设置值。

### **3. BeanFactory：IoC 容器的核心接口**

Spring 使用容器管理 Bean，其中两个重要接口是 **`BeanFactory`** 和 **`ApplicationContext`**：`BeanFactory` 是 Spring IoC 容器的基础接口，提供 Bean 获取等能力；`ApplicationContext` 在它的基础上又提供了事件发布、资源加载、国际化等更多功能。

```java
ApplicationContext context =
        new AnnotationConfigApplicationContext(AppConfig.class);

UserService userService =
        context.getBean(UserService.class);
```

这里没有 `new UserService()`，对象是直接从容器里取出来的，实例化过程全部由容器负责，这就是「通过容器获取 Bean，而不是手动创建对象」。

### **IoC 的整体实现流程**

```text
         Spring 容器启动
                │
                ▼
       扫描注解 / 读取配置
                │
                ▼
       解析 BeanDefinition
                │
                ▼
         实例化 Bean
                │
                ▼
           依赖注入
                │
                ▼
         Bean 初始化
                │
                ▼
       BeanPostProcessor 处理
                │
                ▼
        Bean 交给容器管理
```

这里的 `BeanDefinition` 可以理解为 **Bean 的定义信息**，记录 Bean 类型、作用域、依赖等配置；`BeanPostProcessor` 则允许 Spring 在 Bean 初始化前后进行扩展处理。需要注意，实际执行时后置处理器的前置和后置回调分别发生在初始化方法之前和之后，并不是都集中在初始化完成后。

**所以，IoC 并不是单纯依靠反射实现的，而是依靠 Spring 容器、BeanDefinition、反射和依赖注入等机制共同实现。**

---

## **二、AOP 是通过什么机制实现的？⭐⭐⭐⭐⭐**

AOP（面向切面编程）主要通过**动态代理**实现。

假设有个创建订单的方法，现在希望在创建订单前记录日志：

```java
@Service
public class OrderService {

    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

如果使用 Spring AOP，就把日志逻辑抽成一个切面：

```java
@Aspect
@Component
public class LogAspect {

    @Before("execution(* com.example.service.OrderService.createOrder(..))")
    public void before() {
        System.out.println("记录日志");
    }
}
```

`@Aspect` 声明这是一个切面类，`@Before` 里的 `execution` 表达式指定要切到哪个方法，方法体就是增强逻辑。Spring 会为 `OrderService` 创建代理对象，调用方拿到的其实是代理对象，执行过程：

```text
         调用 createOrder()
                 │
                 ▼
          Spring 代理对象
                 │
                 ▼
           执行前置通知
                 │
                 ▼
          执行目标方法
                 │
                 ▼
             返回结果
```

Spring AOP 主要使用两种动态代理。

### **1. JDK 动态代理**

JDK 动态代理主要基于接口实现，先有接口：

```java
public interface OrderService {
    void createOrder();
}
```

再有实现类：

```java
@Service
public class OrderServiceImpl implements OrderService {

    @Override
    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

JDK 动态代理通过 `Proxy` 和 `InvocationHandler` 等机制创建代理对象：由 `Proxy` 在运行时生成一个实现了同样接口的代理类，所有方法调用都会被转发到 `InvocationHandler` 的 `invoke()` 里，增强逻辑写在这里，增强完再调用目标方法。

```text
OrderService 接口
       │
       ├── OrderServiceImpl（目标对象）
       │
       └── JDK Proxy（代理对象）
                    │
                    ▼
               增强目标方法
```

### **2. CGLIB 动态代理**

CGLIB 主要通过**生成目标类的子类**实现代理。假设目标类没有实现接口：

```java
public class OrderService {

    public void createOrder() {
        System.out.println("创建订单");
    }
}
```

可以简化理解为生成了这样一个子类：

```java
public class OrderServiceProxy extends OrderService {

    @Override
    public void createOrder() {
        System.out.println("记录日志");

        super.createOrder();
    }
}
```

代理类重写目标方法，先在方法里做增强，再用 `super.createOrder()` 执行原来的逻辑。实际 CGLIB 生成的代理类比这个例子复杂，但原理类似。

需要注意：**由于 CGLIB 依赖继承，因此无法代理 `final` 类，也无法通过重写增强 `final` 方法。**

### **JDK 动态代理和 CGLIB 的区别**

|**对比**|**JDK 动态代理**|**CGLIB 动态代理**|
|---|---|---|
|实现原理|基于接口生成代理对象|生成目标类的子类|
|是否需要接口|需要|不需要|
|核心机制| `Proxy`、`InvocationHandler` |字节码生成、方法拦截|
|主要限制|只能代理接口中暴露的方法|无法重写 `final` 方法|

在 Spring Framework 的常见默认配置下，有合适的接口时通常使用 JDK 动态代理，否则使用 CGLIB。不过，**Spring Boot 2.x/3.x 的常见自动配置默认倾向使用 CGLIB 类代理**，可以通过配置修改。

---

## **三、AOP 和 IoC 底层有什么联系？**

这是一个值得掌握的知识点：**Spring AOP 实际上依赖 IoC 容器。** 例如：

```java
@Service
public class OrderService {

    @Transactional
    public void createOrder() {
        // 创建订单
    }
}
```

Spring 在创建 Bean 的过程中，可以通过 `BeanPostProcessor` 机制判断是否需要为 Bean 创建 AOP 代理，Spring AOP 的自动代理创建器本身就是一种 Bean 后置处理器。简化流程：

```text
          Spring IoC 容器
                 │
                 ▼
           创建目标 Bean
                 │
                 ▼
       BeanPostProcessor
                 │
                 ▼
         判断是否需要 AOP
                 │
          ┌──────┴──────┐
          │             │
         不需要        需要
          │             │
          ▼             ▼
       原始 Bean     创建代理对象
          │             │
          └──────┬──────┘
                 │
                 ▼
           交给容器管理
```

因此，当其他 Bean 注入 `OrderService` 时，拿到的可能不是原始对象，而是经过 AOP 增强的代理对象。

这也解释了为什么 `@Transactional` 有时会失效：**同一个类内部使用 `this` 调用事务方法，走的是原始对象，没有经过 Spring 代理对象，因此无法触发事务增强。**

---

## **四、面试怎么回答？⭐⭐⭐⭐⭐**

**Q：Spring 的 IoC 和 AOP 分别是通过什么机制实现的？**

Spring 的 IoC 主要通过 Spring 容器、反射和依赖注入等机制实现。Spring 启动时会通过组件扫描或者配置文件获取 Bean 的定义信息，将其封装为 BeanDefinition，然后由 BeanFactory 根据这些定义创建 Bean，并完成依赖注入、初始化和生命周期管理，从而实现对象控制权的反转。

而 Spring AOP 主要通过动态代理实现，包括 JDK 动态代理和 CGLIB 动态代理。JDK 动态代理基于接口生成代理对象，CGLIB 则通过生成目标类的子类实现方法增强。

此外，Spring AOP 与 IoC 容器密切相关，Spring 可以通过 BeanPostProcessor 在 Bean 创建过程中生成 AOP 代理对象，从而实现日志记录、权限校验和声明式事务等功能。


- **IoC：容器管理 + BeanDefinition + 反射 + 依赖注入。**
- **AOP：动态代理（JDK / CGLIB）+ BeanPostProcessor。**
