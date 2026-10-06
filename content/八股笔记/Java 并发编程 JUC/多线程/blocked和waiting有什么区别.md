
[[#Q：blocked 和 waiting 的区别是什么]]

和操作系统里面很像，blocked 可以理解所需要的资源都到位了，但是在等待一个锁；而 waiting 是不光在等待锁，甚至运行所需要的资源都还没到位所以阻塞等待，等待通知以后才能竞争锁
java 线程中 blocked 和 os 的 ready 很像，而 waiting 和 os 的 blocked 很像

### **举个最直观的例子**

假设线程 A 已经拿到了 `lock`：

```java
synchronized (lock) {
    // 线程A正在执行
}
```

线程 B 也执行：

```java
synchronized (lock) {
    // ...
}
```

但锁在 A 手里：

```text
        lock 🔒
          ↑
       线程A拿着

线程B → 想拿lock → 拿不到
                    ↓
                 BLOCKED
```

所以：

**BLOCKED = 等 synchronized 的 monitor 锁。**

等 A 释放锁后，B 才有机会竞争锁。

---

而 `WAITING` 是另一回事。

线程 A：

```java
synchronized (lock) {
    lock.wait();
}
```

执行 `wait()` 后：

```text
线程A拿到 lock
     ↓
发现条件不满足
     ↓
lock.wait()
     ↓
主动释放 lock
     ↓
   WAITING
     ↓
等待别人 notify / notifyAll
```

⚠️：`notify()` 就是：**从这个对象 monitor 的等待集合里唤醒一个正在 `wait()` 的线程。**

另一个线程：

```java
synchronized (lock) {
    lock.notify();
}
```

A 才会被唤醒。

而且这里有一个很关键的状态变化：

```text
线程A
 ↓
WAITING
 ↓
别人 notify()
 ↓
BLOCKED   ← 可能进入这里！
 ↓
重新竞争 lock
 ↓
拿到锁
 ↓
RUNNABLE
```

为什么 `notify()` 后可能变成 `BLOCKED`？

因为：

**notify 只是告诉 A：“你可以醒了”，但 A 想从`wait()` 返回，必须重新拿到 `lock` ****。**

如果锁还在别人手里，它就得等锁，所以进入 `BLOCKED`。

---

### **再和 sleep 放一起看**

你上一问刚好学了 `sleep`：

```java
Thread.sleep(5000);
```

它通常对应的是：

**TIMED_WAITING**

也就是“有时间限制的等待”。

可以把三个状态一起记：

|**状态**|**为什么在等**|**典型情况**|
|---|---|---|
| `BLOCKED` |**等锁**|进入 `synchronized` 时锁被别人占用|
| `WAITING` |**无限期等事件/通知**| `wait()`、`join()` |
| `TIMED_WAITING` |**有时间限制地等**| `sleep(1000)`、`wait(1000)`、`join(1000)` |

最适合你现在记的图就是：

```text
BLOCKED
“锁被别人拿了，我进不去”
        🚪🔒
线程B → | 线程A正在里面


WAITING
“我主动进去等通知”
线程A → wait()
        ↓
      等 notify()


TIMED_WAITING
“我等一会儿”
线程A → sleep(5秒)
        ↓
      5秒后有机会继续
```

### Q：blocked 和 waiting 的区别是什么

BLOCKED 是线程在等待获取  `synchronized` 的 monitor 锁；WAITING 是线程已经主动进入无限期等待状态，需要其他线程执行特定操作才能继续，例如 `wait()` 等待`notify()` ，或者 `join()` 等待目标线程结束。