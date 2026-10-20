JVM 调优参数说到底是启动时那一串 `-X` / `-XX` 开头的选项，按功能分几类：**堆内存参数、垃圾收集器参数、元空间参数、线程栈参数、GC 日志参数**。

面试里真正需要张口就来的没那么多，`-Xms`、`-Xmx`、`-Xss`、`-XX:MaxMetaspaceSize`、`-XX:+UseG1GC` 这几个是底线，剩下的知道大概方向就行。关键是能说清楚每个参数解决什么问题，而不是报菜名。

## 一、堆内存参数

堆是存对象的地方，也是 JVM 调优的主战场。常用参数如下：

|参数|作用|示例|
|---|---|---|
| `-Xms` |设置初始堆大小| `-Xms2g` |
| `-Xmx` |设置最大堆大小| `-Xmx2g` |
| `-Xmn` |设置年轻代大小| `-Xmn512m` |
| `-XX:NewRatio` |设置老年代与年轻代的容量比例| `-XX:NewRatio=2` |
| `-XX:SurvivorRatio` |设置 Eden 与单个 Survivor 区的容量比例| `-XX:SurvivorRatio=8` |

### 1. -Xms 和 -Xmx

这两个参数长得像，作用也差不多，一个管初始堆，一个管最大堆：

```
-Xms2g -Xmx2g
```

表示 JVM 启动时堆就是 2 GB，最多也长到 2 GB。

**实际部署通常把两个值设成一样，原因是堆在运行过程中会动态扩容和收缩，这个动作本身有开销，固定下来内存使用更稳定。**

但堆不是越大越好。堆开得太大，一是占机器内存，二是某些收集器回收起来更费时间，单次停顿反而变长。

### 2. -Xmn

单独指定年轻代大小：

```
-Xmn512m
```

假设堆是 2 GB，年轻代给了 512 MB，剩下的 1536 MB 就是老年代：

```
              JVM 堆（2GB）
┌────────────────────────────────┐
│                                │
│        年轻代（512MB）          │
│                                │
├────────────────────────────────┤
│                                │
│        老年代（1536MB）         │
│                                │
└────────────────────────────────┘
```

年轻代小，Young GC 就频繁；年轻代大，又会挤占老年代的空间，这两句就是它的取舍。

**⚠️ 用 G1 的时候一般不建议手动指定 `-Xmn`，G1 自己会按停顿目标动态调整年轻代大小，手填反而会打乱它的节奏。**

---

## 二、垃圾收集器参数

JVM 内置了好几种收集器，用参数来选：

|参数|作用|
|---|---|
| `-XX:+UseSerialGC` |使用 Serial 垃圾收集器|
| `-XX:+UseParallelGC` |使用 Parallel GC|
| `-XX:+UseG1GC` |使用 G1 垃圾收集器|
| `-XX:+UseZGC` |使用 ZGC 垃圾收集器|
| `-XX:MaxGCPauseMillis` |设置期望的最大 GC 停顿时间目标|

### 1. UseG1GC

```
-XX:+UseG1GC
```

G1 把堆切成一个个 Region，回收时不是整个新生代 / 老年代一起动，而是挑回收收益高的 Region 先收。特点是支持较大堆、可以设停顿目标、吞吐和延迟之间比较均衡。从 JDK 9 开始，HotSpot 在服务端常见配置下默认就是 G1。

### 2. MaxGCPauseMillis

```
-XX:MaxGCPauseMillis=200
```

意思是希望每次 GC 停顿控制在 200 ms 左右。

**这里容易搞混：200 ms 是软目标，不是硬指标，不代表每次 GC 一定小于 200 ms。** G1 会拿这个值去调整回收策略，比如少收几个 Region 来换更短的停顿。目标设得太激进，GC 会变得频繁，整体吞吐量被拖下来。

---

## 三、元空间参数

从 JDK 8 开始，HotSpot 用元空间（Metaspace）存类元数据，不再用永久代。

|参数|作用|
|---|---|
| `-XX:MetaspaceSize` |设置元空间触发相关 GC 的初始阈值|
| `-XX:MaxMetaspaceSize` |限制元空间最大大小|

例如：

```
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m
```

**最容易搞混的是 `MetaspaceSize`，它不是元空间的初始分配容量，而是触发元空间相关 GC 的初始高水位阈值。** 到水位会触发一次 GC，之后 JVM 再根据释放情况调整这个阈值。真正限制上限的是 `MaxMetaspaceSize`。

业务里大量用动态代理、反射、动态类加载，元空间涨得会快一些。真碰到这个异常：

```
java.lang.OutOfMemoryError: Metaspace
```

要去查类加载数量、ClassLoader 有没有泄漏，以及元空间配置，堆内存加再多也没用，因为这是堆外面的事。

---

## 四、线程栈参数 -Xss

```
-Xss1m
```

表示每个 Java 线程的栈大小是 1 MB。栈里放的是方法调用时的栈帧，栈帧里又有局部变量表、操作数栈这些。

栈太小，递归一深就会栈溢出：

```
java.lang.StackOverflowError
```

比如这样：

```java
public void test() {
    test();
}
```

这种无限递归就是最典型的栈溢出。

但栈也不是越大越好。1 MB × 1000 个线程就是 1 GB 内存，线程数一多，线程栈加起来相当可观。**所以 `-Xss` 要结合线程数量和方法调用深度来定，不是无脑调大。**

---

## 五、GC 日志参数

JVM 调优不能只改参数，还得能看见改完之后的效果，GC 日志就是干这个的。

JDK 8：

```
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xloggc:/logs/gc.log
```

JDK 9 及以上统一成 Xlog：

```
-Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags
```

日志里主要看四件事：**Young GC 和 Full GC 多久发生一次、每次停顿多久、GC 前后内存掉了多少、这次 GC 是什么原因触发的。**

再配上这两个：

```
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/logs/
```

发生支持该机制的 `OutOfMemoryError` 时自动生成堆转储文件，之后用 MAT 之类的工具分析是谁把内存吃掉了。排查内存泄漏时这一步基本是必需的，因为线上的现场不 dump 就没了。

---

## 六、其他常见参数

|参数|作用|
|---|---|
| `-XX:MaxTenuringThreshold` |设置对象晋升年龄的上限|
| `-XX:ParallelGCThreads` |设置部分并行 GC 工作线程数量|
| `-XX:ConcGCThreads` |设置部分并发 GC 工作线程数量|
| `-XX:+DisableExplicitGC` |禁止显式 GC 请求触发常规 GC|
| `-XX:+UseStringDeduplication` |在支持的收集器中启用字符串去重|
| `-XX:InitiatingHeapOccupancyPercent` |影响 G1 等收集器并发标记的启动阈值|

`-XX:MaxTenuringThreshold` 别理解成"对象一定要熬过指定次数的 Young GC 才会晋升"。实际晋升还要看 Survivor 空间够不够、对象年龄分布和收集器策略，这个阈值只是个上限。

---

## 七、实际项目中怎么配置 JVM？

假设一个 Spring Boot 后端服务，跑在 **4 核 8 GB 内存的 Linux 服务器**上，JDK 17，可以从这组配置开始测：

```
java \
  -Xms2g \
  -Xmx2g \
  -Xss1m \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/logs/ \
  -Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags \
  -jar app.jar
```

|参数|配置|目的|
|---|---|---|
|Xms|2 GB|初始堆内存|
|Xmx|2 GB|最大堆内存|
|Xss|1 MB|每个线程的栈大小|
|UseG1GC|开启|使用 G1|
|MaxGCPauseMillis|200 ms|设置 GC 停顿目标|
|HeapDumpOnOutOfMemoryError|开启|OOM 时生成堆转储|
|Xlog|开启|记录 GC 日志|

**注意，这只是一个示例起点，不是 8 GB 服务器的标准答案。** 如果服务器上还部署了 MySQL、Redis、RabbitMQ，就要给这些服务留内存，再算上 JVM 自己的元空间、线程栈、直接内存。堆给 2 GB 是因为剩下的要留给别人，不是随手写的数字。

---

## 八、JVM 调优的正确思路

面试官如果继续问"那你会怎么进行 JVM 调优"，上来就说改 `Xmx` 或者换收集器基本就废了。

正确流程应该是：

```
① 发现性能问题
      │
      ▼
② 收集监控指标
   GC 次数、耗时、堆使用率
      │
      ▼
③ 分析 GC 日志
   判断是否存在频繁 GC
      │
      ▼
④ 定位根本原因
   内存泄漏？
   对象创建过快？
   堆内存不足？
   GC 停顿过长？
      │
      ▼
⑤ 调整 JVM 参数或优化代码
      │
      ▼
⑥ 压测验证
   比较优化前后的 GC 情况
```

几个典型判断：

- Young GC 非常频繁 → 看对象分配速率和年轻代容量，是创建得太快还是新生代太小；
- Full GC 之后内存下降很少 → 重点排查长期存活对象、内存泄漏或容量不足；
- GC 停顿时间过长 → 结合垃圾收集器类型、堆大小和停顿目标一起分析。

**调优的核心不是把参数调得越大越好，而是在内存占用、吞吐量和延迟之间找平衡。** 这三个目标是互相拉扯的：堆调大，延迟可能变好，但内存占用上去了；停顿目标压得太低，吞吐量又下来了。

---

## 九、面试怎么回答？

按类别说，比背参数名强。

> JVM 常见的调优参数主要分五类：堆内存、垃圾收集器、元空间、线程栈、GC 日志。堆内存主要是 `-Xms` 和 `-Xmx`，分别设初始堆和最大堆，通常设成相同值，减少堆动态扩缩容的开销。收集器用 `-XX:+UseG1GC` 选 G1，`-XX:MaxGCPauseMillis` 设停顿时间目标。元空间用 `-XX:MaxMetaspaceSize` 限制上限，线程栈用 `-Xss`。日志和诊断靠 `-Xlog` 记录 GC 过程，`-XX:+HeapDumpOnOutOfMemoryError` 在 OOM 时生成堆转储。

> 实际调优时，先通过 `jstat`、GC 日志和内存分析工具定位问题，看 GC 频率、停顿时间、对象分配情况和内存使用情况，再决定改哪个参数，而不是盲目扩大堆内存。

---

### 最后总结

**Java 后端面试优先记住这 8 个参数：**

|参数|作用|
|---|---|
| `-Xms` |初始堆大小|
| `-Xmx` |最大堆大小|
| `-Xss` |线程栈大小|
| `-XX:MaxMetaspaceSize` |元空间大小上限|
| `-XX:+UseG1GC` |选择 G1 收集器|
| `-XX:MaxGCPauseMillis` |GC 停顿时间目标|
| `-Xlog:gc*` |记录 GC 日志（JDK 9+）|
| `-XX:+HeapDumpOnOutOfMemoryError` |OOM 时生成 Heap Dump|

**面试时能解释这些参数的作用，并说明什么情况下需要调整，比单纯背几十个 JVM 参数更重要。**
