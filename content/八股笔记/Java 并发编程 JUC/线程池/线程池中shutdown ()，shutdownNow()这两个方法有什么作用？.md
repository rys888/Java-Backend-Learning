
[[#Q：线程池中 shutdown ()，shutdownNow()这两个方法有什么作用？]]

这两个都是用来**关闭线程池**的，但关闭的“激进程度”不一样。

 `shutdown()` ****：温柔关闭——不接新任务，但已经提交的任务继续执行。**  
`shutdownNow()` ****：激进关闭——不接新任务，队列里没开始的任务不再执行，并尝试中断正在执行的任务。**

### `shutdown()`

```java
executor.shutdown();
```

假设现在：

```text
正在执行：
Thread-1 → Task1
Thread-2 → Task2

队列：
Task3 → Task4 → Task5
```

调用：

```java
executor.shutdown();
```

之后：

```text
新 Task6
   ↓
❌ 不再接受

Task1、Task2
   ↓
✅ 继续执行

Task3、Task4、Task5
   ↓
✅ 之后继续执行
```

最终：

```text
已有任务全部执行完成
        ↓
Worker线程退出
        ↓
线程池终止
```

所以 `shutdown()` 可以理解成：

**“打烊了，不接新客人，但店里的客人全部服务完再关门。”**

注意，`shutdown()` **不会等所有任务执行完才返回**，它只是发起关闭。如果你需要当前线程等待线程池真正结束，可以配合：

```java
executor.shutdown();
executor.awaitTermination(10, TimeUnit.SECONDS);
```

---

###  `shutdownNow()` 

```java
List<Runnable> tasks = executor.shutdownNow();
```

假设还是：

```text
正在执行：
Thread-1 → Task1
Thread-2 → Task2

队列：
Task3 → Task4 → Task5
```

调用之后：

```text
新 Task6
   ↓
❌ 不接受

Task3、Task4、Task5
   ↓
❌ 从队列中移出，不再执行

Task1、Task2
   ↓
尝试 interrupt()
```

并且：

```java
shutdownNow()
```

会返回：

**尚未开始执行的队列任务列表。**

例如：

```text
返回：
[Task3, Task4, Task5]
```

---
### **最容易出错的点：

`shutdownNow()` **不是“强制杀死线程”**

这一点和你前面学的 `interrupt()` 完全一样。

`shutdownNow()` 对正在运行的 Worker 主要是：

**调用 interrupt，尝试中断。**

例如任务：

```java
while (!Thread.currentThread().isInterrupted()) {
    // 工作
}
```

收到 interrupt：

```text
interrupt()
   ↓
检测到中断
   ↓
结束任务
```

或者任务正在：

```java
Thread.sleep(10000);
```

被 interrupt 后：

```text
抛 InterruptedException
↓
任务可以结束
```

但是如果任务：

```java
while (true) {
    // 完全不响应中断
}
```

那么：

```text
shutdownNow()
↓
interrupt
↓
任务不配合
↓
❌ 不能保证立刻结束
```

所以名字虽然叫：

```text
shutdownNow
```

但不能理解成：

“现在立刻强制杀掉所有线程。”

更准确是：

**尽最大努力停止正在执行的任务。**

你可以直接记成：

```text
shutdown()
“不接新的，旧的干完”
        ↓
优雅关闭


shutdownNow()
“不接新的，排队的别干了，
 正在干的我 interrupt 一下”
        ↓
尝试快速关闭
```

### Q：线程池中 shutdown ()，shutdownNow()这两个方法有什么作用？

`shutdown()` 和 `shutdownNow()` 都用于关闭线程池。`shutdown()` 属于相对优雅的关闭方式，调用后线程池不再接受新任务，但是已经提交的任务，包括正在执行和队列中等待的任务，都会继续执行完成。

`shutdownNow()` 则会停止接收新任务，将队列中尚未开始执行的任务移出并返回，同时通过 `interrupt()` 尝试中断正在执行的 Worker 线程。但 Java 的 interrupt 是协作式中断，因此 `shutdownNow()` 也不能保证正在执行的任务立即停止。