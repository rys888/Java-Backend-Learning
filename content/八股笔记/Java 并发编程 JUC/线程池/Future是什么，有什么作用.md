
[[#Q：Future 是什么？]]

可以把 `Future` 理解成：
**Future = 异步任务的“结果凭证”。任务现在可能还没执行完，但我先拿到一个 Future，以后可以通过它获取结果、判断任务状态或者取消任务。**

### **1. 为什么需要 Future？**

假设线程池里执行一个计算任务：

```java
ExecutorService pool = Executors.newFixedThreadPool(3);

Future<Integer> future = pool.submit(() -> {
    Thread.sleep(2000);
    return 100;
});
```

执行 `submit()` 后，不需要等这个任务执行完：

```text
主线程
  │
  ├── submit(任务)
  │       ↓
  │     线程池
  │       ↓
  │     Worker执行任务
  │       ↓
  │     最终得到 100
  │
  └── 立即拿到 Future<Integer>
```

注意：

**拿到 Future ≠ 已经拿到结果。**

Future 更像一张：

```text
“取货单”
```

当把任务交给线程池：

```java
Future<Integer> future = pool.submit(task);
```

线程池告诉你：

“任务我接了，这个 `future` 给你，以后拿它来查结果。”

---

### **2. Future 最重要的方法**

常见的就这几个：

```java
future.get();

future.isDone();

future.cancel(true);

future.isCancelled();
```

其中最重要的是：

```java
Integer result = future.get();
```

它表示：**获取异步任务的执行结果。**

如果任务已经完成：

```text
future.get()
    ↓
直接得到 100
```

如果任务还没完成：

```text
future.get()
    ↓
主线程阻塞等待
    ↓
Worker执行完成
    ↓
得到100
    ↓
主线程继续
```

所以这是 Future 一个非常重要的特点：

**任务可以异步执行，但**  `get()`  **在结果没准备好时会阻塞。**

---
### **3.** `submit()` 为什么有 Future，`execute()` 没有？

这也是面试常问的。

```java
pool.execute(task);
```

主要是：我只想让线程池执行这个任务，不关心返回结果。

而：

```java
Future<Integer> future = pool.submit(task);
```

是我提交任务，而且之后还想知道执行结果/状态。

所以：

```text
execute()
   ↓
执行任务
   ↓
不返回 Future


submit()
   ↓
执行任务
   ↓
返回 Future
   ↓
以后可以 get() 获取结果
```

---

### **4. Future 和 Callable 又是什么关系？**

```java
Callable<Integer> task = () -> {
    return 100;
};
```

`Callable` 和 `Runnable` 最大区别之一：

```text
Runnable
↓
run()
↓
没有返回值


Callable<V>
↓
call()
↓
返回 V
```

然后：

```java
Future<Integer> future = pool.submit(task);
```

整个链路：

```text
Callable<Integer>
      ↓
提交给线程池
      ↓
pool.submit()
      ↓
Worker线程执行
      ↓
call()
      ↓
return 100
      ↓
结果保存起来
      ↓
Future<Integer>
      ↓
future.get()
      ↓
100
```

所以你可以把它们三个一起记：

**Callable 负责“产生结果”，线程池负责“执行任务”，Future 负责“获取/管理结果”。**

---

### **5. 一个完整例子**

```java
ExecutorService pool = Executors.newFixedThreadPool(3);

Future<Integer> future = pool.submit(() -> {
    Thread.sleep(2000);
    return 100;
});

System.out.println("主线程继续干其他事情");

Integer result = future.get();

System.out.println(result);

pool.shutdown();
```

大概执行过程：

```text
主线程                     Worker线程

submit()
   │
   ├──── Task ─────────────→ 执行任务
   │                         sleep 2秒
   ↓
拿到Future
   ↓
继续干其他事情
   ↓
future.get()
   ↓
结果还没有
   ↓
阻塞等待................... return 100
   ↓                           │
得到100 ←──────────────────────┘
   ↓
继续执行
```

这就是所谓的：

**异步执行 + Future 获取结果。**

---

### 6. Future 还有什么问题？

Future 最大的问题之一就是：

```java
future.get();
```

如果结果还没出来，调用线程就在那里**阻塞等待**。

假设有两个异步任务：

```java
Future<Integer> f1 = pool.submit(task1);
Future<Integer> f2 = pool.submit(task2);
```

如果你想：

task 1 完成之后自动处理结果，再和 task 2 的结果组合，然后统一处理异常……

传统 Future 写起来就不太舒服。

所以 Java 8 又提供了之前学过的：

```java
CompletableFuture
```

它支持：

```java
thenApply()
thenAccept()
thenCombine()
allOf()
exceptionally()
```

所以可以理解成：

```text
Future
   ↓
基础版异步结果

CompletableFuture
   ↓
更强的异步任务编排
```

---

### Q：Future 是什么？

`Future` 是 Java 中用于表示**异步任务执行结果**的接口。我们把任务通过线程池的 `submit()` 方法提交后，可以立即得到一个 Future，而不需要等待任务执行完成。

后续可以通过 `get()` 获取任务结果，如果任务还没有执行完成，`get()` 会阻塞等待；也可以通过 `isDone()` 判断任务是否完成，通过 `cancel()` 尝试取消任务。

Future 解决了异步任务结果获取的问题，但它的 `get()` 存在阻塞，并且不方便进行多个异步任务的组合和编排，因此 Java 8 又提供了 `CompletableFuture`。

你现在把线程池这几个东西连起来：

```text
             ThreadPoolExecutor
                    │
              submit(task)
                    ↓
            ┌──────────────┐
            │     Task     │
            └──────┬───────┘
                   ↓
               Worker执行
                   ↓
                产生结果
                   ↓
                 Future
                   ↓
             future.get()
                   ↓
                 结果
```

一句话口诀：

**线程池负责执行，Callable 负责返回，Future 负责拿结果。**