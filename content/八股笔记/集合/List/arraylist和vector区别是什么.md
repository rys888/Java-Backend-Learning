`ArrayList` 和 `Vector` 非常像，**底层都是动态数组**，最大的区别就是：

**ArrayList 线程不安全，Vector 线程安全。**

可以直接这样对比：

|**对比**|**ArrayList**|**Vector**|
|---|---|---|
|底层结构|动态数组|动态数组|
|线程安全|❌ 不安全|✅ 安全|
|同步机制|没有同步保护|很多方法使用 `synchronized` |
|性能|通常更高|同步有额外开销|
|扩容|通常扩为原来的 **1.5 倍**|默认通常扩为原来的 **2 倍**|
|使用情况|⭐⭐⭐⭐⭐ 非常常用|较老，现在较少使用|

例如 `Vector` 的很多方法带同步：

```java
public synchronized boolean add(E e) {
    // ...
}
```

可以简单理解：

```text
ArrayList
   ↓
多个线程同时修改
   ↓
没有同步保护
   ↓
可能出现并发问题


Vector
   ↓
synchronized
   ↓
同一时刻限制并发修改关键操作
   ↓
保证单个方法调用的线程安全
```

### **为什么现在一般不用 Vector？**

因为 `Vector` 属于比较早期的线程安全集合，它对很多方法直接进行同步，机制比较粗。

现代 Java 并发开发一般根据具体场景选择，例如：

```java
CopyOnWriteArrayList
```

比较适合**读多写少**的场景。

如果只是普通单线程/无需共享的业务代码：

```java
ArrayList
```

通常就是首选。

### **面试回答**

ArrayList 和 Vector 底层都是动态数组，都支持随机访问。最大的区别是 ArrayList 不是线程安全的，而 Vector 的很多方法使用 synchronized，因此是线程安全的，但同步也会带来额外性能开销。另外，两者的默认扩容策略也不同，ArrayList 通常扩容到原来的 1.5 倍，而 Vector 在未指定 capacityIncrement 时通常扩容到原来的 2 倍。实际开发中 ArrayList 使用更多，并发场景通常根据需求考虑 CopyOnWriteArrayList 等并发集合。

一句话记：

**ArrayList：动态数组 + 非线程安全 + 常用；Vector：动态数组 + synchronized + 老牌线程安全集合。**