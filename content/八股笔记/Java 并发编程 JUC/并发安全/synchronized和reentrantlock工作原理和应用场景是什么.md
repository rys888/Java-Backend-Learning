
[[#Q：synchronized 和 ReentrantLock 的原理和区别是什么？]]


这两个是 Java 并发里非常核心的一组对比。你可以先建立总认识：

`synchronized`和`ReentrantLock` 本质都是互斥锁：同一时刻只允许一个线程进入临界区。
`synchronized` 是 JVM 层面提供的关键字，使用简单、自动释放锁；`ReentrantLock` 是 JUC 提供的显式锁，功能更丰富，但需要自己 `unlock()`。

---

# **一、先理解它们解决什么问题**

假设：

```java
int count = 0;
```

两个线程同时：

```java
count++;
```

可能：

```text
线程A：读取 0
线程B：读取 0

线程A：0 + 1 → 写入1
线程B：0 + 1 → 写入1

最终 count = 1 ❌
```

所以需要互斥：

```text
                 🔒 锁

线程A ──抢锁──→ 成功 → count++ → 释放锁
线程B ──抢锁──→ 失败 → 等待
```

`synchronized` 和 `ReentrantLock` 都能完成这个事情。

---

# **二、synchronized 怎么用？**

最常见：

```java
synchronized (lock) {
    count++;
}
```

可以理解：

```text
进入 synchronized
       ↓
尝试获得 lock 的 monitor
       ↓
   ┌──成功──→ 执行代码
   │             ↓
   │          退出同步块
   │             ↓
   │          自动释放锁
   │
   └──失败──→ 等待锁
```

你前面学的 `BLOCKED` 就在这里出现。

如果其他线程已经持有这个 monitor：

```text
线程A → synchronized(lock)
             ↓
           获得锁 🔒

线程B → synchronized(lock)
             ↓
           获取失败
             ↓
           BLOCKED
```

---

# **三、synchronized 的底层原理 ⭐⭐⭐⭐⭐**

先记两个关键词：

**Monitor + 对象头**

Java 每个对象都可以作为：

```java
synchronized (lock)
```

中的锁对象。

JVM 对象大致可以理解：

```text
Java对象
│
├── 对象头 Header
│     ├── Mark Word
│     └── Class Pointer
│
└── 实例数据
```

其中 `Mark Word` 会保存与锁状态相关的信息。

而 `synchronized` 的同步语义和 JVM 的 **Monitor（监视器）机制**密切相关。

简化理解：

```text
                 lock 对象
                     │
                  Monitor
                     🔒
              ┌──────┴──────┐
              ↓             ↓
          当前持有者       竞争线程
           Thread A       Thread B
```

A 持有 monitor 后：

```text
A → 执行 synchronized 代码

B → 获取同一 monitor 失败
  → 等待
```

---

# **四、monitorenter / monitorexit**

对于：

```java
synchronized (lock) {
    count++;
}
```

从 JVM 字节码角度，经常会看到：

```text
monitorenter
     ↓
临界区代码
     ↓
monitorexit
```

可以粗略理解：

```text
monitorenter
= 尝试获得 monitor

monitorexit
= 释放 monitor
```

而 `synchronized` 方法的实现形式在 class 文件层面有所不同，通常通过方法的 `ACC_SYNCHRONIZED` 标志体现，由 JVM 在调用时处理 monitor。

所以面试回答：

synchronized 底层和 JVM Monitor 机制有关，同步代码块对应 `monitorenter` / `monitorexit` 等字节码语义。

---

# **五、synchronized 是可重入锁 ⭐⭐⭐⭐**

假设：

```java
synchronized (lock) {

    method();

}
```

而：

```java
void method() {

    synchronized (lock) {
        // ...
    }

}
```

线程 A 已经持有 `lock`，再次请求：

```text
线程A

第一次 synchronized(lock)
        ↓
      获得锁

        ↓

第二次 synchronized(lock)
        ↓
      同一个线程
        ↓
    允许再次进入 ✅
```

不会把自己锁死。

这就是：

**可重入锁。**

通常可以理解为锁内部会记录：

```text
当前持有线程
+
重入次数
```

退出一层：

```text
重入次数 - 1
```

全部退出之后：

```text
重入次数 = 0
↓
真正释放
```

---

# **六、ReentrantLock 是什么？**

名字直接翻译：

`ReentrantLock` = 可重入锁。

使用：

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();

try {

    count++;

} finally {

    lock.unlock();
}
```

一定要注意经典写法：

```java
lock.lock();

try {
    // 临界区
} finally {
    lock.unlock();
}
```

为什么必须 `finally`？

因为：

```text
获得锁
 ↓
执行代码
 ↓
突然异常 💥
 ↓
如果没有 finally
 ↓
unlock 没执行
 ↓
其他线程一直拿不到锁
```

而 `synchronized`：

```java
synchronized (lock) {

}
```

离开同步块时 JVM 会帮你释放，不需要手动 `unlock()`。

---

# **七、ReentrantLock 工作原理 ⭐⭐⭐⭐⭐**

这里你现在不用钻太深源码，记住：

**ReentrantLock 主要基于 AQS + CAS 实现。**

AQS：

**AbstractQueuedSynchronizer，抽象队列同步器。**

可以先把它想成：

```text
ReentrantLock
      │
      ↓
     AQS
      │
 ┌────┴────────────┐
 ↓                 ↓
state            等待队列
锁状态           排队的线程
```

简化：

```text
state = 0
↓
锁没人拿

state = 1
↓
线程A拿到锁
```

线程 A：

```text
CAS尝试：

state
0 → 1

成功
↓
获得锁
```

这时候线程 B：

```text
CAS：

期望 state=0

但实际 state=1
↓
失败
↓
进入 AQS 等待队列
```

于是：

```text
       锁状态
       state=1
          ↑
      Thread A
       正在执行


AQS等待队列：

Thread B → Thread C → Thread D
```

A 执行：

```java
lock.unlock();
```

释放锁后：

```text
state → 0
   ↓
唤醒等待线程
   ↓
继续竞争锁
```

---

# **八、ReentrantLock 为什么也叫“可重入”？**

假设 A 已经拿锁：

```text
state = 1
owner = Thread A
```

A 又：

```java
lock.lock();
```

发现：

```text
当前锁持有者
= 我自己
```

于是允许重入：

```text
state = 2
```

再进入：

```text
state = 3
```

释放：

```text
unlock → state 3 → 2
unlock → state 2 → 1
unlock → state 1 → 0
```

`state = 0` 才真正释放。

所以：

**synchronized 和 ReentrantLock 都是可重入锁。**

---

# **九、两者最大的区别是什么？⭐⭐⭐⭐⭐**

这个表建议直接掌握：

|**对比**|**synchronized**|**ReentrantLock**|
|---|---|---|
|类型|Java 关键字/JVM 同步机制|JUC 中的类|
|是否可重入|✅|✅|
|锁释放|**自动释放**|**手动 unlock**|
|可中断获取锁|普通进入方式不提供 `lockInterruptibly` 这种 API|✅ `lockInterruptibly()` |
|尝试获取锁|❌ 没有 `tryLock` API|✅ `tryLock()` |
|超时获取|❌|✅|
|公平锁|不提供公平策略配置|✅ 支持|
|多条件队列|一个 monitor 的 wait-set|✅ 多个 `Condition` |
|基础实现|JVM Monitor 等机制|AQS + CAS 等|
|使用难度|简单|更灵活、稍复杂|

---

# **十、ReentrantLock 最大优势：tryLock ⭐⭐⭐⭐⭐**

`synchronized`：

```java
synchronized (lock) {
}
```

基本是：

我要进去，锁暂时拿不到就等。

而 ReentrantLock：

```java
if (lock.tryLock()) {

    try {
        // 拿到了
    } finally {
        lock.unlock();
    }

} else {

    // 没拿到，做其他事情
}
```

可以：

**试一下，拿不到就算了。**

还可以限时：

```java
if (lock.tryLock(3, TimeUnit.SECONDS)) {
    try {
        // ...
    } finally {
        lock.unlock();
    }
}
```

意思：

最多等 3 秒。

这就是 synchronized 不方便直接做到的。

---

# **十一、ReentrantLock 可以响应中断**

前面你刚学过：

```java
thread.interrupt();
```

ReentrantLock 可以：

```java
lock.lockInterruptibly();
```

如果线程正在等待锁，可以响应中断。

比如：

```text
线程B
 ↓
等待 lock
 ↓
等了很久
 ↓
其他线程 interrupt()
 ↓
B可以放弃等待
```

对于需要：

**取消任务、避免无限等待**

的场景很有价值。

---

# **十二、公平锁**

ReentrantLock：

```java
new ReentrantLock(true);
```

可以创建公平锁。

粗略理解：

```text
B先等
C后等
D最后等

↓
尽量按照等待顺序获取
```

默认：

```java
new ReentrantLock();
```

是非公平锁。

新来的线程有机会直接参与竞争：

```text
B：等很久了
C：等着
D：刚来

锁释放

大家竞争
```

不保证严格按照先来后到。

公平锁通常会带来额外调度/吞吐开销，因此不是“公平一定更好”。

---

# **十三、Condition 是 ReentrantLock 的另一个重要优势**

你上一问刚学：

```java
wait()
notify()
```

`synchronized`：

```java
synchronized (lock) {

    lock.wait();

}
```

一个 monitor 有对应的等待集合。

而 ReentrantLock 可以：

```java
Condition notEmpty = lock.newCondition();
Condition notFull = lock.newCondition();
```

例如生产者消费者：

```text
              ReentrantLock
                    │
           ┌────────┴────────┐
           ↓                 ↓
       notEmpty           notFull
           │                 │
     等待“非空”         等待“非满”
       的消费者           的生产者
```

可以更精确地唤醒不同类型的等待线程。

这也是：

```text
wait       ↔ await
notify     ↔ signal
notifyAll  ↔ signalAll
```

---

# **十四、什么时候用 synchronized？**

对于绝大多数**简单互斥同步**：

```java
synchronized (lock) {
    // 修改共享数据
}
```

优先考虑它就很好。

例如：

```text
简单共享变量保护
简单临界区
简单线程同步
不需要高级锁功能
```

优势：

**代码简单、自动释放锁、不容易因为忘记 unlock 出错。**

现代 JVM 已经对 `synchronized` 做了大量优化，选择两者主要看**功能需求和代码设计**，而不是简单认为 ReentrantLock 一定更快。

---

# **十五、什么时候用 ReentrantLock？**

当你明确需要这些能力：



```text
需要 tryLock
      ↓
ReentrantLock

需要超时获取锁
      ↓
ReentrantLock

等待锁时需要响应 interrupt
      ↓
ReentrantLock

需要公平锁
      ↓
ReentrantLock

需要多个 Condition
      ↓
ReentrantLock
```

比如：

“最多等锁 2 秒，拿不到就返回失败。”

这种：

```java
lock.tryLock(2, TimeUnit.SECONDS)
```

ReentrantLock 就非常合适。

---

# **十六、把两者原理串起来**

你可以形成这张图：

```text
              Java互斥锁
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
 synchronized          ReentrantLock
        │                   │
 JVM关键字/机制            JUC类
        │                   │
 Monitor等机制            AQS
        │                   │
 对象头锁信息           state + 等待队列
                            │
                           CAS

        ↓                   ↓

 自动释放锁             手动 unlock
                        tryLock
                        可中断
                        公平锁
                        Condition
```

---

## Q：synchronized 和 ReentrantLock 的原理和区别是什么？

`synchronized` 和 `ReentrantLock` 都属于可重入的互斥锁，用于保证同一时刻只有一个线程进入临界区。

`synchronized` 是 Java 关键字，由 JVM 提供同步语义，与对象 Monitor 机制相关，同步代码块在字节码层面会涉及 `monitorenter` 和 `monitorexit`，退出同步区域时 JVM 会自动释放锁。

`ReentrantLock` 是 JUC 提供的显式锁，主要基于 AQS 实现，通过同步状态 `state`、CAS 和等待队列管理锁的获取与释放，需要在 `finally` 中手动 `unlock()`。

两者都支持可重入，但 ReentrantLock 功能更丰富，支持 `tryLock`、超时获取、可中断获取、公平锁以及多个 Condition。因此普通简单同步场景通常使用 synchronized；需要高级锁控制能力时使用 ReentrantLock。