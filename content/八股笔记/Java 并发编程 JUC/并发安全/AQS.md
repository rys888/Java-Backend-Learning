**AQS 可以理解为 JUC 中用来实现"锁和线程同步器"的基础框架。** 全称 AbstractQueuedSynchronizer，抽象队列同步器。

核心就四块：**一个 `state` 同步状态 + 一个 FIFO/CLH 风格等待队列 + CAS + park/unpark。** 资源能拿到就继续执行；拿不到就排队并挂起；释放时唤醒等待线程继续竞争。

[[#Q：介绍一下 AQS]]

---

## 1. 为什么需要 AQS

自己实现一把锁，要处理的问题其实就那几个：**锁有没有人拿、谁拿着、抢不到怎么办、怎么让等待线程别空转 CPU、释放后叫醒谁。** 每种并发工具都重写一遍太麻烦，AQS 就把这些通用能力抽了出来：

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

ReentrantLock、Semaphore、CountDownLatch 都是在 AQS 基础上实现自己的同步规则。

---

## 2. 第一核心：state ⭐⭐⭐⭐⭐

AQS 内部有一个同步状态：

```java
private volatile int state;
```

不同同步器对 state 的解释不一样。ReentrantLock 里它是锁的占用/重入状态：**0 表示没有线程持有，1 表示某线程拿了一次锁，2 表示同一个线程重入了一次，再重入就继续加。** Semaphore 里它是剩余许可证数量，CountDownLatch 里是剩余计数。

更准确的说法是：**state 是 AQS 的同步状态，具体含义由具体同步器决定。**

state 用 volatile 修饰，是因为多个线程都要读它，需要保证可见性。但只有 volatile 不够：两个线程同时把 0 改成 1，必须保证只有一个成功，这就需要 CAS。

---

## 3. 第二核心：CAS ⭐⭐⭐⭐⭐

假设 state = 0，线程 A 和 B 同时抢 ReentrantLock：

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

CAS 的意思可以粗略理解成：**如果 state 现在还是我预期的值，就原子地把它修改成新值。** state + CAS 一起，负责安全地竞争和修改同步状态。

---

## 4. CAS 失败：进入等待队列

A 拿到锁之后，B、C、D 的 CAS 都失败了，AQS 会把它们组织成一个 **CLH 风格的双向等待队列**。简化理解就是抢不到就排队：

```text
A：正在执行 🔒

AQS：
Head
 ↓
Node(B) ⇄ Node(C) ⇄ Node(D)
```

Node 里保存线程和等待状态等信息。所以 AQS 的两块核心可以这样对应：**state 回答"资源现在什么状态"，等待队列回答"拿不到资源的人怎么办"。**

---

## 5. 排队之后为什么要 park

假设 A 执行一个任务要 10 秒，B 在队列里一直自旋问"我能拿锁了吗"，CPU 就白白浪费了。所以 AQS 在判断当前确实拿不到之后，会调用 `LockSupport.park()` 让线程暂停：

```text
B 抢锁失败
→ 进入 AQS 队列
→ 判断当前暂时不能获得
→ park()
→ WAITING
→ 不再持续占 CPU 空转
```

资源释放时，比如 `lock.unlock()` 让 state 从 1 变成 0，AQS 会唤醒合适的后继线程，底层是 `LockSupport.unpark(thread)`：

```text
A unlock()
→ state → 0
→ AQS 处理等待队列
→ unpark(B)
→ B 从 park 返回
→ 再次尝试获取同步状态
```

这里容易搞混：**unpark 不等于把锁直接交给 B，它的作用只是让 B 醒来继续尝试竞争。**

---

## 6. AQS 的完整流程

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
持锁线程 unlock()               │
        ↓                      │
     释放资源                   │
        ↓                      │
     state改变                  │
        ↓                      │
  唤醒合适的后继 ─────────────——─┘
        ↓
      unpark
        ↓
   被唤醒线程再次尝试
```

这就是 AQS 最核心的思想。

---

## 7. 为什么叫"抽象"队列同步器

AQS 自己并不知道"怎样才算真正获得资源"，具体规则交给子类实现。独占模式通常是 `tryAcquire()` / `tryRelease()`，共享模式通常是 `tryAcquireShared()` / `tryReleaseShared()`。

分工就是：**AQS 负责 state、CAS、排队、阻塞、唤醒这些通用逻辑；子类只负责回答"什么情况下算获取成功、什么情况下算释放成功"。** 这是典型的模板方法设计。

---

## 8. 两种模式：独占和共享 ⭐⭐⭐⭐

**独占模式**：同一时刻主要由一个线程独占同步状态，典型是 ReentrantLock。

```text
          🔒
           ↑
        Thread A

Thread B → 等
Thread C → 等
```

**共享模式**：允许多个线程同时获得共享资源。比如 `new Semaphore(3)` 相当于 3 个许可证：

```text
许可证 = 3

线程A → 拿一个 ✅
线程B → 拿一个 ✅
线程C → 拿一个 ✅
线程D → 没了 → 等待
```

对应关系：**独占模式 → ReentrantLock；共享模式 → Semaphore、CountDownLatch（利用共享获取/释放语义）。**

---

## 9. 用 ReentrantLock 把 AQS 串一遍

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

线程 A 第一次 `lock()`：state 从 0 改成 1，A 获得锁。A 再 `lock()` 一次，发现持锁者就是自己，state 从 1 加到 2，这就是可重入。B 这时 `lock()` 会获取失败，进入 AQS 队列并 park。

A 第一次 `unlock()`，state 从 2 减到 1，还没有真正释放；第二次 `unlock()`，state 从 1 减到 0，才真正释放，然后 AQS 唤醒后继线程，unpark。

另外别把两者混为一谈：**AQS 不是 Java 实现的 Monitor。** synchronized 走的是 JVM Monitor 机制（monitorenter/monitorexit、wait/notify），ReentrantLock 走的是 AQS（state + CAS + 等待队列 + LockSupport），两者只是都在解决多线程同步、竞争、等待、唤醒这类问题。

---

## Q：介绍一下 AQS

AQS 全称 AbstractQueuedSynchronizer，是 JUC 中用于构建锁和同步器的基础框架，例如 ReentrantLock、Semaphore、CountDownLatch 等都基于或利用 AQS 的同步机制。

AQS 的核心是一个 `state` 同步状态和一个 CLH 风格的等待队列。线程会通过 CAS 等方式尝试修改 state 来获取同步资源，如果获取失败，则会被组织到等待队列中，并在合适的时候通过 `LockSupport.park()` 挂起，避免一直占用 CPU。

当持有同步资源的线程释放资源后，AQS 会根据队列状态唤醒合适的后继线程，底层会使用 `LockSupport.unpark()`，被唤醒的线程再重新尝试获取同步状态。

AQS 同时支持独占模式和共享模式，例如 ReentrantLock 主要使用独占模式，而 Semaphore、CountDownLatch 等会利用共享模式。


已 xhs
