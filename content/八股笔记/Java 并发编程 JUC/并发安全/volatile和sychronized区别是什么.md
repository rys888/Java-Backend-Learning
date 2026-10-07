可以把它俩理解成解决并发问题的**两个不同层级的工具**：

**volatile：不加锁，重点解决“别人能不能及时看到我的修改 + 指令顺序”。**  
**synchronized：加锁互斥，重点解决“同一时刻只能一个线程操作”，同时也保证可见性和有序性。**

[[#Q：volatile 和 synchronized 有什么区别？]]

| **对比**   | `volatile`         | `synchronized`         |
| -------- | ------------------ | ---------------------- |
| 原子性      | ❌ 不保证复合操作原子性       | ✅ 临界区互斥，从而保护复合操作       |
| 可见性      | ✅                  | ✅                      |
| 有序性      | ✅ 限制特定重排序          | ✅                      |
| 是否加锁     | ❌                  | ✅                      |
| 是否可能阻塞线程 | ❌ 不因 volatile 本身阻塞 | ✅ 锁竞争时可能               |
| 修饰对象     | 变量                 | 方法、代码块                 |
| 可重入      | 不涉及                | ✅                      |
| 典型场景     | 状态标志、DCL           | `count++`、多个操作需要整体线程安全 |

### **1. volatile 为什么不能替代 synchronized？**

比如：

```java
volatile int count = 0;

count++;
```

即使 `count` 是 volatile，仍然线程不安全，因为 `count++` 可以理解成：

```text
读取 count
   ↓
+ 1
   ↓
写回 count
```

两个线程可能：

```text
初始 count = 0

线程A              线程B
  ↓                  ↓
读取0               读取0
  ↓                  ↓
+1                  +1
  ↓                  ↓
写入1               写入1

最终 count = 1 ❌
```

volatile 只能保证大家能看到新的 `count`，**不能阻止两个线程同时执行这几个步骤**。

而：

```java
synchronized (lock) {
    count++;
}
```

相当于：

```text
线程A拿锁
 ↓
读取 → +1 → 写回
 ↓
释放锁

线程B才能进来
 ↓
读取 → +1 → 写回
```

最终：

```text
count = 2 ✅
```

所以最重要的区别就是：

**volatile 不提供互斥；synchronized 提供互斥。**

---

### **2. 那为什么 synchronized 也有可见性？**

你前面学过 JMM 的 happens-before：

**对一个 monitor 的解锁，happens-before 后续对同一个 monitor 的加锁。**

比如：

```java
synchronized (lock) {
    count = 100;
}
```

A 释放 `lock` 后，B 再获得**同一个** `lock` **：

```java
synchronized (lock) {
    System.out.println(count);
}
```

JMM 保证相应写入对 B 可见。

所以 synchronized 不只是：

```text
加锁 → 防止别人进来
```

它还同时提供相应的：

```text
互斥
+
可见性
+
有序性
```

---

### Q：volatile 和 synchronized 有什么区别？

`volatile` 和 `synchronized` 都可以提供可见性和一定的有序性保证，但 volatile 不提供互斥，因此不能保证 `count++` 等复合操作的原子性；而 synchronized 通过 Monitor 实现互斥，同一时刻只有获得同一把锁的线程才能进入临界区，因此可以保护复合操作，同时也具有可见性和有序性保证。

volatile 更适合状态标志等不需要互斥的场景，而 synchronized 更适合多个线程需要互斥访问共享数据的场景。