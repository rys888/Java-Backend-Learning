Spring Bean 的生命周期是 Java 后端面试的高频考点，而且跟前面学的 **IoC、依赖注入、BeanPostProcessor、AOP 动态代理、三级缓存** 都能串起来。一句话概括：**Bean 的生命周期，就是一个 Bean 从创建、依赖注入、初始化、使用到最终销毁的完整过程。**

先记住这条主线：**实例化 → 属性赋值（依赖注入）→ 初始化 → 使用 → 销毁**。不过面试里问"完整生命周期"时，还要把 `BeanPostProcessor` 这类扩展机制加进去。

## 一、Spring Bean 生命周期的完整流程

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
     7. BeanPostProcessor 后置处理
                  │
                  ▼
          8. Bean 可以正常使用
                  │
                  ▼
          9. 容器关闭，销毁 Bean
```

下面逐步拆开看。

## 二、Bean 生命周期的各个阶段

### 1. 注册 BeanDefinition

Spring Boot 启动时会创建并刷新 `ApplicationContext`，通过组件扫描等方式发现标注了 `@Service` 的类：

```java
@Service
public class UserService {
}
```

然后把这些类的定义信息封装成 `BeanDefinition` 注册到容器里。`BeanDefinition` 里存的是 Bean 的类型、作用域、初始化方法、依赖信息这些内容，相当于"怎么创建这个 Bean"的说明书。**注册 BeanDefinition 不等于创建 Bean 对象。**

### 2. 实例化 Bean

Spring 根据 BeanDefinition 创建对象，相当于执行 `new UserService()`，实际底层是通过构造器反射、工厂方法等方式完成的。这个时候**对象已经有了，但属性还没注入，初始化方法也还没跑**。

对于符合条件的单例 Bean，Spring 还可能在实例化后把对象工厂提前暴露到三级缓存，用来支持部分循环依赖场景。

### 3. 属性赋值与依赖注入

比如：

```java
@Service
public class UserService {

    @Autowired
    private OrderService orderService;
}
```

Spring 会解析 `@Autowired`，从 IoC 容器里找到对应的依赖 Bean 注入进来，大致过程：

```text
UserService 实例化
        ↓
发现 @Autowired
        ↓
从容器获取 OrderService
        ↓
注入 UserService
```

这里容易搞混：**构造器注入发生在实例化过程中**，而**字段注入、Setter 注入通常发生在实例化之后**。所以并不是所有依赖注入都发生在对象实例化之后。

### 4. 执行 Aware 接口回调

Spring 提供了一系列 `Aware` 接口，让 Bean 能感知到容器里的信息。比如实现 `BeanNameAware` 之后，容器创建这个 Bean 时会把 Bean 名称回调进来：

```java
@Component
public class UserService implements BeanNameAware {

    @Override
    public void setBeanName(String name) {
        System.out.println("Bean 名称：" + name);
    }
}
```

常见的几个：

| 接口 | 作用 |
| --- | --- |
| `BeanNameAware` | 获取 Bean 名称 |
| `BeanFactoryAware` | 获取 BeanFactory |
| `ApplicationContextAware` | 获取 ApplicationContext |

其中部分回调是由专门的 `BeanPostProcessor` 实现的，所以这里列的是简化后的典型顺序。

### 5. BeanPostProcessor 前置处理

初始化之前，Spring 会回调 `BeanPostProcessor` 的 `postProcessBeforeInitialization()`：

```java
public interface BeanPostProcessor {

    Object postProcessBeforeInitialization(
            Object bean, String beanName);

    Object postProcessAfterInitialization(
            Object bean, String beanName);
}
```

这个接口的作用就是在 Bean 初始化前后插一段自己的逻辑，写个实现类就能看到执行效果：

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

**BeanPostProcessor 是 Spring 里非常关键的扩展点，AOP 自动代理也跟它有关。**

### 6. 执行初始化方法

Spring 支持三种初始化方式。

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

**③ @Bean(initMethod = "…")**

```java
@Bean(initMethod = "init")
public UserService userService() {
    return new UserService();
}
```

三种方式同时配置时，执行顺序是：

```text
@PostConstruct
       ↓
InitializingBean.afterPropertiesSet()
       ↓
自定义 initMethod
```

需要注意，`@PostConstruct` 并不是 Spring 自己直接调的，它是在一个专门处理 `@PostConstruct` 的 BeanPostProcessor 的**前置处理**阶段执行的。

### 7. BeanPostProcessor 后置处理 ⭐⭐⭐⭐⭐

初始化完成后，Spring 会回调 `postProcessAfterInitialization()`。**这里是 Spring AOP 通常创建代理对象的地方。**

比如这个 Bean：

```java
@Service
public class UserService {

    @Transactional
    public void saveUser() {
        // ...
    }
}
```

Spring AOP 的自动代理创建器会判断这个 Bean 需不需要代理，需要的话就创建 JDK 或 CGLIB 代理：

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

这就和前面学的 AOP 对上了。不过**如果发生循环依赖，Spring 可能通过三级缓存提前创建 AOP 代理对象**，不会等到这个阶段才第一次创建。

### 8. Bean 正常使用

经过初始化这些处理后，Bean 就能正常用了。普通单例 Bean 的最终对象会放进一级缓存 `singletonObjects`，如果这个 Bean 需要 AOP 增强，缓存里放的就是最终的代理对象。其他组件通过 `@Autowired` 注入拿到的，就是 Spring 容器对外提供的这个 Bean。

### 9. Bean 销毁

Spring 容器关闭时，会执行受管理单例 Bean 的销毁回调。常见方式有三种：

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

**③ 自定义 destroyMethod**，比如 `@Bean(destroyMethod = "close")`。

三种方式同时配置时，销毁顺序是：

```text
@PreDestroy
      ↓
DisposableBean.destroy()
      ↓
自定义 destroyMethod
```

需要注意：**Spring 不会自动管理 Prototype Bean 的完整销毁过程**。Prototype Bean 创建出来交出去之后，后面的清理得由使用方自己负责。

## 三、Bean 生命周期和 AOP、三级缓存的关系 ⭐⭐⭐⭐⭐

这部分是把前面学的知识串起来：

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

三个关键点：**IoC** 负责创建、管理 Bean 的整个生命周期；**AOP** 通过 BeanPostProcessor 在 Bean 创建过程中生成代理对象；**三级缓存** 在部分循环依赖场景下提前暴露 Bean 引用，必要时提前拿到 AOP 代理对象。

## 四、Q：Spring Bean 的生命周期是什么？

Spring Bean 的生命周期是指 Bean 从创建到销毁的整个过程分为以下几个阶段：
1. 实例化：Spring 容器通过反射（调用构造器）创建 Bean 实例。
2. 属性赋值：对 Bean 的成员变量进行填充，包括依赖注入。
3. Aware 接口回调：如果 Bean 实现了特定的 Aware 接口，Spring 会调用相应方法注入容器相关对象。
4. BeanPostProcessor 前置处理：在 Bean 初始化前，调用所有 BeanPostProcessor 的 postProcessBeforeInitialization 方法，可以对 Bean 进行自定义加工。
5. 初始化：
    - 如果 Bean 实现了 InitializingBean 接口，调用其 afterPropertiesSet()方法。
    - 如果配置了自定义的 init-method（比如 XML 中指定或@Bean(initMethod = "...")），则调用该方法。
6. BeanPostProcessor 后置处理：调用所有 BeanPostProcessor 的 postProcessAfterInitialization 方法，此时 Bean 已经准备就绪，可以对外提供服务。
7. 使用中：Bean 驻留在容器中，被应用程序使用。
8. 销毁：当容器关闭时，如果 Bean 实现了 DisposableBean 接口，调用其 destroy()方法；如果配置了自定义的 destroy-method，则调用该方法。

## 五、最后记住这张简化流程图

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
