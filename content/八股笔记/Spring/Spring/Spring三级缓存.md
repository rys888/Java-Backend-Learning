
[[#Q：Spring 的三级缓存是什么？为什么需要三级缓存？]]

Spring 的三级缓存，就是 Spring 创建单例 Bean 的时候用来存"还没完全创建好的 Bean"的三层 Map，主要解决**部分单例 Bean 的循环依赖**问题，同时保证依赖注入时拿到的对象是正确的——包括 AOP 生成的代理对象。这块经常和 IoC、DI、Bean 生命周期、AOP 一起考，属于 Spring 里绕不开的一个点。

## **一、Spring 的三级缓存分别是什么？**

三层缓存都在 `DefaultSingletonBeanRegistry` 这个类里。

|**缓存级别**|**名称**|**存储内容**|
|---|---|---|
|**一级缓存**| `singletonObjects` |已经创建完成的单例 Bean|
|**二级缓存**| `earlySingletonObjects` |提前暴露的单例 Bean 对象，可能是原始对象或代理对象|
|**三级缓存**| `singletonFactories` |用于获取提前暴露 Bean 的 `ObjectFactory`|

可以这样理解：

```text
           Spring IoC 容器
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    一级缓存    二级缓存    三级缓存
       │          │          │
       ▼          ▼          ▼
   完整 Bean   提前暴露的   ObjectFactory
                Bean        对象工厂
```

需要注意两点：**三级缓存不是存 BeanDefinition 的地方**；也不是每个 Bean 都要依次过一遍这三个缓存，没有循环依赖的 Bean 创建完直接进一级缓存就完事了。

---

## **二、为什么 Spring 需要三级缓存？**

根子上就是为了解决**循环依赖**。假设有两个 Service 互相注入：

```java
@Service
public class UserService {

    @Autowired
    private OrderService orderService;
}

@Service
public class OrderService {

    @Autowired
    private UserService userService;
}
```

`UserService` 依赖 `OrderService`，`OrderService` 又依赖 `UserService`，绕成了一个圈：**UserService → OrderService → UserService → ...**。如果 Spring 老老实实"创建 A 的时候发现要 B，就去创建 B，创建 B 又发现要 A"，那就会一直转下去拿不到对象。三级缓存要做的就是：**在 Bean 还没创建完的时候，先把它的一个提前引用暴露出去**，让依赖方先拿着用。

---

## **三、Spring 三级缓存解决循环依赖的流程 ⭐⭐⭐⭐⭐**

还是拿上面两个 Service 举例，前提是**单例 Bean + 字段注入**，并且容器允许循环依赖。

### **第一步：创建 UserService**

Spring 先实例化 `UserService`，也就是 `new UserService()`。这时候对象已经堆里有了，但 `orderService` 还是 null，依赖注入还没做。Spring 会把一个能拿到该 Bean 提前引用的 `ObjectFactory` 放进三级缓存，`singletonFactories` 里就多了一条 **userService → ObjectFactory**。

⚠️ 注意：三级缓存存的是对象工厂，不是 UserService 对象本身。

### **第二步：为 UserService 注入 OrderService**

Spring 看到 `@Autowired private OrderService orderService;`，就去容器里拿 `OrderService`，发现它还没创建，于是开始创建 `OrderService`，同样 `new OrderService()`，再把它的对象工厂也放进三级缓存。这时候三级缓存里是 userService、orderService 两条记录。

### **第三步：OrderService 反过来需要 UserService**

给 `OrderService` 注入依赖时发现它要 `UserService`，但 `UserService` 还没初始化完成。这个时候 Spring 就去缓存里找，查找顺序是这样的：

```text
查找 UserService
       │
       ▼
一级缓存 singletonObjects
       │
       ├── 找到了 → 直接返回
       │
       ▼
二级缓存 earlySingletonObjects
       │
       ├── 找到了 → 返回提前引用
       │
       ▼
三级缓存 singletonFactories
       │
       ├── 找到 ObjectFactory
       │
       ▼
调用 ObjectFactory.getObject()
       │
       ▼
获取 UserService 的提前引用
       │
       ▼
放入二级缓存
       │
       ▼
移除三级缓存中对应的工厂
```

一级缓存没有就查二级缓存，二级缓存也没有才去三级缓存拿 ObjectFactory，调 `getObject()` 拿到提前引用，然后放进二级缓存，同时把三级缓存里对应的工厂删掉。这样一来 `OrderService` 就拿到了一个还没初始化完的 `UserService` 引用，循环也就断开了。

### **第四步：OrderService 创建完成**

依赖已经拿到了，`OrderService` 可以继续走完初始化流程，完成后被放进一级缓存，也就是 **singletonObjects 里多了 orderService**。

### **第五步：UserService 创建完成**

回到最开始的 `UserService`，现在 `OrderService` 已经是完整对象了，直接注进去，接着执行 `UserService` 自己的初始化流程，最后也注册到一级缓存，并清理掉提前暴露用的那些缓存。到这一步一级缓存里 userService、orderService 都在了，**循环依赖解决完毕**。

---

## **四、为什么需要三级缓存，而不是两级缓存？⭐⭐⭐⭐⭐**

这是三级缓存最经典的追问。

一级缓存存完整 Bean，二级缓存存提前暴露的引用，三级缓存存获取提前引用的工厂。那么问题来了：**为什么不直接把实例化后的 Bean 放进二级缓存，非要再套一层 ObjectFactory？**

关键在于 **Spring AOP 可能需要为 Bean 创建代理对象**。比如 `UserService` 上加了事务增强：

```java
@Service
public class UserService {

    @Autowired
    private OrderService orderService;

    @Transactional
    public void saveUser() {
        // 保存用户
    }
}
```

假如真的发生循环依赖，`OrderService` 要提前拿 `UserService`，而二级缓存里如果直接放的是原始对象，那结果就是 **OrderService 持有原始 UserService，容器最终管理的却是 UserService 代理对象**。OrderService 调 UserService 的方法时就走不到代理上，事务增强直接失效。

三级缓存就是为了避免这件事：Spring 不把原始对象直接交出去，而是通过三级缓存里的 `ObjectFactory` 去获取提前引用。这个过程最终会调用类似 `getEarlyBeanReference(beanName, mbd, bean)` 的方法，如果需要 AOP 代理，相关的自动代理创建器就有机会提前返回代理对象：

```text
三级缓存 ObjectFactory
          │
          ▼
   getEarlyBeanReference()
          │
          ▼
     判断是否需要代理
          │
     ┌────┴────┐
     ▼         ▼
   不需要     需要
     │         │
     ▼         ▼
   原始对象   代理对象
     │         │
     └────┬────┘
          │
          ▼
      放入二级缓存
          │
          ▼
      注入 OrderService
```

这样就能保证：**依赖方提前拿到的 Bean 引用，与容器最终提供的 Bean 是一致的**。

需要注意，并不是三级缓存里所有工厂都会生成代理对象，只有在确实需要提前引用的时候，才会去调对应的工厂。

---
## Q：Spring 的三级缓存是什么？为什么需要三级缓存？


Spring 的三级缓存主要用于解决部分单例 Bean 的循环依赖问题。

一级缓存 `singletonObjects` 保存已经创建完成的单例 Bean；二级缓存 `earlySingletonObjects` 保存提前暴露的 Bean 引用；三级缓存 `singletonFactories` 保存能够获取 Bean 提前引用的 ObjectFactory。

当 Spring 创建一个单例 Bean 时，会先实例化对象，然后在满足条件时，将对应的 ObjectFactory 放入三级缓存。

如果在依赖注入过程中发生循环依赖，Spring 就可以通过三级缓存获取尚未完成初始化的 Bean 引用，将其放入二级缓存，再注入其他 Bean，从而打破循环依赖。

之所以需要三级缓存，主要是为了兼容 AOP。通过 ObjectFactory，Spring 可以在需要提前引用时调用 `getEarlyBeanReference()`，必要时提前创建代理对象，避免依赖方持有原始对象而容器最终管理代理对象的问题。



至于为什么需要三级缓存是为了兼容 AOP 这里有很好的逻辑来描述：

```
一级缓存：没有 UserService
    ↓
二级缓存：没有 UserService
    ↓
三级缓存：找到 ObjectFactory
    ↓
调用 getObject()
    ↓
调用 getEarlyBeanReference()
    ↓
AOP 创建 UserService 代理对象
    ↓
代理对象放入二级缓存
    ↓
从三级缓存移除对应工厂
```

这样二级缓存中存着的就是代理对象而不是 UserService 对象了，就能进行 AOP 有关的业务处理了