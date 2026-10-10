`BeanFactory` 和 `ApplicationContext` 都是 Spring IoC 容器的核心接口，主要负责 **Bean 的创建、依赖注入和生命周期管理**。

它们最重要的区别是：

**BeanFactory 是 Spring IoC 容器的基础接口，而 ApplicationContext 是在 BeanFactory 基础上扩展了更多企业级功能的高级容器接口。**

## **一、BeanFactory 和 ApplicationContext 的区别 ⭐⭐⭐⭐⭐**

|**对比**|**BeanFactory**|**ApplicationContext**|
|---|---|---|
|定位|基础 IoC 容器接口|高级 IoC 容器接口|
|Bean 管理|支持|支持|
|依赖注入|支持|支持|
|Bean 生命周期|支持|支持|
|国际化|不直接提供|支持|
|事件发布|不直接提供|支持|
|资源访问|功能较基础|提供统一资源访问能力|
|AOP|可以支持|可以支持|
|Bean 创建时机|取决于具体实现|通常在容器刷新时预实例化非懒加载单例 Bean|
|使用场景|底层容器机制|日常 Spring / Spring Boot 开发|

需要特别注意：**BeanFactory 和 ApplicationContext 是接口，而不是两个具体的容器实现类。**

---

## **二、BeanFactory 是什么？**

`BeanFactory` 是 Spring IoC 容器最基础的接口。

它提供的核心能力就是：

**根据 Bean 的名称或类型，从容器中获取 Bean。**

例如：

```java
public interface BeanFactory {

    Object getBean(String name);

    <T> T getBean(Class<T> requiredType);

    boolean containsBean(String name);

}
```

以上只是部分方法的简化展示。

假设容器中存在：

```java
@Service
public class UserService {

    public void saveUser() {
        System.out.println("保存用户");
    }
}
```

我们可以通过：

```java
UserService userService =
        beanFactory.getBean(UserService.class);
```

获取 Bean。

### **BeanFactory 的特点**

它主要负责：

- 管理 Bean 的定义信息。
- 创建 Bean。
- 完成依赖注入。
- 管理 Bean 的生命周期。
- 根据名称或类型获取 Bean。

需要注意，`BeanFactory` 本身只是接口，具体功能由实现类提供。

例如：

```java
DefaultListableBeanFactory
```

它是 Spring 中非常重要的 BeanFactory 实现类。

---

## **三、ApplicationContext 是什么？**

`ApplicationContext` 是 Spring 提供的高级 IoC 容器接口。

它继承了 `BeanFactory`：

```java
public interface ApplicationContext
        extends EnvironmentCapable,
                ListableBeanFactory,
                HierarchicalBeanFactory,
                MessageSource,
                ApplicationEventPublisher,
                ResourcePatternResolver {
}
```

这里省略了部分父接口。

因此，**ApplicationContext 不仅具备 BeanFactory 的 Bean 管理能力，还扩展了很多功能。**

例如：

### **1. 国际化**

通过 `MessageSource`，可以根据不同语言环境获取对应的文本。

### **2. 事件发布**

Spring 支持事件发布与监听机制。

例如：

```java
@Component
public class OrderListener {

    @EventListener
    public void handleOrder(OrderCreatedEvent event) {
        System.out.println("订单创建成功");
    }
}
```

可以通过：

```java
applicationContext.publishEvent(event);
```

发布事件。

### **3. 资源加载**

可以通过 Spring 提供的资源抽象访问文件、类路径资源等。

### **4. 自动注册和管理更多 Spring 基础设施**

例如：

- `BeanPostProcessor`
- `BeanFactoryPostProcessor`
- 事件监听器
- 国际化相关组件

这些功能使 `ApplicationContext` 更适合实际项目开发。

---

## **四、最重要的区别：Bean 的创建时机 ⭐⭐⭐⭐⭐**

这是面试经常追问的地方。

很多八股文会说：

BeanFactory 是懒加载，ApplicationContext 是立即加载。

**这种说法不够准确。**

准确来说：

- `BeanFactory` 是否立即创建 Bean，取决于具体实现和调用方式。
- `ApplicationContext` 通常在容器刷新过程中，预实例化非懒加载的单例 Bean。

例如：

```java
@Service
public class UserService {

    public UserService() {
        System.out.println("UserService 被创建");
    }
}
```

在典型的 `ApplicationContext` 启动过程中：

```text
Spring 容器启动
       ↓
注册 BeanDefinition
       ↓
实例化非懒加载的单例 Bean
       ↓
完成依赖注入与初始化
       ↓
容器启动完成
```

即使没有主动调用：

```java
applicationContext.getBean(UserService.class);
```

`UserService` 也可能已经创建完成。

但是，如果使用：

```java
@Lazy
@Service
public class UserService {
}
```

Spring 通常会延迟创建这个 Bean，直到真正需要时才实例化。

因此：

**ApplicationContext 默认预实例化非懒加载单例 Bean，但并不是所有 Bean 都会在容器启动时创建。**

---

## **五、BeanFactory 和 ApplicationContext 是什么关系？**

可以用这张图理解：

```text
               BeanFactory
                    ▲
                    │
             继承并扩展
                    │
            ApplicationContext
                    ▲
                    │
          ┌─────────┴─────────┐
          │                   │
AnnotationConfig       ClassPathXml
ApplicationContext     ApplicationContext
```

其中：

- `BeanFactory`：定义最基础的 Bean 管理能力。
- `ApplicationContext`：在 BeanFactory 基础上扩展更多功能。
- `AnnotationConfigApplicationContext`：基于注解配置的 ApplicationContext 实现。
- `ClassPathXmlApplicationContext`：基于 XML 配置的 ApplicationContext 实现。

**还有一个容易忽略的细节：**

虽然 `ApplicationContext` 继承了 `BeanFactory` 接口，但很多具体的 ApplicationContext 实现内部仍然使用 `DefaultListableBeanFactory` 来完成实际的 Bean 创建和管理。

可以简化理解为：

```text
          ApplicationContext
                 │
                 │ 对外提供高级容器功能
                 ▼
       DefaultListableBeanFactory
                 │
                 │ 实际管理 Bean
                 ▼
         BeanDefinition
                 ↓
            Bean 实例
```

这也解释了为什么我们经常说：

**BeanFactory 是 Spring IoC 的基础，ApplicationContext 是在其基础上构建的高级容器。**

---

## Q：BeanFactory 和 ApplicationContext 有什么区别？

BeanFactory 和 ApplicationContext 都是 Spring IoC 容器的核心接口。

BeanFactory 是最基础的容器接口，主要负责 Bean 的创建、依赖注入、生命周期管理以及 Bean 的获取。

ApplicationContext 继承了 BeanFactory，并在此基础上扩展了国际化、事件发布、资源加载等功能，因此实际开发中通常使用 ApplicationContext。

此外，两者在典型使用方式下的 Bean 创建时机也有所不同。BeanFactory 的具体加载行为取决于实现，而 ApplicationContext 通常会在容器刷新时提前实例化非懒加载的单例 Bean。

最后，ApplicationContext 虽然继承了 BeanFactory，但其具体实现内部通常仍然依赖 DefaultListableBeanFactory 来完成 Bean 的实际管理。

### **最后总结**

**BeanFactory 是基础 IoC 容器接口，ApplicationContext 是功能更丰富的高级 IoC 容器接口。**

对于 Java 后端实习面试，重点记住三个区别：

1. **功能不同**：ApplicationContext 提供事件发布、国际化、资源加载等扩展能力。
2. **Bean 创建时机不同**：ApplicationContext 通常在启动时预实例化非懒加载单例 Bean，而 BeanFactory 取决于具体实现。
3. **实际使用不同**：Spring Boot 开发通常使用 ApplicationContext，底层 Bean 管理仍然依赖 BeanFactory 体系。