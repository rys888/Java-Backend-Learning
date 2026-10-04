Stream 流的并行 API 主要就是 ** `parallelStream()` ** 和 ** `parallel()` **。

比如普通串行流：

```java
list.stream()
    .forEach(System.out::println);
```

改成并行流：

```java
list.parallelStream()
    .forEach(System.out::println);
```

也可以先创建普通 Stream，再转换：

```java
list.stream()
    .parallel()
    .forEach(System.out::println);
```

两者最终都是得到 **并行 Stream**。

### **它是怎么并行的？**

可以简单理解成把一批数据**拆成多个小任务，让多个线程同时处理，最后再合并结果**：

```text
[1,2,3,4,5,6,7,8]
        ↓
      拆分
   ↙    ↓    ↘
[1,2] [3,4] [5,6] [7,8]
   ↓     ↓     ↓     ↓
 线程1  线程2  线程3  线程4
   ↘     ↓     ↓     ↙
        合并结果
```

Java 8 的并行 Stream 底层主要依赖 **Fork/Join 框架**，默认通常使用：

```java
ForkJoinPool.commonPool()
```

### **面试怎么回答？**

如果面试官问：

Stream 流的并行 API 是什么？

可以回答：

Java Stream 可以通过 `parallelStream()` 直接创建并行流，也可以通过普通 Stream 的 `parallel()` 方法转换成并行流。并行 Stream 会将数据拆分成多个任务并行处理，底层主要基于 Fork/Join 框架，默认通常使用 `ForkJoinPool.commonPool()`。不过并行流并不一定比串行流快，因为任务拆分、线程调度和结果合并本身也有开销，而且还需要注意线程安全问题。

再记一个对应关系就行：

```text
stream()          → 串行流
parallelStream()  → 并行流

parallel()        → 转并行
sequential()      → 转串行
```

实习八股问到这里，基本就够了。