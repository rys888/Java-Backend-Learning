`
Hashtable` 和 `HashMap` 很适合放在一起记。最核心的区别：

**HashMap：线程不安全，性能通常更好。**  
**Hashtable：线程安全，但实现方式比较粗暴——大量方法直接用** `synchronized` **锁住整个 Hashtable 对象。**

### **1. Hashtable 和 HashMap 的主要区别**

|**对比**|**HashMap**|**Hashtable**|
|---|---|---|
|线程安全|❌|✅|
|实现时间|JDK 1.2|JDK 1.0，比较老|
|null Key|✅ 允许一个|❌ 不允许|
|null Value|✅ 允许|❌ 不允许|
|并发性能|单线程下较好|较差|
|锁机制|没有同步保护| `synchronized` |
|推荐程度|⭐⭐⭐⭐⭐ 常用|⚠️ 基本不推荐新代码使用|

并发场景现在通常使用：

```java
ConcurrentHashMap
```

而不是 `Hashtable`。

---

## **2. Hashtable 怎么实现线程安全？⭐⭐⭐⭐⭐**

核心就是：

**在很多核心方法上直接使用**  `synchronized` ****。**

比如可以简化理解为：

```java
public synchronized V put(K key, V value) {
    // 添加数据
}
```

以及：

```java
public synchronized V get(Object key) {
    // 查询数据
}
```

还有类似：

```java
public synchronized V remove(Object key) {
    // 删除数据
}
```

这里要注意：

```java
public synchronized void xxx() {
}
```

实例方法上的 `synchronized`，锁的是：

```java
this
```

也就是**当前 Hashtable 对象本身**。

假设：

```java
Hashtable<String, Integer> table = new Hashtable<>();
```

三个线程：

```text
线程 A → table.put()
线程 B → table.put()
线程 C → table.get()
```

它们竞争的是**同一把对象锁**：

```text
             Hashtable
                🔒
          /      |      \
      线程A    线程B    线程C
       put      put      get
```

假如线程 A 获得锁：

```text
线程A → 🔒 → put()
线程B → 等待
线程C → 等待
```

A 完成释放锁后，其他线程才能继续竞争。

所以 Hashtable 的线程安全实现非常容易理解：

**对整个 Hashtable 加 synchronized，核心操作互斥执行。**

---

## **3. 为什么 Hashtable 性能不如 ConcurrentHashMap？**

因为锁粒度不同。

### **Hashtable**

```text
          整个 Map
             🔒
        /     |     \
      桶0    桶1    桶2
```

即使：

```text
线程A → 修改桶0
线程B → 修改桶10
```

明明操作不同桶，仍然可能因为同一个 Hashtable 对象锁而互相等待。

---

### **JDK 8 ConcurrentHashMap**

你刚学过：

```text
table

桶0 → A → B
      🔒

桶1 → C → D

桶2 → E → F
      🔒
```

不同桶上的操作可以具有更高的并发性，同时还会结合 CAS。

所以可以粗略对比：

```text
Hashtable
    ↓
synchronized
    ↓
锁整个表
    ↓
锁粒度大


ConcurrentHashMap
    ↓
CAS + synchronized
    ↓
更细粒度并发控制
    ↓
并发性能更好
```

### **面试回答**

**Hashtable 和 HashMap 有什么区别？Hashtable 怎么保证线程安全？**

可以回答：

HashMap 是线程不安全的，允许一个 null Key 和多个 null Value；Hashtable 是线程安全的，并且不允许 Key 和 Value 为 null。Hashtable 是比较早期的集合类，它主要通过在 `put`、`get`、`remove` 等核心方法上使用 `synchronized` 来保证线程安全，实例同步方法锁的是整个 Hashtable 对象，因此锁粒度比较大，并发性能相对较低。现在并发场景一般优先使用 ConcurrentHashMap。

一句话记忆：

**HashMap：不加锁。**  
**Hashtable：一把大锁。**  
**ConcurrentHashMap：CAS + 更细粒度的锁。**