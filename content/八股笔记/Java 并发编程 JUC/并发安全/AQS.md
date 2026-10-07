
**AQS 可以理解为 JUC 中用来实现“锁和线程同步器”的基础框架。**
**AbstractQueuedSynchronizer，抽象队列同步器。**

**AQS = 一个 `state` 同步状态 + 一个 FIFO/CLH 风格等待队列 + CAS + park/unpark。**

**资源能拿到 → 线程继续执行；资源拿不到 → 把线程组织起来排队并挂起；资源释放 → 唤醒等待线程继续竞争。**

[[#Q：介绍一下 AQS]]

---

## **一、为什么需要 AQS？**

假设你要自己实现一把锁。

你首先需要知道：

```text
① 锁现在有没有人拿？
② 谁拿着锁？
③ 其他线程抢不到怎么办？
④ 怎么让等待线程别一直消耗 CPU？
⑤ 锁释放后叫醒谁？
```

如果每一种并发工具都自己重新写一遍这些逻辑，会非常麻烦。

于是 Java 提供 AQS，把这些通用能力抽出来：

```text
                    AQS
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     同步状态      等待队列      阻塞/唤醒
      state       CLH风格队列   park/unpark
        │
       CAS
```

然后：

```text
ReentrantLock
Semaphore
CountDownLatch
...
```

可以在 AQS 基础上实现自己的同步规则。

---

# **二、AQS 第一核心：state ⭐⭐⭐⭐⭐**

AQS 内部有一个同步状态：

```java
private volatile int state;
```

不同同步器，对 `state` 的解释不一样。

例如：

```text
ReentrantLock

state = 0
→ 没有线程持有锁

state = 1
→ 某线程拿了一次锁

state = 2
→ 同一个线程重入了一次

state = 3
→ 又重入一次
```

所以：

**ReentrantLock 中，state 可以表示锁的占用/重入状态。**

而 `Semaphore`：

```text
state = 剩余许可证数量
```

`CountDownLatch`：

```text
state = 剩余计数
```

所以不要背：

`state 就是锁状态。`

更准确：

**state 是 AQS 的同步状态，具体含义由具体同步器决定。**

---

# **三、state 为什么是 volatile？**

因为多个线程都会观察这个状态：

```text
线程A ──→
线程B ──→ state
线程C ──→
```

所以需要保证相关状态读取的可见性。

你之前学的 JMM 就接上了：

**volatile → 可见性 + 相应的有序性保证。**

但仅仅 `volatile` 不够。

例如两个线程同时想：

```text
state：

0 → 1
```

必须保证只有一个成功。

于是需要：

**CAS。**

---

# **四、AQS 第二核心：CAS ⭐⭐⭐⭐⭐**

假设：

```text
state = 0
```

线程 A 和 B 同时抢 ReentrantLock：

```text
                  state = 0
                     │
            ┌────────┴────────┐
            ↓                 ↓
         Thread A          Thread B

         CAS 0→1           CAS 0→1
            ↓                 ↓
           成功               失败
            ↓                 ↓
          获得锁            没获得锁
```

CAS 的意思可以粗略理解：

“如果 state 现在还是我预期的值，就原子地把它修改成新值。”

所以：

```text
state
  +
CAS
```

负责：

**安全地竞争/修改同步状态。**

---

# **五、CAS 失败怎么办？**

这才是 AQS 名字里的：

**Queued —— 队列。**

线程 A 拿到了资源：

```text
A：正在持锁
```

B、C、D 都失败了。

AQS 会把等待线程组织成一个 **CLH 风格的双向等待队列**，简化理解：

```text
A：正在执行 🔒


AQS：

Head
 ↓
Node(B) ⇄ Node(C) ⇄ Node(D)
```

可以理解：

**抢不到就排队。**

Node 里面会保存线程以及等待状态等相关信息。

所以 AQS：

```text
state
↓
“资源现在什么状态？”

等待队列
↓
“拿不到资源的人怎么办？”
```

---

# **六、为什么排队以后还要 park？**

假设 A 执行一个任务要 10 秒。

B 在后面一直：

```java
while (true) {
    // 我能拿锁了吗？
    // 我能拿锁了吗？
    // 我能拿锁了吗？
}
```

那 CPU 就被白白浪费了。

所以 AQS 在适当的时候：

```java
LockSupport.park();
```

让 B 暂停执行。

于是：

```text
B
↓
抢锁失败
↓
进入 AQS 队列
↓
判断当前暂时不能获得
↓
park()
↓
WAITING
↓
不再持续占 CPU 空转
```

这正好和你刚才学的 Java 线程状态接起来。

---

# **七、资源释放之后怎么办？**

例如 ReentrantLock：

```java
lock.unlock();
```

假设 A 完全释放：

```text
state

1 → 0
```

AQS 会让合适的后继等待线程恢复执行，底层会涉及：

```java
LockSupport.unpark(thread);
```

比如 B：

```text
A unlock()
    ↓
state → 0
    ↓
AQS处理等待队列
    ↓
unpark(B)
    ↓
B从 park 返回
    ↓
再次尝试获取同步状态
```

这里一定记住你上一问刚学的：

**unpark ≠ 把锁直接交给 B。**

而是：

**“B，你可以醒来继续尝试了。”**

---

# **八、所以 AQS 的完整流程**

假设 A、B、C 抢一把 ReentrantLock：

```text
                    lock()
                      ↓
                尝试获取 state
                      ↓
                   CAS等机制
                      │
              ┌───────┴───────┐
              ↓               ↓
            成功              失败
              ↓               ↓
           获得资源        加入AQS队列
                              ↓
                         Node排队
                              ↓
                         条件合适时
                              ↓
                            park()
                              ↓
                           WAITING
                              │
                              │
持锁线程 unlock()             │
        ↓                     │
     释放资源                  │
        ↓                     │
     state改变                 │
        ↓                     │
  唤醒合适的后继 ──────────────┘
        ↓
      unpark
        ↓
   被唤醒线程再次尝试
```

这就是 AQS 最核心的思想。

---

# **九、AQS 为什么叫“抽象”队列同步器？**

因为 AQS 并不知道：

**“怎样才算真正获得资源？”**

具体规则交给子类实现。

例如独占模式会涉及类似：

```java
tryAcquire()
tryRelease()
```

共享模式会涉及：

```java
tryAcquireShared()
tryReleaseShared()
```

你可以理解：

```text
AQS负责：

排队
阻塞
唤醒
state
CAS
等待管理
        ↑
        │
具体同步器负责：
“什么情况下算获取成功？”
“什么情况下算释放成功？”
```

这就是一个非常典型的：

**模板方法设计思想。**

---

# **十、AQS 有两种模式：独占和共享 ⭐⭐⭐⭐**

这个非常重要。

### **独占模式**

同一时刻主要由一个线程独占同步状态。

典型：

```text
ReentrantLock
```

```text
          🔒
           ↑
        Thread A

Thread B → 等
Thread C → 等
```

---

### **共享模式**

可以允许多个线程同时获得共享资源。

例如：

```java
Semaphore semaphore = new Semaphore(3);
```

相当于：

```text
许可证 = 3

线程A → 拿一个 ✅
线程B → 拿一个 ✅
线程C → 拿一个 ✅
线程D → 没了 → 等待
```

所以：

```text
AQS

独占模式
↓
ReentrantLock

共享模式
↓
Semaphore
CountDownLatch（利用共享获取/释放语义）
```

---

# **十一、用 ReentrantLock 把 AQS 串起来**

你刚学的 ReentrantLock 可以理解成：

```text
                 ReentrantLock
                       ↓
                      AQS
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
      state           CAS          等待队列
        │                              │
   锁/重入次数                       Node
                                       │
                                     park
                                       ↓
                                    WAITING
```

线程 A：

```java
lock.lock();
```

```text
state = 0
↓
尝试获取
↓
成功
↓
state = 1
↓
A获得锁
```

A 再：

```java
lock.lock();
```

发现持锁者就是自己：

```text
state

1 → 2
```

实现：

**可重入。**

B：

```java
lock.lock();
```

发现 A 持有：

```text
获取失败
↓
AQS排队
↓
park
```

A：

```java
lock.unlock();
```

第一次：

```text
state 2 → 1
```

还没有真正释放。

第二次：

```text
state 1 → 0
↓
真正释放
↓
AQS唤醒后继
↓
unpark
```

这样你前面所有知识就连起来了。

---

# **十二、AQS、Monitor 不要混**

可以这样对照：

```text
synchronized
     ↓
JVM Monitor机制
     ↓
monitorenter / monitorexit
     ↓
wait / notify


ReentrantLock
     ↓
AQS
     ↓
state + CAS + 等待队列
     ↓
LockSupport
     ↓
park / unpark
```

但是不要说：

AQS 就是 Java 实现的 Monitor。

它们不是同一个东西，只是都在解决：

**多线程同步、竞争、等待、唤醒**

这些类似的问题。

---

# **十三、AQS 和哪些类有关？**

面试最常见的几个：

```text
                    AQS
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
ReentrantLock    Semaphore    CountDownLatch
```

你以后还会碰到 `ReentrantReadWriteLock` 等。

所以学懂 AQS 的价值就在于：

**不是为了背 AQS 源码，而是理解很多 JUC 工具为什么都是类似的“state + 排队 + park/unpark”。**

---

## Q：介绍一下 AQS

AQS 全称 AbstractQueuedSynchronizer，是 JUC 中用于构建锁和同步器的基础框架，例如 ReentrantLock、Semaphore、CountDownLatch 等都基于或利用 AQS 的同步机制。

AQS 的核心是一个 `state` 同步状态和一个 CLH 风格的等待队列。线程会通过 CAS 等方式尝试修改 state 来获取同步资源，如果获取失败，则会被组织到等待队列中，并在合适的时候通过 `LockSupport.park()` 挂起，避免一直占用 CPU。

当持有同步资源的线程释放资源后，AQS 会根据队列状态唤醒合适的后继线程，底层会使用 `LockSupport.unpark()`，被唤醒的线程再重新尝试获取同步状态。

AQS 同时支持独占模式和共享模式，例如 ReentrantLock 主要使用独占模式，而 Semaphore、CountDownLatch 等会利用共享模式。