
[[#Q：sleep 和 wait 的区别]]

会。 `sleep()` 会让当前线程暂时放弃 CPU 执行机会，但不会释放已经持有的锁；`wait()` 不仅会让线程等待，还会释放对应对象的 monitor 锁。

这是两者最核心的区别。

| **对比**   | `sleep()`         | `wait()`                                    |
| -------- | ----------------- | ------------------------------------------- |
| 所属类      | `Thread`          | `Object`                                    |
| 是否释放 CPU | ✅ 会               | ✅ 会                                         |
| 是否释放锁    | ❌ **不会**          | ✅ **会释放对应对象锁**                              |
| 使用位置     | 任意合适位置            | 必须持有对应对象的 monitor                           |
| 如何恢复     | 时间到 / 被 interrupt | `notify()` / `notifyAll()` / 超时 / interrupt |
| 主要用途     | 暂停线程一段时间          | 线程间通信、条件等待                                  |

### **1. sleep 会释放 CPU 吗？**

会。

比如：

```java
synchronized (lock) {

    System.out.println("A");

    Thread.sleep(5000);

    System.out.println("B");
}
```

线程执行到 `sleep(5000)`：

```text
线程A获得 lock
      ↓
打印 A
      ↓
sleep(5秒)
      ↓
暂时不占用 CPU 执行
      ↓
但仍然持有 lock 🔒
```

这时候其他线程可以获得 CPU 执行，但是如果它也想：

```java
synchronized (lock) {
    ...
}
```

就进不去：

```text
线程A：sleep
       但还拿着 🔒 lock

线程B：想获取 lock
       ↓
       等待……
```

所以一定区分：

**释放 CPU ≠ 释放锁。**

`sleep()`：**CPU 让了，锁没让。**

---

### **2. wait() 就不一样**

例如：

```java
synchronized (lock) {

    System.out.println("A");

    lock.wait();

    System.out.println("B");
}
```

执行到：

```java
lock.wait();
```

之后：

```text
线程A
 ↓
持有 lock 🔒
 ↓
调用 lock.wait()
 ↓
释放 lock 🔓
 ↓
进入等待状态
```

于是其他线程就可以：

```java
synchronized (lock) {
    // 获得 lock
}
```

然后另一个线程可以：

```java
lock.notify();
```

唤醒等待该对象 monitor 的线程。

但注意：

被  `notify()` 唤醒 ≠ 马上执行。

它还需要重新竞争 `lock`：

```text
线程A wait()
   ↓
释放 lock
   ↓
等待
   ↓
其他线程 notify()
   ↓
A 被唤醒
   ↓
重新竞争 lock 🔒
   ↓
拿到锁
   ↓
从 wait() 后面继续执行
```

### **3. 为什么 wait 必须释放锁？**

这很好理解。

假设线程 A：

```text
拿到锁
 ↓
发现条件不满足
 ↓
wait()
```

如果 `wait()` **不释放锁**：

```text
A拿着锁等待条件改变
        ↓
B需要这把锁才能修改条件
        ↓
B拿不到锁
        ↓
A永远等不到条件变化
```

所以 `wait()` 必须：

**等待的同时释放 monitor，让其他线程有机会进入同步区域、改变条件。**

---

### Q：sleep 和 wait 的区别

`sleep()` 是 Thread 类的静态方法，主要用于让当前线程暂停执行一段时间。它会让当前线程暂时不参与 CPU 执行，但**不会释放已经持有的锁**。

`wait()` 是 Object 类的方法，主要用于线程间通信和条件等待，调用时线程必须持有对应对象的 monitor。调用 `wait()` 后会**释放该对象的 monitor 锁**并进入等待状态，之后可以通过 `notify()` 或 `notifyAll()` 等方式唤醒，但唤醒后还需要重新竞争锁。


**sleep：让 CPU，不让锁。**  
**wait：让 CPU，也让对应的锁；被唤醒后还要重新抢锁。**