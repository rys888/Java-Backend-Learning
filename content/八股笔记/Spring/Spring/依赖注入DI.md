
[[#Q：依赖注入了解吗？Spring 是怎么实现依赖注入的？]]
[[#Q：@Autowired 和 @Resource 有什么区别？]]


依赖注入（Dependency Injection，简称 **DI**）是 Spring IoC 的核心实现方式之一。

简单来说，**依赖注入就是对象不需要自己创建所依赖的对象，而是由 Spring 容器负责创建，并将依赖对象注入进去**——创建和注入这两件事都不归对象自己管了。

## 一、什么是依赖注入？

假设现在开发一个订单模块，`OrderService` 需要使用 `OrderMapper` 操作数据库。

### **1. 不使用依赖注入**

```java
public class OrderService {

    private OrderMapper orderMapper = new OrderMapperImpl();

    public void createOrder() {
        orderMapper.insert();
    }
}
```

这里的问题在于：`OrderService` 需要自己创建 `OrderMapperImpl` 对象。如果以后需要更换 `OrderMapper` 的实现类，就可能需要修改 `OrderService` 的代码，**这意味着两个类之间的耦合度比较高。**

### **2. 使用 Spring 依赖注入**

```java
@Service
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;

    public void createOrder() {
        orderMapper.insert();
    }
}
```

此时 `OrderService` 由 Spring 容器创建，`OrderMapper` 由 Spring 容器管理，Spring 自动将 `OrderMapper` 注入 `OrderService`：

```text
          Spring IoC 容器
                 │
        ┌────────┴────────┐
        ▼                 ▼
   OrderService       OrderMapper
        │                 ▲
        └──── 依赖注入 ────┘
```

因此，**依赖注入的核心价值就是降低对象之间的耦合度，让对象只需要关注自身业务逻辑。**

---

## **二、Spring 有哪几种依赖注入方式？⭐⭐⭐⭐⭐**

Spring 主要支持三种依赖注入方式。

### **1. 构造器注入（推荐）**

通过构造方法注入依赖对象。

```java
@Service
public class OrderService {

    private final OrderMapper orderMapper;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }
}
```

Spring 创建 `OrderService` 时，会先找到对应的 `OrderMapper` Bean，再通过构造方法将其传入。

**优点：**

- 依赖关系明确。
- 可以使用 `final` 修饰成员变量。
- 方便进行单元测试。
- 能够保证对象创建完成时，必需的依赖已经提供。

现在的 Spring 里，如果类只有一个构造方法，通常不需要添加 `@Autowired`。**实际开发更推荐构造器注入。**

### **2. Setter 注入**

通过 Setter 方法注入依赖对象。

```java
@Service
public class OrderService {

    private OrderMapper orderMapper;

    @Autowired
    public void setOrderMapper(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }
}
```

Spring 会先创建 `OrderService` 对象，再调用 Setter 方法注入 `OrderMapper`，适合一些可选依赖或需要重新配置的场景。

### **3. 字段注入**

直接通过注解注入成员变量。

```java
@Service
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;
}
```

这是很多 Spring Boot 教学项目中常见的写法，优点是代码简洁，但缺点也比较明显：

- 依赖关系不如构造器注入明确。
- 不方便脱离 Spring 容器进行单元测试。
- 不利于使用 `final` 保证依赖不可重新赋值。

因此，虽然字段注入使用方便，但**实际开发通常更推荐构造器注入。**

### **三种方式总结**

|**注入方式**|**实现机制**|**推荐程度**|
|---|---|---|
|构造器注入|调用构造方法传入依赖|⭐⭐⭐⭐⭐|
|Setter 注入|调用 Setter 方法传入依赖|⭐⭐⭐|
|字段注入|通过反射设置成员变量|⭐⭐|

注意中间这一列：**构造器注入和 Setter 注入都是「调用方法」，只有字段注入是靠反射直接给成员变量赋值**，三种方式的底层差别就体现在这里。

---

## **三、Spring 底层是怎么实现依赖注入的？⭐⭐⭐⭐⭐**

这是面试官最可能追问的部分。这里以 `@Autowired` 字段注入为例：

```java
@Service
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;
}
```

Spring 的依赖注入主要涉及 **BeanDefinition、BeanFactory、反射、BeanPostProcessor**。

### **第一步：扫描并注册 Bean**

Spring 启动时，通过组件扫描等方式找到：

```java
@Service
public class OrderService {
}
```

然后把 Bean 的定义信息封装成 `BeanDefinition`，注册到 Spring 容器，这一步走下来就是 **扫描 `@Service` → 解析 BeanDefinition → 注册到 BeanFactory**。注意这个时候注册的还只是 Bean 的定义信息，并不意味着所有 Bean 都已经完成实例化。

### **第二步：创建 Bean 对象**

Spring 根据 BeanDefinition 创建 `OrderService` 对象，例如通过构造方法实例化：**BeanDefinition → 解析构造方法 → 实例化 OrderService**。

### **第三步：解析依赖关系**

Spring 需要处理：

```java
@Autowired
private OrderMapper orderMapper;
```

这里涉及一个重要的类 **`AutowiredAnnotationBeanPostProcessor`**，它负责处理 `@Autowired` 等注解对应的注入逻辑。Spring 会识别需要注入的字段或方法，并解析对应的依赖：**OrderService → 发现 `@Autowired` → 需要 OrderMapper 类型的 Bean → 向 Spring 容器查找**。

### **第四步：查找依赖对象**

Spring 根据依赖类型、候选 Bean、限定符等信息，选择合适的 Bean：

```text
需要：OrderMapper

Spring 容器：
    │
    ├── OrderService
    │
    ├── OrderMapper
    │
    └── UserService
           │
           ▼
    找到 OrderMapper
```

如果存在多个相同类型的 Bean，Spring 还需要结合 `@Qualifier`、`@Primary` 等信息进行选择。

### **第五步：通过反射完成注入**

对于字段注入，Spring 可以通过反射设置成员变量，简化理解：

```java
Field field = OrderService.class.getDeclaredField("orderMapper");

field.setAccessible(true);

field.set(orderService, orderMapper);
```

`getDeclaredField("orderMapper")`：按字段名拿到 `OrderService` 上的这个字段。`setAccessible(true)`：打开访问权限，绕过 `private` 的限制。`set()`：真正把依赖对象赋给这个字段。这样即使 `orderMapper` 是 `private` 字段，也能够在允许的反射访问条件下完成注入。对于构造器注入，则是在创建 Bean 时解析构造参数并调用相应构造方法。

**因此，依赖注入并不是简单地通过反射赋值，而是 Spring 先解析依赖，再通过构造器、方法调用或字段反射完成注入。**

### **整体流程**

```text
          Spring 容器启动
                 │
                 ▼
         扫描并注册 Bean
                 │
                 ▼
          创建 Bean 对象
                 │
                 ▼
          解析依赖注入点
                 │
                 ▼
        从容器查找依赖 Bean
                 │
                 ▼
        构造器 / Setter / 反射
                 │
                 ▼
             完成注入
                 │
                 ▼
           Bean 初始化完成
```

补充一点：构造器注入发生在对象实例化过程中，而字段注入、Setter 注入通常发生在实例化之后、初始化之前。

---

## Q：@Autowired 和 @Resource 有什么区别？

其实关键的是知道：
`@Autowired` 主要按类型解析
`@Resource` 默认按名称解析，找不到匹配名称时，在符合条件的情况下可以回退到类型匹配。


详细了解：

|**对比**| `@Autowired` | `@Resource` |
|---|---|---|
|来源|Spring|Jakarta / Java EE 规范|
|默认匹配方式|主要按类型|通常优先按名称|
|指定 Bean| `@Qualifier` | `name` 属性|
|构造器注入|支持|不支持|
|字段注入|支持|支持|
|Setter 注入|支持|支持|

例如 **`@Autowired`：**

```java
@Autowired
@Qualifier("orderMapper")
private OrderMapper orderMapper;
```

**`@Resource`：**

```java
@Resource(name = "orderMapper")
private OrderMapper orderMapper;
```

---

## Q：依赖注入了解吗？Spring 是怎么实现依赖注入的？

可以这样回答：

依赖注入是 Spring 实现 IoC 的主要方式，指的是对象不需要自己创建依赖对象，而是由 Spring 容器负责创建和注入，从而降低对象之间的耦合度。

Spring 主要支持构造器注入、Setter 注入和字段注入三种方式，其中实际开发更推荐构造器注入。

从底层实现来看，Spring 首先通过组件扫描或配置解析 BeanDefinition，并将其注册到 BeanFactory 中（之前已经提到 BeanFactory 是一个 IOC 容器接口）。

在创建 Bean 时，Spring 会解析它的依赖关系。对于 `@Autowired` 注解，主要由 `AutowiredAnnotationBeanPostProcessor` 处理，Spring 会根据类型、限定符等信息从容器中查找对应的 Bean。

最后，根据不同的注入方式，通过构造方法、Setter 方法或者反射完成依赖注入。

因此，Spring 依赖注入的底层主要涉及 **IoC 容器、BeanDefinition、依赖解析、BeanPostProcessor 和反射机制**。

---

**① 什么是依赖注入？**

对象不自己创建依赖，而是由 Spring 容器提供。

**② 有哪些注入方式？**

构造器注入、Setter 注入、字段注入。

**③ 底层怎么实现？**

```text
扫描 Bean
    ↓
注册 BeanDefinition
    ↓
创建 Bean
    ↓
解析依赖关系
    ↓
查找依赖 Bean
    ↓
构造器 / Setter / 反射注入
```


再次捋一遍：
SpringBoot 通过 BeanFactory 的具体实现来管理 Bean
Spring 启动会扫描带注解（@Service等）的类；
然后注册为 Bean 放入 SpringIOC 容器中，这些 Bean 的信息会封装为 BeanDefinition；
然后 Spring 容器会创建这些 Bean 的对象（类➡️对象）；
创建对象时候会解析依赖关系，通过@AutoWired 注解等从容器中找到对应的依赖 Bean，再通过构造器、Setter 或字段反射等方式完成依赖注入
