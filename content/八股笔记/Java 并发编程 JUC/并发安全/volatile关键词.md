
[[#Q：volatile 有什么作用？]]

`volatile` 是 Java 并发里非常高频的关键词。

**volatile 主要保证两个东西：可见性 + 有序性，但不能保证复合操作的原子性。**

---

## **1. 为什么需要 volatile？**

假设有两个线程共享变量：

```java
boolean running = true;
```

线程 A：

```java
while (running) {
    // 工作
}
```

线程 B：

```java
running = false;
```

按照直觉：

```text
线程B：running = false
          ↓
线程A发现 running = false
          ↓
退出循环
```

但在多线程环境下，如果没有正确的同步手段，JMM **不保证线程 A 必然按你期望及时观察到 B 的修改**。

可以用我们之前讲 JMM 的抽象模型理解：

```text
             共享变量 running
                    ↑
             主内存 / 共享内存
              ↗           ↖
         Thread A        Thread B
       本地工作状态      本地工作状态
```

于是：

```text
B修改 running = false

但是

A仍可能继续使用之前观察到的 true
```

---

# **2. volatile 第一作用：保证可见性 ⭐⭐⭐⭐⭐**

改成：

```java
volatile boolean running = true;
```

当线程 B：

```java
running = false;
```

根据 JMM 对 volatile 的规定，其他线程后续读取这个 volatile 变量时能够观察到相应的最新写入。

因此：

```text
Thread B
running = false
      ↓
volatile 写

      ↓ 可见

Thread A
重新读取 running
      ↓
false
```

所以：

**一个线程对 volatile 变量的写，对之后读取这个变量的其他线程可见。**

JMM 里还有一条非常重要的 happens-before：

**对一个 volatile 变量的写，happens-before 后续对该变量的读。**

这就是它可见性保证的重要理论基础。

---

# **3. volatile 第二作用：保证有序性 ⭐⭐⭐⭐⭐**

你之前学 JMM：

```text
三大问题：

原子性
可见性
有序性
```

CPU/JIT/编译器在不改变**单线程语义**的前提下，可能进行指令重排序。

比如：

```java
a = 10;
b = 20;
```

在允许的情况下，底层实际执行顺序不一定机械地与源码一一对应。

但是多线程情况下，一些重排序可能造成问题。

`volatile` 会通过 JMM 规定的内存语义限制相关重排序，可以粗略理解为：

**volatile 读写周围建立了不能随意跨越的排序边界。**

面试经常会说：

**volatile 通过内存屏障等机制实现可见性和禁止特定的指令重排序。**

注意是：

❌ 完全禁止所有指令重排序  
✅ **禁止会破坏 volatile 内存语义的特定重排序**

---

# **4. 最经典场景：双重检查单例 DCL**

这也是 volatile 高频考点。

```java
class Singleton {

    private static volatile Singleton instance;

    public static Singleton getInstance() {

        if (instance == null) {

            synchronized (Singleton.class) {

                if (instance == null) {
                    instance = new Singleton();
                }

            }
        }

        return instance;
    }
}
```

为什么 `instance` 要加 volatile？

因为：

```java
instance = new Singleton();
```

概念上可以拆成类似：

```text
① 分配内存
② 初始化 Singleton 对象
③ instance 指向这块内存
```

我们希望：

```text
1 → 2 → 3
```

如果缺少合适的排序约束，某些情况下可能出现对其他线程可观察到的：

```text
1 → 3 → 2
```

也就是：

```text
内存已经分配
↓
instance 已经不是 null
↓
但对象初始化相关写入还没被另一个线程正确观察到
```

另一个线程：

```java
if (instance != null) {
    return instance;
}
```

就可能拿到一个没有按预期安全发布的对象。

所以 DCL 中：

```java
private static volatile Singleton instance;
```

利用 volatile 的**可见性和排序语义**保证安全发布。

---

# **5. volatile 最大重点：不能保证复合操作原子性 ⭐⭐⭐⭐⭐**

这是面试最爱问的。

例如：

```java
volatile int count = 0;
```

两个线程不断：

```java
count++;
```

是不是线程安全？

**不是。**

因为：

```java
count++;
```

不是一个不可分割的操作。

可以粗略拆成：

```text
① 读取 count
② count + 1
③ 写回 count
```

假设：

```text
count = 0
```

线程 A：

```text
读取 0
```

线程 B：

```text
读取 0
```

然后：

```text
A：0 + 1 → 写入1

B：0 + 1 → 写入1
```

最终：

```text
count = 1
```

而不是：

```text
count = 2
```

所以即使：

```java
volatile int count;
```

也没用。

volatile 能保证：

“B 能看到 A 对 count 的写。”

但是不能保证：

“`读取 → +1 → 写回` 整体不会被其他线程插进来。”

---

# **6. 那 count++ 应该怎么办？**

你现在已经学过这些了：

### **synchronized**

```java
synchronized (lock) {
    count++;
}
```

通过互斥保证整个操作。

### **ReentrantLock**

```java
lock.lock();
try {
    count++;
} finally {
    lock.unlock();
}
```

### **AtomicInteger**

```java
AtomicInteger count = new AtomicInteger();

count.incrementAndGet();
```

底层利用 CAS 等机制实现原子更新。

所以：

```text
volatile
    ↓
保证“看得见”
但不能把 count++ 变成一个不可分割操作


AtomicInteger
    ↓
CAS等机制
    ↓
可以原子更新
```

---

# **7. volatile 和 synchronized 区别**

这是非常经典的面试题。

||**volatile**|**synchronized**|
|---|---|---|
|可见性|✅|✅|
|有序性|✅ 提供特定排序保证|✅|
|原子性|❌ 不保证复合操作|✅ 临界区互斥|
|阻塞线程|❌|竞争时可能|
|适用|状态标记等|复合共享操作|

比如：

```java
volatile boolean running;
```

非常适合。

因为：

```java
running = false;
```

本身就是简单的单次读写，而且主要需求是：

**让其他线程及时看到状态变化。**

但是：

```java
volatile int count;

count++;
```

不行，因为这里需要的是：

**复合操作的原子性。**

---

# **8. volatile 和 CAS 又是什么关系？**

你现在刚学完 CAS，这两个经常一起出现。

例如很多 JUC 类里会看到：

```text
volatile
+
CAS
```

可以粗略理解：

```text
volatile
↓
让线程正确观察共享状态
+ 提供排序语义

CAS
↓
原子地比较并修改状态
```

例如你刚学 AQS 的 `state`，它的并发控制就涉及 volatile 语义和 CAS 更新。

所以：

**volatile 和 CAS 经常配合，而不是互相替代。**

# **10. volatile 最典型的应用**

你面试阶段重点记两个。
### **状态标志**

```java
private volatile boolean running = true;
```

```text
Thread A：
while (running) {
    ...
}

Thread B：
running = false;
```

核心需求：

可见性。

### **DCL 单例**

```java
private static volatile Singleton instance;
```

核心：

**可见性 + 防止不安全的重排序/保证安全发布。**

---

# **11. 把你目前学的并发知识串起来**

现在其实已经可以形成一个体系：

```text
                  JMM
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
     原子性       可见性       有序性
       │           │           │
       │         volatile ─────┘
       │
   ┌───┴────────────┐
   ↓                ↓
锁机制              CAS
   ↓                ↓
synchronized    AtomicInteger
ReentrantLock       AQS
```

当然这张图是帮助理解，不代表这些机制只负责单一属性。

---

## Q：volatile 有什么作用？

`volatile` 是 Java 提供的一种轻量级的线程同步机制，主要保证变量的**可见性和有序性**。当一个线程写入 volatile 变量后，后续其他线程读取该变量时能够观察到相应的写入，并且 volatile 读写具有特定的 happens-before 和重排序约束。

但是 volatile **不能保证复合操作的原子性**，例如 `count++` 包含读取、加一和写回多个步骤，即使 count 使用 volatile 修饰，在多线程环境下仍然可能发生丢失更新。如果需要保证这种复合操作的原子性，可以使用 synchronized、ReentrantLock 或 AtomicInteger 等。