
它和 `synchronized` 最大的底层区别可以先粗略理解为：
`synchronized` 主要是 JVM 提供的 Monitor 同步机制；`ReentrantLock` 是 Java/JUC 层面的锁，核心依赖 **AQS**。

[[#Q：ReentrantLock 底层原理]]

---

# **1. ReentrantLock 最基本的使用**

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();

try {
    count++;
} finally {
    lock.unlock();
}
```

整个过程：

```text
线程A
 ↓
lock.lock()
 ↓
尝试获得锁
 ↓
成功
 ↓
执行临界区
 ↓
unlock()
 ↓
释放锁
```

如果线程 B 同时：

```java
lock.lock();
```

但是 A 已经拿着锁：

```text
A：持有锁 🔒

B：获取失败
      ↓
进入 AQS 等待队列
      ↓
必要时 park 挂起
      ↓
等待被唤醒
```

这背后最重要的就是 **AQS**。

---

# **2. 什么是 AQS？⭐⭐⭐⭐⭐**

AQS：

**AbstractQueuedSynchronizer，抽象队列同步器。**

很多 JUC 并发工具都建立在它之上。

现在可以把它理解成：

**AQS 帮 ReentrantLock 管理“锁现在被谁占着”和“没抢到锁的线程怎么排队”。**

核心可以先记两个东西：

```text
                 AQS
                  │
         ┌────────┴────────┐
         ↓                 ↓
       state            等待队列
         │                 │
    表示同步状态       管理抢锁失败的线程
```

对于 `ReentrantLock`：

```text
state = 0
→ 当前没有线程持有锁

state > 0
→ 锁已经被某线程持有
```

---

# **3. 第一个核心：state**

AQS 内部维护同步状态 `state`。

对于 ReentrantLock，可以简单理解：

```text
state = 0

🔓 没人持有锁
```

线程 A：

```java
lock.lock();
```

尝试把：

```text
state

0 → 1
```

如果成功：

```text
state = 1

Owner = Thread A
```

A 获得锁。

所以：

```text
AQS

state = 1
owner = Thread A
```

表示：

A 当前持有这把 ReentrantLock。

---

# **4. 怎么保证 0 → 1 不被两个线程同时成功？**

这就用到了之前学过的：

**CAS**

例如 A 和 B 同时：

```text
state = 0
```

A：

```text
我希望：
state还是0
↓
如果是
↓
原子地改成1
```

B 同时也这么做。

CAS 保证只有一个能成功：

```text
             state = 0
                │
        ┌───────┴───────┐
        ↓               ↓
     Thread A         Thread B
     CAS 0→1          CAS 0→1
        ↓               ↓
       成功             失败
        ↓               ↓
      获得锁          没抢到
```

所以之前学：

CAS = 乐观锁思想。

这里就真正用上了。

---

# **5. B CAS 失败之后怎么办？**

这才是 AQS 最重要的地方。

假设：

```text
A拿到了锁
↓
state = 1
```

B：

```text
CAS失败
↓
发现锁被别人拿着
```

AQS 不会简单让 B 一直疯狂：

```text
while (true) {
    CAS...
}
```

否则会浪费 CPU。

而是会把抢锁失败的线程组织到一个 **CLH 风格的双向等待队列**中。

简化：

```text
A正在持有锁 🔒


AQS等待队列：

Head
 ↓
Node(B) ⇄ Node(C) ⇄ Node(D)
```

每个等待节点可以关联相应的线程。

可以理解成：

**没抢到锁？先排队。**

---

# **6. 排队以后线程还一直占 CPU 吗？**

不会一直傻等。

AQS 在适当条件下会使用：

```java
LockSupport.park()
```

把线程挂起。

例如 B：

```text
B没抢到锁
   ↓
进入AQS队列
   ↓
再次判断是否有机会获取
   ↓
暂时还是不行
   ↓
LockSupport.park()
   ↓
B暂停执行
```

学线程状态时提到：

```java
LockSupport.park();
```

通常就会让线程进入：

**WAITING**

所以前面的知识又接上了：

```text
ReentrantLock
     ↓
AQS
     ↓
抢锁失败
     ↓
进入等待队列
     ↓
LockSupport.park()
     ↓
WAITING
```

这里就证明了我们上一问说的：

**WAITING 不一定是** `wait()`  **导致的。**

ReentrantLock/AQS 就大量使用 `park/unpark` 机制。

---

# **7. A unlock 之后发生什么？**

线程 A：

```java
lock.unlock();
```

底层开始释放锁。

简化：

```text
state = 1
   ↓
state = 0
   ↓
锁释放
```

然后 AQS 会唤醒合适的后继等待线程：

```java
LockSupport.unpark(thread);
```

例如唤醒 B：

```text
A unlock()
    ↓
state → 0
    ↓
unpark(B)
    ↓
B从 park 中返回
    ↓
再次尝试获取锁
```

注意！

**unpark(B) ≠ 直接把锁送给 B。**

它更接近：

“B，醒醒，可以再次尝试获取锁了。”

所以：

```text
A释放锁
   ↓
唤醒B
   ↓
B重新尝试获取
   ↓
成功
   ↓
成为新的锁持有者
```

这一点和前面学 `notify()` 很像：

**唤醒 ≠ 直接获得锁。**

---

# **8. 为什么 ReentrantLock 是“可重入”的？⭐⭐⭐⭐⭐**

这是名字：

```text
Reentrant
=
可重入
```

的来源。

假设 A 已经拿到了锁：

```text
state = 1
owner = A
```

A 又执行：

```java
lock.lock();
```

这时候发现：

```text
锁已经有人持有
       ↓
持有者是谁？
       ↓
就是当前线程 A
```

所以允许重入。

于是：

```text
state：

1 → 2
```

A 再获取：

```text
2 → 3
```

因此这里的 `state` 不仅表示“有没有锁”，还可以表示：

**当前线程重入了多少次。**

例如：

```text
Thread A

lock.lock()
↓
state = 1

    lock.lock()
    ↓
    state = 2

        lock.lock()
        ↓
        state = 3
```

释放：

```text
unlock()
↓
3 → 2

unlock()
↓
2 → 1

unlock()
↓
1 → 0
```

只有：

```text
state = 0
```

才算：

**真正完全释放锁。**

这和刚才学的 synchronized 可重入非常类似。

---

# **9. 所以 lock() 的完整过程是什么？⭐⭐⭐⭐⭐**

把整个过程串起来：

```text
             Thread A
                 │
              lock()
                 ↓
        尝试 CAS 修改 state
                 │
          ┌──────┴──────┐
          ↓             ↓
        成功            失败
          ↓             ↓
       获得锁      是不是自己持有？
                        │
                 ┌──────┴──────┐
                 ↓             ↓
                是             否
                 ↓             ↓
            state++        AQS排队
                              ↓
                         Node加入队列
                              ↓
                     LockSupport.park()
                              ↓
                           WAITING
                              ↓
                     前驱释放锁后被唤醒
                              ↓
                         再次尝试获取
```

这张图基本就是 ReentrantLock 原理的核心。

---

# **10. unlock() 的流程**

再看释放：

```java
lock.unlock();
```

简化：

```text
当前线程 unlock()
        ↓
    state - 1
        ↓
┌───────┴────────┐
↓                ↓
state > 0       state = 0
↓                ↓
还有重入层数     完全释放
↓                ↓
暂时不释放      owner清空
                 ↓
           唤醒后继等待线程
                 ↓
       LockSupport.unpark()
```

所以为什么一定：

```java
try {
    ...
} finally {
    lock.unlock();
}
```

就是为了确保异常情况下也能把 `state` 正确减回去并最终释放锁。


### Q：ReentrantLock 底层原理

`ReentrantLock` 是 JUC 提供的可重入互斥锁，底层主要基于 AQS 实现。AQS 内部通过 `state` 维护同步状态，并通过 CAS 保证状态修改的原子性，同时使用 CLH 风格的等待队列管理获取锁失败的线程。

当线程调用 `lock()` 时，会尝试获取同步状态。如果锁空闲，则通过 CAS 等方式获得锁并记录当前持有线程；如果锁已经被其他线程持有，则线程会进入 AQS 等待队列，并可能通过 `LockSupport.park()` 挂起。

持锁线程调用 `unlock()` 后会减少 state，当 state 减到 0 时才真正释放锁，并唤醒合适的后继等待线程，使其重新尝试获取锁。

ReentrantLock 支持可重入，如果当前线程已经持有锁后再次获取同一把锁，会增加 state 的重入计数；每次 unlock 对应减少一次，直到 state 为 0 才完全释放。此外它还支持公平锁、tryLock、可中断获取锁以及 Condition 等高级功能。
 