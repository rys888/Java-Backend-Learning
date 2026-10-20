
## **一、什么是 JUC？**

**JUC（Java Util Concurrent）是 Java 提供的并发编程工具包，主要位于**  **`java.util.concurrent` 及其子包中。**

它从 JDK 1.5 开始引入，主要用于解决多线程开发中的三个问题：

- **线程安全：** 多个线程同时操作共享数据时，如何保证数据正确性。
- **线程协作：** 多个线程之间如何协调执行顺序。
- **并发性能：** 如何减少锁竞争，提高多线程执行效率。

例如，假设 100 个线程同时执行：

```java
count++;
```

由于 `count++` 不是原子操作，最终结果可能小于 100。

JUC 提供了 `AtomicInteger`：

```java
AtomicInteger count = new AtomicInteger(0);

count.incrementAndGet();
```

通过原子操作，可以保证多个线程并发递增时不会丢失更新。

---

## **二、JUC 包含哪些主要组件？**

JUC 主要可以分为 **6 大类**。

|**分类**|**主要组件**|**核心作用**|
|---|---|---|
|1. 锁机制|ReentrantLock、ReentrantReadWriteLock、StampedLock|控制共享资源的并发访问|
|2. 原子类|AtomicInteger、AtomicReference、LongAdder|实现线程安全的原子操作|
|3. 并发集合|ConcurrentHashMap、CopyOnWriteArrayList、BlockingQueue|提供线程安全的数据结构|
|4. 线程池|ThreadPoolExecutor、Executors、ScheduledThreadPoolExecutor|管理和复用线程|
|5. 同步工具|CountDownLatch、CyclicBarrier、Semaphore、Phaser|实现线程之间的协调|
|6. 异步编程|Future、CompletableFuture、FutureTask|获取异步任务执行结果|

下面分别介绍。

### **1. 锁机制（Lock）**

JUC 提供了比 `synchronized` 更灵活的锁机制。

最常见的是 `ReentrantLock`。

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();

try {
    // 操作共享资源
    count++;
} finally {
    lock.unlock();
}
```

它具有以下特点：

- **可重入：** 同一个线程可以重复获取同一把锁。
- **可中断：** 可以通过 `lockInterruptibly()` 响应中断。
- **支持超时：** 可以通过 `tryLock()` 尝试获取锁。
- **支持公平锁：** 可以指定公平或非公平策略。

另外还有 `ReentrantReadWriteLock`，允许多个线程同时读，但写操作需要独占访问。

**面试重点：**** `synchronized`  **和**  `ReentrantLock`  **的区别。**

### 2. 原子类（Atomic）

原子类位于：

```java
java.util.concurrent.atomic
```

常见组件：

|**原子类**|**作用**|
|---|---|
|AtomicInteger|原子更新整数|
|AtomicLong|原子更新长整数|
|AtomicBoolean|原子更新布尔值|
|AtomicReference|原子更新对象引用|
|LongAdder|适合高并发计数|

例如：

```java
AtomicInteger count = new AtomicInteger(0);

count.incrementAndGet();
```

其核心实现通常依赖 **CAS（Compare And Swap，比较并交换）**。

CAS 的基本思想是：

**只有当变量当前值等于预期值时，才执行更新，否则重新尝试或返回失败。**

因此，可以在不使用传统互斥锁的情况下，实现某些线程安全操作。

不过 CAS 也存在 ABA 问题等局限。

**面试重点：CAS 原理、ABA 问题、AtomicInteger 和 LongAdder 的区别。**

### 3. 并发集合 

普通集合通常不保证线程安全。

例如：

```java
Map<String, Integer> map = new HashMap<>();
```

多个线程同时修改 HashMap，可能出现数据竞争等问题。

JUC 提供了线程安全的并发集合。

|**集合**|**特点**|
|---|---|
|ConcurrentHashMap|支持高并发读写的 Map|
|CopyOnWriteArrayList|写时复制，适合读多写少|
|ConcurrentLinkedQueue|基于非阻塞算法的并发队列|
|ArrayBlockingQueue|基于数组的有界阻塞队列|
|LinkedBlockingQueue|基于链表的阻塞队列|

例如：

```java
Map<String, Integer> map = new ConcurrentHashMap<>();

map.put("Java", 1);
map.put("Redis", 2);
```

ConcurrentHashMap 可以支持多个线程安全地执行单次 `put()`、`get()` 等操作。

但要注意：

```java
map.put("Java", map.get("Java") + 1);
```

这样的复合操作不具备整体原子性。

应该考虑：

```java
map.merge("Java", 1, Integer::sum);
```

**面试重点：HashMap 和 ConcurrentHashMap 的区别、ConcurrentHashMap 如何保证线程安全。**

### **4. 线程池（ThreadPool）**

如果每次执行任务都创建一个新线程：

```java
new Thread(() -> {
    // 执行任务
}).start();
```

频繁创建和销毁线程会产生额外开销。

因此，JUC 提供了线程池：

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2,
    4,
    60,
    TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),
    new ThreadPoolExecutor.AbortPolicy()
);

executor.execute(() -> {
    System.out.println("执行任务");
});

executor.shutdown();
```

线程池主要解决：

- 线程复用，减少创建和销毁开销。
- 控制并发线程数量。
- 使用任务队列管理待执行任务。
- 通过拒绝策略处理超出容量的任务。

**面试重点：ThreadPoolExecutor 的 7 个参数、任务执行流程、4 种拒绝策略。**

### **5. 同步工具类**

同步工具类主要用于协调多个线程的执行。

最常见的是以下三个：

|**工具类**|**作用**|**典型场景**|
|---|---|---|
|CountDownLatch|等待多个任务执行完成|主线程等待多个子任务|
|CyclicBarrier|让多个线程在指定位置相互等待|多线程分阶段执行|
|Semaphore|限制同时访问资源的线程数量|控制并发访问量|

**① CountDownLatch**

假设主线程需要等待三个任务全部执行完成：

```java
CountDownLatch latch = new CountDownLatch(3);

// 每个任务执行完成后
latch.countDown();

// 主线程等待
latch.await();
```

当计数器从 3 减少到 0 时，等待的线程就可以继续执行。

**② CyclicBarrier**

假设三个线程必须全部到达某个位置，才能继续执行：

```java
CyclicBarrier barrier = new CyclicBarrier(3);

barrier.await();
```

三个线程全部调用 `await()` 后，才能通过屏障。

**③ Semaphore**

假设某个资源最多允许 10 个线程同时访问：

```java
Semaphore semaphore = new Semaphore(10);

semaphore.acquire();

try {
    // 访问共享资源
} finally {
    semaphore.release();
}
```

Semaphore 通过许可证数量限制并发访问。

**面试重点：CountDownLatch 和 CyclicBarrier 的区别、Semaphore 的使用场景。**

### **6. 异步编程（Future / CompletableFuture）**

JUC 还提供了异步任务执行和结果获取机制。

例如：

```java
CompletableFuture<String> future =
    CompletableFuture.supplyAsync(() -> {
        return "查询用户信息";
    });

String result = future.join();
```

这里 `supplyAsync()` 会提交异步任务。

调用 `join()` 时，如果任务尚未完成，当前线程会等待结果。

`CompletableFuture` 还支持多个任务的组合、依赖执行和异常处理。

例如：

```java
CompletableFuture.allOf(future1, future2);
```

可以等待多个异步任务全部完成。

实际项目中，可以用于并行查询多个相互独立的数据源，减少串行等待时间。

需要注意，实际开发中通常建议为业务任务指定合适的线程池，而不是无条件使用默认线程池。

---

## 三、JUC 和 AQS 是什么关系？

这是理解 JUC 的一个关键知识点。

**AQS（AbstractQueuedSynchronizer，抽象队列同步器）是 JUC 中许多锁和同步工具的基础框架。**

例如：

```text
                  AQS
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
  ReentrantLock  Semaphore  CountDownLatch
```

AQS 主要通过：

**state 状态变量 + CAS + 等待队列**

来实现线程同步。

例如：

对于 `ReentrantLock`，AQS 的 `state` 可以表示锁的持有状态及重入次数。

对于 `Semaphore`，`state` 可以表示可用许可证数量。

对于 `CountDownLatch`，`state` 可以表示剩余计数。

因此，AQS 可以为不同同步工具提供一套通用的实现基础。

但并不是所有 JUC 组件都基于 AQS，例如 `ConcurrentHashMap` 和 `AtomicInteger` 就不是通过继承 AQS 实现的。

---

## **四、面试怎么回答？**

JUC 是 Java 提供的并发编程工具包，主要位于 `java.util.concurrent` 及其子包中，用于解决多线程环境下的线程安全、线程协作以及并发性能问题。

JUC 主要包含六类组件。

第一类是锁机制，例如 ReentrantLock 和 ReentrantReadWriteLock，用于控制共享资源的并发访问。

第二类是原子类，例如 AtomicInteger、AtomicReference 和 LongAdder，主要通过 CAS 等机制实现原子操作。

第三类是并发集合，例如 ConcurrentHashMap、CopyOnWriteArrayList 和 BlockingQueue，提供线程安全的数据结构。

第四类是线程池，例如 ThreadPoolExecutor，用于线程复用和任务调度。

第五类是同步工具，例如 CountDownLatch、CyclicBarrier 和 Semaphore，用于协调多个线程的执行。

第六类是异步编程工具，例如 Future 和 CompletableFuture，用于执行异步任务并获取结果。

此外，JUC 中很多同步工具都基于 AQS 实现，AQS 通过状态变量、CAS 和等待队列提供通用的线程同步机制。