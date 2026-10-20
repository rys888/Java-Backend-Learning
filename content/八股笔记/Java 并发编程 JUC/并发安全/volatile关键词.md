[[#Q：volatile 有什么作用？]]

`volatile` 是 Java 并发里非常高频的关键词，主要保证两个东西：**可见性 + 有序性，但不能保证复合操作的原子性**。

---

## 1. 为什么需要 volatile

先看一个最常见的场景。两个线程共享一个布尔变量：

```java
boolean running = true;
```

线程 A 循环等待，线程 B 负责把标志位改掉：

```java
// 线程 A
while (running) {
    // 工作
}

// 线程 B
running = false;
```

按照直觉，B 把 running 改成 false 之后，A 应该马上退出循环。但多线程环境下如果没有同步手段，JMM 并不保证 A 能及时观察到 B 的修改。

用 JMM 的抽象模型看就是这样：主内存里放共享变量，每个线程有自己的工作状态，线程之间的修改不是立刻同步的。

```text
             共享变量 running
                    ↑
             主内存 / 共享内存
              ↗           ↖
         Thread A        Thread B
       本地工作状态      本地工作状态
```

于是会出现这种情况：B 已经把 running 改成了 false，A 仍然拿着之前观察到的 true 在循环。

---

## 2. 第一作用：保证可见性 ⭐⭐⭐⭐⭐

把变量改成：

```java
volatile boolean running = true;
```

这时候线程 B 执行 `running = false`，根据 JMM 对 volatile 的规定，其他线程后续读取这个 volatile 变量时能够观察到相应的最新写入。

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

一句话总结：**一个线程对 volatile 变量的写，对之后读取这个变量的其他线程可见。**

JMM 里对应的 happens-before 规则是：**对一个 volatile 变量的写，happens-before 后续对该变量的读。** 这条规则就是可见性保证的重要理论基础。

---

## 3. 第二作用：保证有序性 ⭐⭐⭐⭐⭐

JMM 里的三大问题是原子性、可见性、有序性。CPU、JIT、编译器在不改变**单线程语义**的前提下，可能进行指令重排序，比如：

```java
a = 10;
b = 20;
```

单线程下换个顺序没问题，但多线程下有些重排序会出问题。volatile 会通过 JMM 规定的内存语义限制相关重排序，粗略理解就是：**volatile 读写周围建立了不能随意跨越的排序边界。**

面试里常说的是：**volatile 通过内存屏障等机制实现可见性和禁止特定的指令重排序。** 注意范围：

- ❌ 完全禁止所有指令重排序
- ✅ 只禁止会破坏 volatile 内存语义的特定重排序

---

## 4. 最经典场景：双重检查单例 DCL

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

为什么 instance 必须加 volatile？关键在这一行：

```java
instance = new Singleton();
```

它不是一个原子动作，概念上可以拆成三步：**① 分配内存；② 初始化 Singleton 对象；③ instance 指向这块内存。**

正常期望的顺序是 1 → 2 → 3。但如果缺少合适的排序约束，某些情况下可能变成 1 → 3 → 2：内存已经分配，instance 也已经不是 null，但对象初始化相关的写入还没被另一个线程正确观察到。这时候另一个线程走到 `if (instance != null) return instance;`，拿到的就是一个没有按预期安全发布的对象。

所以 DCL 里的 `private static volatile Singleton instance;`，利用的就是 volatile 的**可见性和排序语义**来保证安全发布。

---

## 5. 最大重点：不能保证复合操作原子性 ⭐⭐⭐⭐⭐

这是面试最爱问的点。比如：

```java
volatile int count = 0;
```

两个线程不断执行 `count++`，这样线程安全吗？**不是。** 因为 `count++` 本身不是不可分割的操作，可以粗略拆成：**① 读取 count；② count + 1；③ 写回 count。**

假设 count = 0，线程 A 和 B 同时读到 0，各自加 1 再写回：

```text
线程 A 读 count = 0
线程 B 读 count = 0
线程 A 写回 1
线程 B 写回 1
最终 count = 1（期望是 2）
```

所以就算用 `volatile int count;` 也没用。volatile 能保证"B 能看到 A 对 count 的写"，但不能保证"读取 → +1 → 写回"这整个动作不被其他线程插进来。

---

## 6. count++ 应该怎么办

常见的三种方式。

**synchronized**：通过互斥保证整个操作。

```java
synchronized (lock) {
    count++;
}
```

**ReentrantLock**：同样是锁，只是手动加锁和解锁。

```java
lock.lock();
try {
    count++;
} finally {
    lock.unlock();
}
```

**AtomicInteger**：底层利用 CAS 等机制实现原子更新。

```java
AtomicInteger count = new AtomicInteger();

count.incrementAndGet();
```

区别可以这样记：**volatile 保证"看得见"，但没法把 count++ 变成一个不可分割的操作；AtomicInteger 靠 CAS 等机制才能做到原子更新。**

---

## 7. volatile 和 synchronized 区别

经典面试题，直接上表：

||**volatile**|**synchronized**|
|---|---|---|
|可见性|✅|✅|
|有序性|✅ 提供特定排序保证|✅|
|原子性|❌ 不保证复合操作|✅ 临界区互斥|
|阻塞线程|❌|竞争时可能|
|适用|状态标记等|复合共享操作|

`volatile boolean running;` 非常适合，因为 `running = false` 本身就是简单的单次读写，主要需求是让其他线程及时看到状态变化。但 `volatile int count; count++;` 就不行，这里需要的是复合操作的原子性。

---

## 8. volatile 和 CAS 又是什么关系

这两个经常一起出现，很多 JUC 类里都是 **volatile + CAS** 的组合。可以粗略理解成：**volatile 让线程正确观察共享状态，并提供排序语义；CAS 负责原子地比较并修改状态。**

比如 AQS 的 `state`，它的并发控制就同时涉及 volatile 语义和 CAS 更新。所以两者的关系是配合，不是互相替代。

---

## 9. volatile 最典型的应用

面试阶段重点记两个。

**状态标志**：`private volatile boolean running = true;`，线程 A 循环读取，线程 B 改标志位，核心需求就是可见性。

**DCL 单例**：`private static volatile Singleton instance;`，核心是可见性 + 防止不安全的重排序，保证安全发布。

---

## 10. 把并发知识串起来

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

注意这张图只是帮助理解，不代表这些机制只负责单一属性。

---

## Q：volatile 有什么作用？

`volatile` 是 Java 提供的一种轻量级的线程同步机制，主要保证变量的**可见性和有序性**。当一个线程写入 volatile 变量后，后续其他线程读取该变量时能够观察到相应的写入，并且 volatile 读写具有特定的 happens-before 和重排序约束。

但是 volatile **不能保证复合操作的原子性**，例如 `count++` 包含读取、加一和写回多个步骤，即使 count 使用 volatile 修饰，在多线程环境下仍然可能发生丢失更新。如果需要保证这种复合操作的原子性，可以使用 synchronized、ReentrantLock 或 AtomicInteger 等。


已 xhs
