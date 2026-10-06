个人理解：
synchronized是可重入锁，能够让线程获取一把锁，别的线程就无法进入同一把锁保护的临界区；其中这是通过 monitor 来实现的，获取和释放会牵扯到 moniterenter 和 moniterexit 字节码

根据多线程牵扯到的很多八股可以从操作系统原理的视角去理解，比硬啃好受点

[[#Q：说说 synchronized 的底层原理]]

---
# **1. synchronized 到底锁的是什么？**

比如：

```java
Object lock = new Object();

synchronized (lock) {
    count++;
}
```

这里不是“把 `count` 锁住”，而是：

线程必须先获得 lock 对象对应的 monitor，才能进入这段代码。

可以理解：

```text
                     lock 对象
                        │
                        ↓
                    Monitor 🔒
                        │
            ┌───────────┴───────────┐
            ↓                       ↓
         Thread A                 Thread B
         获得锁                   想获得锁
            ↓                       ↓
       count++                  获取失败
                                  ↓
                               BLOCKED
```

所以真正实现线程安全的前提是：

**所有访问共享数据的线程，都遵守同一把锁。**

```java
synchronized (lock) {
    count++;
}
```

如果另一个线程直接：

```java
count++;
```

那 synchronized 管不了它。

---

# **2. synchronized 和 Monitor 是什么关系？**

可以先建立这个模型：

```text
Java对象 lock
     │
     ├── 对象头 Mark Word
     │       ↑
     │    锁相关信息
     │
     └── 与 Monitor 机制关联
              │
              ↓
          Monitor
         ┌─────────┐
         │ Owner   │ → 当前持有锁的线程
         │ EntrySet│ → 等待获取锁的线程
         │ WaitSet │ → 调用 wait() 等待的线程
         └─────────┘
```

可以把 Monitor 想象成一个“门卫 + 等待区域”。

---

# **3. Monitor 里面有什么？**

概念上重点理解三个东西：

```text
Monitor

Owner
  │
  └── 谁现在持有这把锁？

EntrySet
  │
  └── 谁正在竞争这把锁？

WaitSet
  │
  └── 谁调用了 wait()，正在等通知？
```

例如现在：

```text
Owner     → Thread A

EntrySet  → Thread B
            Thread C

WaitSet   → Thread D
            Thread E
```

```text
A：我已经拿到锁，在 synchronized 里面执行

B/C：我也想进去，但是锁被 A 拿了
     → BLOCKED

D/E：之前进去过，但是调用了 wait()
     → WAITING
```

把前面学的：`BLOCKED`、`WAITING`、`wait()`、`notify()` 全部串起来了。

---

# **4. synchronized 是怎么获得锁的？**

代码：

```java
synchronized (lock) {
    count++;
}
```

编译成字节码后，同步代码块会涉及：

```text
monitorenter

    count++

monitorexit
```

你可以先粗略理解成：

```text
monitorenter
    ↓
“我要获得 lock 对应的 monitor”


monitorexit
    ↓
“我要释放这个 monitor”
```

于是线程 A 执行：

```text
Thread A
   ↓
monitorenter
   ↓
检查 monitor
   ↓
没人持有
   ↓
A 成为 Owner
   ↓
获得锁
   ↓
执行 synchronized
```

---

# **5. 如果另一个线程来了呢？**

假设 A 还没有执行完：

```text
Monitor

Owner → Thread A
```

此时 B：

```text
Thread B
   ↓
monitorenter
   ↓
发现：
Owner = Thread A
   ↓
“别人拿着锁”
   ↓
竞争失败
   ↓
BLOCKED
```

于是：

```text
                 Monitor 🔒
                    │
          Owner = Thread A
                    │
             执行 count++
                    │
                    │
Thread B ─────→ 等待获取锁
                    │
                 BLOCKED
```

等 A：

```text
monitorexit
```

释放锁以后，B 等竞争者才有机会获取锁。

注意：

**不是 A 释放锁以后一定轮到最早 BLOCKED 的线程。**

`synchronized` 不提供公平锁保证。

---

# **6. monitorexit 怎么释放锁？**

线程 A：

```text
执行完 synchronized
        ↓
    monitorexit
        ↓
释放 monitor
        ↓
其他竞争线程有机会获取
```

例如：

```text
原来：

Owner → A
等待 → B、C


A monitorexit
       ↓

Owner → 空闲

       ↓

B、C 竞争

       ↓

假设 C 抢到了

       ↓

Owner → C
B继续等待
```

所以 synchronized 最基本的互斥原理就是：

**通过 Monitor 控制同一时刻哪个线程能够进入临界区。**

---

# **7. 那“可重入”是怎么回事？⭐⭐⭐⭐⭐**

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
        System.out.println("hello");
    }

}
```

线程 A：

```text
第一次 synchronized(lock)

A → monitorenter
     ↓
获得 lock
```

然后 A 调用 `method()`，再次遇到：

```java
synchronized (lock)
```

这时候 JVM 发现：

```text
当前锁的 Owner
      =
   Thread A

现在申请锁的线程
      =
   Thread A
```

是自己。

所以：

**允许再次获得，而不是把自己 BLOCKED。**

概念上可以理解成有一个重入计数：

```text
A 第一次获得
↓
重入次数 = 1

A 第二次获得
↓
重入次数 = 2

A 第三次获得
↓
重入次数 = 3
```

释放：

```text
monitorexit
↓
3 → 2

monitorexit
↓
2 → 1

monitorexit
↓
1 → 0
↓
真正完全释放
```

所以：

**可重入 = 同一个线程已经持有某把锁之后，可以再次获得同一把锁。**

---

# **8. 为什么一定要可重入？**

否则非常容易自己把自己锁死。

比如：

```java
public synchronized void methodA() {
    methodB();
}

public synchronized void methodB() {
    // ...
}
```

如果两个方法锁的是同一个对象 `this`：

```text
线程A
 ↓
进入 methodA
 ↓
拿到 this 锁
 ↓
调用 methodB
 ↓
methodB 又需要 this 锁
```

如果不可重入：

```text
A拿着锁
 ↓
A等待自己释放锁
 ↓
但A必须进入methodB后才能继续
 ↓
永远等待
```

自己把自己死锁了。

所以 synchronized 支持可重入。
**

---

# **10. synchronized 修饰不同地方，锁谁？**

这个也是面试高频。

### **普通代码块**

```java
synchronized (lock) {
}
```

锁：

`lock` 对象。

---

### **普通实例方法**

```java
public synchronized void test() {
}
```

相当于理解成：

```java
synchronized (this) {
}
```

锁：

**当前实例对象** `this` ****。**

---

### **static synchronized**

```java
public static synchronized void test() {
}
```

锁的是：

**这个类对应的**  `Class`  **对象。**

例如：

```java
User.class
```

可以理解：

```java
synchronized (User.class) {
}
```

所以：

```text
synchronized 实例方法
        ↓
      this锁


static synchronized 方法
        ↓
     Class对象锁
```

它们不是同一把锁。

---

# **11. synchronized 不只是“互斥”**

这一点和你刚学的 JMM 联系起来。

`synchronized` 不只是：

同一时间只让一个线程进来。

它还提供了**内存可见性和有序性保证**。

比如：

```java
synchronized (lock) {
    count = 100;
}
```

线程 A 释放 `lock`。

线程 B 后续：

```java
synchronized (lock) {
    System.out.println(count);
}
```

根据 JMM 的 happens-before 规则：

**对同一个 monitor 的 unlock happens-before 后续对这个 monitor 的 lock。**

因此前一个线程释放锁之前的相关修改，对后续成功获得同一把锁的线程可见。

所以 synchronized 帮我们同时处理：

```text
            synchronized
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
      原子性    可见性    有序性
        │        │        │
       互斥    JMM保证   JMM保证
```

---

# **12. 再把 wait / notify 接进来**

现在 Monitor 这张图就完整了：

```text
                   Monitor
                      │
         ┌────────────┼────────────┐
         ↓            ↓            ↓
       Owner        EntrySet      WaitSet
         │            │            │
      持有锁       等待锁        等通知
         │            │            │
     Thread A      Thread B      Thread C
                       │            │
                    BLOCKED       WAITING
```

Thread A：

```java
synchronized (lock) {
    lock.wait();
}
```

发生：

```text
A原来是 Owner
    ↓
wait()
    ↓
释放 monitor
    ↓
进入 WaitSet
    ↓
WAITING
```

Thread B：

```java
synchronized (lock) {
    lock.notify();
}
```

相当于：

```text
WaitSet 中某个线程
        ↓
被 notify
        ↓
从“等通知”
变成“准备重新竞争锁”
        ↓
最终还需要重新获得 monitor
```

所以你之前的知识现在全串起来了。

# **14. 现在可以这样理解整个 synchronized**

把所有内容压缩成一张图：

```text
Java代码

synchronized (lock) {
    count++;
}

        ↓ 编译

同步代码块字节码

monitorenter
     ↓
  count++
     ↓
monitorexit

        ↓ JVM

lock对象
   ↓
对象头中的锁相关信息
   +
Monitor同步机制

        ↓

┌──────────────────────────────┐
│           Monitor            │
│                              │
│ Owner    → 当前持锁线程       │
│ EntrySet → 竞争锁的线程       │
│ WaitSet  → wait等待的线程     │
└──────────────────────────────┘

        ↓

同一时刻
只有获得锁的线程
可以进入受同一把锁保护的临界区

        ↓

实现：
互斥 + 可见性 + 有序性保证

同时：
支持可重入
```

### Q：说说 synchronized 的底层原理

`synchronized` 是 Java 提供的可重入互斥同步机制。线程进入 synchronized 保护的临界区之前，需要先获得对应对象的锁，其他使用同一把锁的线程无法同时进入该临界区。

它的实现与 JVM 的 Monitor 机制有关。对于 synchronized 代码块，字节码层面会使用 `monitorenter` 和 `monitorexit` 来表示 monitor 的获取和释放；对于 synchronized 方法，则通过 `ACC_SYNCHRONIZED` 标志让 JVM 在调用方法时进行同步。

当一个线程持有锁时，其他竞争同一 monitor 的线程可能进入 BLOCKED 状态；持锁线程退出同步区域后释放锁，其他线程再参与竞争。synchronized 还是可重入锁，同一个线程已经获得锁之后可以再次进入由同一把锁保护的同步代码。

此外，根据 JMM 的 happens-before 规则，对同一个 monitor 的解锁 happens-before 后续的加锁，因此 synchronized 不仅提供互斥，还提供相应的可见性和有序性保证。