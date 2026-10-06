JMM（Java Memory Model，Java 内存模型）是 Java 并发里非常核心的概念。可以先用一句话理解：

**JMM 是 Java 定义的一套多线程内存访问规则，它规定了一个线程对共享变量的修改，什么时候、以什么方式能够被其他线程看到。**

它主要解决多线程中的三个问题：

**原子性、可见性、有序性。**

### **1. 为什么需要 JMM？**

假设有两个线程共享变量：

```java
int count = 0;
```

你可能以为两个线程都直接操作内存里的这个 `count`：

```text
线程A ──→ count ←── 线程B
```

为了理解 JMM，可以先用一个**简化模型**：

```text
              主内存
          count = 0
          /       \
         ↓         ↓
   线程A工作内存   线程B工作内存
     count=0        count=0
        ↓              ↓
      CPU执行         CPU执行
```

每个线程可能使用共享变量值的本地副本/缓存状态。

例如线程 A：

```java
count = 10;
```

线程 A 修改之后：

```text
主内存：       count = 0
                  ↑
                  │ 还没有及时可见
                  │
线程A观察：    count = 10

线程B观察：    count = 0
```

于是线程 B 可能暂时看不到 A 的修改。

这就是：

**可见性问题。**

注意，这张图是帮助理解的**抽象模型**，不要把“工作内存”简单等同于 CPU 缓存。实际 JVM、CPU、寄存器、缓存和编译器优化会复杂得多。

---

## **2. JMM 主要解决三个问题**

### **① 原子性 Atomicity**

所谓原子性：

**一个操作要么完整执行，要么不执行，不能被其他线程看到“执行一半”的状态。**

例如：

```java
count++;
```

看起来只有一句，实际上可以粗略理解：

```text
读取 count
    ↓
count + 1
    ↓
写回 count
```

两个线程同时执行：

```text
初始 count = 0

线程A              线程B
读取 0             读取 0
  ↓                  ↓
+1                  +1
  ↓                  ↓
写入 1             写入 1

最终：
count = 1
```

但我们本来希望：

```text
count = 2
```

所以：

`count++` **不是原子操作**。

可以通过：

```java
synchronized
```

或者：

```java
AtomicInteger
```

等方式解决。

---

### **② 可见性 Visibility ⭐⭐⭐⭐⭐**

一个线程修改共享变量后：

**其他线程能不能及时看到这个修改？**

例如：

```java
boolean flag = false;
```

线程 A：

```java
flag = true;
```

线程 B：

```java
while (!flag) {
    // ...
}
```

如果没有正确的同步机制，不能简单假定线程 B 一定按你期望的方式立即观察到 `true`。

可以使用：

```java
volatile boolean flag;
```

建立相应的可见性保证。

所以你刚才学 ConcurrentHashMap 时看到的：

```java
volatile
```

其实就和 JMM 密切相关。

---

### **③ 有序性 Ordering ⭐⭐⭐⭐⭐**

你写的代码：

```java
a = 1;
b = 2;
c = 3;
```

并不意味着底层在所有情况下都必须严格按照你看到的源码顺序执行。

编译器、JIT、CPU 在**不影响单线程语义**的前提下，可能进行：

**指令重排序。**

单线程：

```text
重排序
↓
结果没变化
↓
通常没问题
```

但是多线程情况下：

```text
线程A正在修改

线程B正在观察

↓
```

如果缺少正确的同步关系，重排序可能造成线程 B 观察到意料之外的状态。

因此 JMM 还需要规定：

**哪些操作之间不能随意重排序，以及一个线程中的操作何时必须对另一个线程可见。**

---

## **3. volatile 和 JMM 什么关系？**

这是最容易被连着问的。

```java
volatile boolean flag = false;
```

`volatile` 主要提供：

**可见性 + 一定的有序性保证**

例如：

```text
线程A：
flag = true
      ↓
其他线程能够按照 JMM 对 volatile 的规则观察到修改


同时：
volatile 读写具有特定的内存语义
      ↓
限制相关指令重排序
```

但：

**volatile 不保证复合操作的原子性。**

所以：

```java
volatile int count = 0;

count++;
```

仍然不是线程安全的。

一定记：

```text
volatile

可见性     ✅
有序性     ✅（提供相应保证）
count++原子性 ❌
```

---

## **4. synchronized 和 JMM**

`synchronized` 就更全面一些。

```java
synchronized (lock) {
    count++;
}
```

可以帮助提供：

```text
原子性  ✅
可见性  ✅
有序性  ✅
```

你可以简单理解：

```text
进入 synchronized
        ↓
获得锁
        ↓
执行临界区
        ↓
释放锁
        ↓
后续获得同一把锁的线程
能够看到之前线程的相关修改
```

这背后就涉及 JMM 非常重要的：

**happens-before 原则。**

---

# **5. Happens-Before ⭐⭐⭐⭐⭐**

这是 JMM 最重要的八股之一。

它可以简单理解为：

如果操作 A happens-before 操作 B，那么 A 的执行结果对 B 可见，并且 A 在相应的内存顺序上先于 B。

例如：

### **synchronized**

```text
线程A：
修改数据
 ↓
unlock(lock)

     happens-before

线程B：
lock(lock)
 ↓
读取数据
```

**对同一把锁**，前一次 unlock happens-before 后续的 lock。

因此线程 A 在释放锁之前的相关修改，可以对随后获得同一把锁的线程 B 可见。

---

### **volatile**

```text
线程A：

普通变量修改
    ↓
volatile变量写

    happens-before

线程B：

volatile变量读
    ↓
后续操作
```

对同一个 volatile 变量：

**一次 volatile 写 happens-before 后续对该变量的 volatile 读。**

这也是 volatile 实现线程间通信的重要基础。

---

### **Thread.start()**

```java
int a = 10;

thread.start();
```

`start()` 之前的操作 happens-before 新线程开始执行后的相应操作。

---

### **Thread.join()**

线程 A：

```java
thread.start();
thread.join();
```

`thread` 中执行完成的操作 happens-before `join()` 成功返回之后线程 A 的后续操作。

---

# **6. JMM 和 JVM 内存区域不要搞混 ⭐⭐⭐⭐⭐**

这是面试特别容易混淆的。

你后面学 JVM 会学：

```text
JVM 运行时数据区域

├── 堆
├── 方法区 / 元空间
├── Java虚拟机栈
├── 程序计数器
└── 本地方法栈
```

这个回答的是：

**Java 程序运行时，数据存在哪里？**

而：

```text
JMM
├── 原子性
├── 可见性
├── 有序性
└── happens-before
```

回答的是：

**多线程之间如何正确地访问、观察共享数据？**

所以：

**JMM ≠ JVM 内存区域。**

这两个一定不要混。

---

## 和最近学的并发知识串起来

```text
ArrayList线程不安全
HashMap线程不安全
CopyOnWriteArrayList
ConcurrentHashMap
volatile
CAS
synchronized
```

现在其实可以统一到：

```text
                  JMM
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
     原子性       可见性       有序性
       │           │           │
 synchronized    volatile    volatile
 Atomic类        锁机制      synchronized
 CAS             ...         ...
       │
       ↓
   并发工具实现
       │
 ┌─────┴──────────────┐
 ↓                    ↓
CopyOnWriteArrayList  ConcurrentHashMap
```

所以 JMM 是底层的**规范和规则体系**，而 `volatile`、`synchronized`、CAS、各种并发集合是在这些规则基础上实现线程安全的具体手段。

### Q：什么是 Java 内存模型 JMM？

JMM，也就是 Java Memory Model，是 Java 定义的一套多线程内存访问规范，用来规定线程之间如何访问和共享变量，以及一个线程对共享变量的修改什么时候能够被其他线程看到。JMM 主要关注三个问题：原子性、可见性和有序性，同时通过 happens-before 规则定义线程之间的内存可见性和顺序关系。像 volatile、synchronized 等并发机制的内存语义都建立在 JMM 之上。