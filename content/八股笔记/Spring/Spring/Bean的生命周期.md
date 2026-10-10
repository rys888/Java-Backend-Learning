
Spring Bean 的生命周期是 Java 后端面试的高频考点，而且和我们前面学习的 **IoC、依赖注入、BeanPostProcessor、AOP 动态代理、三级缓存** 都有关系。

**Bean 的生命周期，就是一个 Bean 从创建、依赖注入、初始化、使用到最终销毁的完整过程。**

先记住这条主线：

**实例化 → 属性赋值（依赖注入）→ 初始化 → 使用 → 销毁**

但如果面试官问的是 Spring Bean 的完整生命周期，还需要加入 `BeanPostProcessor` 等扩展机制。

## **一、Spring Bean 生命周期的完整流程**

以一个普通的 Singleton Bean 为例：

```text
          Spring IoC 容器启动
                  │
                  ▼
          1. 注册 BeanDefinition
                  │
                  ▼
          2. 实例化 Bean
                  │
                  ▼
          3. 属性赋值、依赖注入
                  │
                  ▼
          4. 执行 Aware 接口回调
                  │
                  ▼
     5. BeanPostProcessor 前置处理
                  │
                  ▼
          6. 执行初始化方法
                  │
                  ▼
     6. BeanPostProcessor 后置处理
                  │
                  ▼
          8. Bean 可以正常使用
                  │
                  ▼
          9. 容器关闭，销毁 Bean
```

下面逐步理解。

---

## **二、Bean 生命周期的各个阶段**

### **1. 注册 BeanDefinition**

Spring Boot 启动时，会创建并刷新 `ApplicationContext`。

通过组件扫描等方式发现：

```java
@Service
public class UserService {
}
```

然后将 Bean 的定义信息封装为 `BeanDefinition`，注册到容器中。

`BeanDefinition` 包含：

- Bean 的类型
- Bean 的作用域
- 初始化方法
- 依赖信息等

**注意：注册 BeanDefinition 不等于创建 Bean 对象。**

### **2. 实例化 Bean**

Spring 根据 BeanDefinition 创建对象。

例如：

```java
UserService userService = new UserService();
```

实际上，Spring 可以通过构造器反射、工厂方法等方式创建对象。

此时：

**对象已经创建，但还没有完成属性注入和初始化。**

对于符合条件的单例 Bean，Spring 还可能在实例化后提前暴露对象工厂到三级缓存，以支持部分循环依赖场景。

### **3. 属性赋值与依赖注入**

例如：

```java
@Service
public class UserService {

    @Autowired
    private OrderService orderService;
}
```

Spring 会解析 `@Autowired`，从 IoC 容器中寻找对应的依赖 Bean，并完成注入。

```text
UserService 实例化
        ↓
发现 @Autowired
        ↓
从容器获取 OrderService
        ↓
注入 UserService
```

这里需要注意：

- **构造器注入**：发生在实例化过程中。
- **字段注入、Setter 注入**：通常发生在实例化之后。

因此，并不是所有依赖注入都发生在对象实例化之后。

### **4. 执行 Aware 接口回调**

Spring 提供了一系列 `Aware` 接口，让 Bean 能够感知容器中的相关信息。

例如：

```java
@Component
public class UserService implements BeanNameAware {

    @Override
    public void setBeanName(String name) {
        System.out.println("Bean 名称：" + name);
    }
}
```

常见接口：

| **接口**                    | **作用**                |
| ------------------------- | --------------------- |
| `BeanNameAware`           | 获取 Bean 名称            |
| `BeanFactoryAware`        | 获取 BeanFactory        |
| `ApplicationContextAware` | 获取 ApplicationContext |

其中部分回调由专门的 `BeanPostProcessor` 实现，因此这里展示的是简化后的典型顺序。

### **5. BeanPostProcessor 前置处理**

Spring 会执行：

```java
postProcessBeforeInitialization()
```

它属于 `BeanPostProcessor` 接口：

```java
public interface BeanPostProcessor {

    Object postProcessBeforeInitialization(
            Object bean, String beanName);

    Object postProcessAfterInitialization(
            Object bean, String beanName);
}
```

这个接口允许开发者在 Bean 初始化前后添加额外逻辑。

例如：

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessBeforeInitialization(
            Object bean, String beanName) {

        System.out.println("初始化前：" + beanName);

        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(
            Object bean, String beanName) {

        System.out.println("初始化后：" + beanName);

        return bean;
    }
}
```

**BeanPostProcessor 是 Spring 非常重要的扩展机制，AOP 自动代理也与它有关。**

### **6. 执行初始化方法**

Spring 支持多种初始化方式。

**① @PostConstruct**

```java
@Component
public class UserService {

    @PostConstruct
    public void init() {
        System.out.println("Bean 初始化");
    }
}
```

**② InitializingBean**

```java
@Component
public class UserService implements InitializingBean {

    @Override
    public void afterPropertiesSet() {
        System.out.println("Bean 初始化");
    }
}
```

**③ @Bean(initMethod = “…”)**

```java
@Bean(initMethod = "init")
public UserService userService() {
    return new UserService();
}
```

对于同时配置这些方式的常见场景，执行顺序通常是：

```text
@PostConstruct
       ↓
InitializingBean.afterPropertiesSet()
       ↓
自定义 initMethod
```

需要注意，`@PostConstruct` 实际上是在一个专门的 BeanPostProcessor 的初始化前置处理过程中执行的。

### **7. BeanPostProcessor 后置处理 ⭐⭐⭐⭐⭐**

初始化完成后，Spring 会执行：

```java
postProcessAfterInitialization()
```

**这里是 Spring AOP 通常创建代理对象的重要阶段。**

例如：

```java
@Service
public class UserService {

    @Transactional
    public void saveUser() {
        // ...
    }
}
```

Spring AOP 自动代理创建器会判断这个 Bean 是否需要代理。

如果需要，就可能创建 JDK 或 CGLIB 代理对象。

```text
UserService 原始对象
        ↓
BeanPostProcessor 后置处理
        ↓
判断是否需要 AOP
        ↓
创建代理对象
        ↓
将代理对象作为最终 Bean
```

这就和我们前面学习的 AOP 联系起来了。

不过，**如果发生循环依赖，Spring 可能通过三级缓存提前创建 AOP 代理对象**，而不是等到这个阶段才第一次创建。

### **8. Bean 正常使用**

经过初始化等处理后，Bean 就可以正常使用。

对于普通单例 Bean，Spring 会将最终对象保存到一级缓存：

```java
singletonObjects
```

如果 Bean 需要 AOP 增强，缓存的通常就是最终代理对象。

其他组件通过：

```java
@Autowired
private UserService userService;
```

获取的就是 Spring 容器对外提供的 Bean。

### **9. Bean 销毁**

当 Spring 容器关闭时，会执行受管理单例 Bean 的销毁回调。

常见方式：

**① @PreDestroy**

```java
@PreDestroy
public void destroy() {
    System.out.println("Bean 销毁");
}
```

**② DisposableBean**

```java
@Override
public void destroy() {
    System.out.println("Bean 销毁");
}
```

**③ 自定义 destroyMethod**

```java
@Bean(destroyMethod = "close")
```

对于同时配置的常见场景，销毁顺序通常是：

```text
@PreDestroy
      ↓
DisposableBean.destroy()
      ↓
自定义 destroyMethod
```

需要注意：**Spring 不会自动管理 Prototype Bean 的完整销毁过程**。Prototype Bean 创建并交给使用者后，其后续清理通常需要使用者自己负责。

---

## **三、Bean 生命周期和 AOP、三级缓存的关系 ⭐⭐⭐⭐⭐**

这部分可以帮助你把前面学过的知识串起来。

```text
              BeanDefinition
                    ↓
                实例化 Bean
                    ↓
       三级缓存提前暴露 ObjectFactory
             （符合条件时）
                    ↓
                 依赖注入
                    ↓
           如果发生循环依赖
                    ↓
        通过三级缓存获取提前引用
                    ↓
          必要时提前创建 AOP 代理（循环依赖）
                    ↓
                初始化 Bean
                    ↓
        BeanPostProcessor 后置处理
                    ↓
        正常情况下创建 AOP 代理
                    ↓
              最终 Bean
                    ↓
              一级缓存
                    ↓
                 使用
                    ↓
                 销毁
```

这里有三个关键点：

**① IoC：** Spring 负责创建、管理 Bean 的整个生命周期。

**② AOP：** Spring 可以通过 BeanPostProcessor，在 Bean 创建过程中生成代理对象。

**③ 三级缓存：** 在部分循环依赖场景下，Spring 可以提前暴露 Bean 引用，必要时提前获取 AOP 代理对象。

---

## Q：Spring Bean 的生命周期是什么？

Spring Bean 的生命周期主要包括实例化、属性赋值、初始化、使用和销毁几个阶段。

首先，Spring 容器会根据 BeanDefinition 实例化 Bean，然后进行依赖注入，例如通过 `@Autowired` 注入其他 Bean。

接着执行相关的 Aware 接口回调，让 Bean 感知容器信息。

然后进入初始化阶段，先执行 BeanPostProcessor 的前置处理，再执行初始化回调，例如 `@PostConstruct`、`InitializingBean` 和自定义初始化方法。

初始化完成后，会执行 BeanPostProcessor 的后置处理。Spring AOP 通常就在这个阶段为需要增强的 Bean 创建代理对象。

最后，Bean 可以正常使用。当容器关闭时，Spring 会执行 `@PreDestroy`、`DisposableBean` 等销毁回调。

此外，在部分单例 Bean 的循环依赖场景下，Spring 还可以通过三级缓存提前暴露 Bean 引用，必要时提前创建 AOP 代理对象。

---

## **五、最后记住这张简化流程图**

```text
       BeanDefinition
              ↓
          实例化 Bean
              ↓
          属性赋值 / DI
              ↓
          Aware 接口回调
              ↓
    BeanPostProcessor 前置
              ↓
         Bean 初始化
              ↓
    BeanPostProcessor 后置
              ↓
         AOP 代理（如需要）
              ↓
          Bean 正常使用
              ↓
          Bean 销毁
```

**一句话总结：Spring Bean 的生命周期是实例化 → 依赖注入 → Aware 回调 → 初始化前置处理 → 初始化 → 初始化后置处理 → 使用 → 销毁，其中 AOP 代理通常在后置处理阶段创建，三级缓存则可以在循环依赖时提前暴露 Bean。**