Java 8 新特性是 **Java 后端实习面试非常经典的一组八股**。不用把 JDK 8 所有变化都背下来，Oracle 官方列出的变化很多，但从面试角度，重点集中在 **Lambda、函数式接口、Stream、方法引用、接口 default/static 方法、Optional、新日期时间 API、CompletableFuture，以及 JVM 的永久代→元空间变化**。Oracle 官方也将 Lambda、方法引用、默认方法、Stream 等列为 JDK 8 的核心增强。 

|**特性**|**实习面试重要度**|**要掌握程度**|
|---|---|---|
|Lambda 表达式|⭐⭐⭐⭐⭐|必须|
|函数式接口|⭐⭐⭐⭐⭐|必须|
|Stream API|⭐⭐⭐⭐⭐|必须|
|方法引用|⭐⭐⭐⭐|必须|
|接口 default / static 方法|⭐⭐⭐⭐|必须|
|Optional|⭐⭐⭐⭐|必须|
|新日期时间 API|⭐⭐⭐|会说|
|CompletableFuture|⭐⭐⭐⭐|并发部分重点|
|HashMap 优化|⭐⭐⭐⭐⭐|放到集合八股重点学|
|永久代 → 元空间|⭐⭐⭐⭐⭐|放到 JVM 八股重点学|
|重复注解 / 类型注解等|⭐⭐|知道即可|

---

# **一、Lambda 表达式 ⭐⭐⭐⭐⭐**

这是 Java 8 最标志性的特性之一。

以前想把“一段行为”传进去，经常需要匿名内部类。

比如开一个线程：

```java
new Thread(new Runnable() {
    @Override
    public void run() {
        System.out.println("执行任务");
    }
}).start();
```

Java 8 可以：

```java
new Thread(() -> {
    System.out.println("执行任务");
}).start();
```

甚至：

```java
new Thread(() -> System.out.println("执行任务")).start();
```

Lambda 基本语法：

```text
(参数) -> { 方法体 }
```

例如：

```java
(a, b) -> a + b
```

你可以简单理解成：

**Lambda 就是用更加简洁的方式表示“一段可以传递的行为”。**

但面试官很可能继续问：

**Lambda 随便什么接口都能用吗？**

不能。

它主要配合下面的**函数式接口**使用。Oracle 对 Lambda 的描述也是：它能够更加紧凑地表达单一抽象方法接口的实例。 

---

# **二、函数式接口 ⭐⭐⭐⭐⭐**

函数式接口：

**只有一个抽象方法的接口。**

例如：

```java
@FunctionalInterface
public interface Calculator {

    int calculate(int a, int b);
}
```

因为只有一个抽象方法，所以可以：

```java
Calculator c = (a, b) -> a + b;

System.out.println(c.calculate(10, 20));
```

这里：

```java
(a, b) -> a + b
```

实际上就是在提供：

```java
int calculate(int a, int b)
```

这个方法的实现。

所以你要建立这个关系：

```text
函数式接口
     ↑
Lambda 为它提供实现
```

Java 8 提供了很多现成函数式接口，集中在 `java.util.function` 包中。 

面试最常见四个：

|**接口**|**参数**|**返回值**|**理解**|
|---|---|---|---|
| `Function<T,R>` |T|R|输入一个，返回一个|
| `Consumer<T>` |T|void|消费一个东西|
| `Supplier<T>` |无|T|提供一个东西|
| `Predicate<T>` |T|boolean|判断|

例如：

```java
Predicate<Integer> p = age -> age >= 18;

System.out.println(p.test(20)); // true
```

就是：

```text
20
 ↓
age >= 18
 ↓
true
```

这个非常重要，因为后面的 **Stream 本质上大量使用这些函数式接口**。

---

# **三、Stream API ⭐⭐⭐⭐⭐**

这是 Java 8 面试的绝对重点。

注意：

**Stream 不是数据结构，它自己不存数据，而是对数据进行流水线式处理。**

比如：

```java
List<Integer> list =
        Arrays.asList(1, 2, 3, 4, 5, 6);
```

要求：

找出所有偶数，然后乘 10。

传统写法：

```java
List<Integer> result = new ArrayList<>();

for (Integer num : list) {
    if (num % 2 == 0) {
        result.add(num * 10);
    }
}
```

Stream：

```java
List<Integer> result = list.stream()
        .filter(x -> x % 2 == 0)
        .map(x -> x * 10)
        .collect(Collectors.toList());
```

你可以把它理解成流水线：

```text
1 2 3 4 5 6
    ↓
filter(x -> x % 2 == 0)
    ↓
2 4 6
    ↓
map(x -> x * 10)
    ↓
20 40 60
    ↓
collect
    ↓
List
```

Oracle 官方说明，Java 8 新增 `java.util.stream`，用于对元素流执行函数式操作，并与 Collections API 集成。 

## **Stream 常见操作必须认识**

### **filter：过滤**

```java
list.stream()
    .filter(x -> x > 10);
```

保留：

```text
x > 10
```

的数据。

### **map：转换**

```java
list.stream()
    .map(x -> x * 2);
```

例如：

```text
1 2 3

↓

2 4 6
```

### **sorted：排序**

```java
list.stream()
    .sorted();
```

### **distinct：去重**

```java
list.stream()
    .distinct();
```

### **forEach：遍历**

```java
list.stream()
    .forEach(System.out::println);
```

### **collect：收集结果**

```java
List<Integer> result = list.stream()
        .filter(x -> x > 10)
        .collect(Collectors.toList());
```

---

# **四、Stream 的中间操作和终止操作 ⭐⭐⭐⭐**

这个非常容易被追问。

Stream 操作分两类。

### **中间操作**

例如：

```text
filter
map
sorted
distinct
limit
skip
```

特点：

返回新的 Stream，可以继续链式调用。

例如：

```java
list.stream()
    .filter(...)
    .map(...)
    .sorted(...)
```

而且中间操作具有**惰性**，没有终止操作时通常不会真正执行整个流水线。

---

### **终止操作**

例如：

```text
collect
forEach
count
reduce
findFirst
```

它会触发 Stream 流水线执行。

例如：

```java
long count = list.stream()
        .filter(x -> x > 10)
        .count();
```

所以：

```text
数据源

 ↓

filter     ← 中间操作
 ↓
map        ← 中间操作
 ↓
sorted     ← 中间操作
 ↓
collect    ← 终止操作

 ↓

结果
```

---
# **五、方法引用**  `::`  ⭐⭐⭐⭐

你肯定在代码里见过：

```java
System.out::println
```

它是 Java 8 的**方法引用**。

例如 Lambda：

```java
list.forEach(x -> System.out.println(x));
```

可以简化：

```java
list.forEach(System.out::println);
```

因为 Lambda 做的事情仅仅是：

```text
收到 x
 ↓
调用 println(x)
```

所以可以直接引用已经存在的方法。

再比如：

```java
list.stream()
    .map(x -> x.toString());
```

可以写成：

```java
list.stream()
    .map(Object::toString);
```

记住：

**方法引用可以理解为 Lambda 的进一步简化：如果 Lambda 只是调用一个已经存在的方法，就可以考虑使用**  `::` ****。**

Oracle 也将方法引用描述为针对已有命名方法的一种更易读的 Lambda 表达形式。 

---

# **六、接口 default 方法 ⭐⭐⭐⭐**

Java 8 以前，接口的方法主要是抽象方法：

```java
interface Animal {
    void eat();
}
```

实现类必须实现：

```java
class Dog implements Animal {

    @Override
    public void eat() {
    }
}
```

Java 8 允许接口拥有：

```java
default
```

方法。

```java
interface Animal {

    void eat();

    default void sleep() {
        System.out.println("睡觉");
    }
}
```

实现类：

```java
class Dog implements Animal {

    @Override
    public void eat() {
        System.out.println("吃饭");
    }
}
```

即使没有实现 `sleep()`：

```java
dog.sleep();
```

也可以调用。

### **为什么 Java 8 要引入 default？**

这是面试比较喜欢问的。

假设：

```java
interface Animal {
    void eat();
}
```

已经有 100 个实现类。

现在突然给接口增加：

```java
void sleep();
```

那么：

100 个实现类理论上都需要实现 `sleep()`。

兼容性会有问题。

所以：

```java
default void sleep() {
    // 默认实现
}
```

老的实现类不需要修改。

因此核心目的：

**在不破坏已有实现类兼容性的情况下，为接口增加新的方法实现。**

Oracle 官方明确说明，default method 的设计目标之一就是给已有接口增加功能，同时保持旧代码的二进制兼容性。 

---

# **七、接口 static 方法 ⭐⭐⭐**

Java 8 还允许接口定义静态方法：

```java
interface Utils {

    static void hello() {
        System.out.println("hello");
    }
}
```

调用：

```java
Utils.hello();
```

所以 Java 8 以后：

```text
接口

├── abstract method
├── default method
└── static method
```

---

# **八、Optional ⭐⭐⭐⭐**

以前 Java 最经典的问题：

```java
User user = getUser();

System.out.println(user.getName());
```

如果：

```java
user == null
```

直接：

```text
NullPointerException
```

Java 8 提供：

```java
Optional<T>
```

它是一个：

**可能包含非 null 值，也可能为空的容器。**  

例如：

```java
Optional<User> user = findUser();
```

判断：

```java
if (user.isPresent()) {
    System.out.println(user.get());
}
```

更常见：

```java
User result = user.orElse(new User());
```

意思：

```text
有 User
 ↓
返回 User

没有
 ↓
返回默认 User
```

还可以：

```java
user.ifPresent(System.out::println);
```

常见方法：

```text
Optional.of()
Optional.ofNullable()
Optional.empty()

isPresent()
ifPresent()

orElse()
orElseGet()

map()
flatMap()
```

### **高频坑：of 和 ofNullable**

```java
Optional.of(null);
```

直接 NPE。

而：

```java
Optional.ofNullable(null);
```

得到：

```java
Optional.empty()
```

所以：

`of()` 要求对象不能为空；`ofNullable()` 允许 null。

---

# **九、新的日期时间 API ⭐⭐⭐**

Java 8 新增：

```java
java.time
```

Oracle 将新的 Date-Time Package 作为 JDK 8 的重要新增 API。 

常见类：

```text
LocalDate       日期
LocalTime       时间
LocalDateTime   日期 + 时间
Instant         时间戳/时间线上的瞬时点
Duration        时间间隔
Period          日期间隔
DateTimeFormatter 格式化
```

例如：

```java
LocalDate now = LocalDate.now();
```

```java
LocalDateTime now = LocalDateTime.now();
```

```java
LocalDateTime tomorrow =
        LocalDateTime.now().plusDays(1);
```

格式化：

```java
DateTimeFormatter formatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

String result =
        LocalDateTime.now().format(formatter);
```

八股回答重点：

Java 8 引入 `java.time` 日期时间 API，相比旧的 `Date`、`Calendar` API 设计更加清晰；核心日期时间类型通常采用不可变设计，更适合并发环境。

---

# **十、CompletableFuture ⭐⭐⭐⭐**

这个等学**多线程/线程池**时要重点掌握。

Java 8 新增：

```java
CompletableFuture
```

用于：

**异步编程和异步任务编排。**

例如：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            return "查询数据库结果";
        });
```

主线程可以继续干其他事情。

之后：

```java
String result = future.get();
```

获取结果。

还可以：

```java
CompletableFuture.supplyAsync(() -> "hello")
        .thenApply(x -> x + " world")
        .thenAccept(System.out::println);
```

形成：

```text
异步任务
   ↓
得到 "hello"
   ↓
thenApply
   ↓
"hello world"
   ↓
thenAccept
   ↓
打印
```

`CompletableFuture` 同时实现 `Future` 和 `CompletionStage`，可以组合多个异步阶段；没有显式指定 Executor 的 `async` 方法通常使用 `ForkJoinPool.commonPool()`。 

面试初期你先知道：

**Future 主要解决异步任务结果获取；CompletableFuture 在此基础上进一步支持任务编排、回调和组合，减少大量阻塞式等待。**

后面学并发再深入：

```text
runAsync
supplyAsync
thenApply
thenAccept
thenRun
thenCompose
thenCombine
allOf
anyOf
exceptionally
handle
```

---

# **十一、HashMap 优化 ⭐⭐⭐⭐⭐**

这个虽然属于 Java 8 改动，但**不要放在“Java 8 新特性”这里死背**。

等你学 HashMap 时重点掌握。

Java 7：

```text
数组 + 链表
```

Java 8：

```text
数组 + 链表 + 红黑树
```

大概：

```text
table

[0]
[1] → Node → Node
[2]
[3] → Node → Node → Node → Node → ...
                       ↓
                 链表过长
                       ↓
                    红黑树
```

Java 8 对 HashMap 的 key collision 性能进行了改进。 

你之后专门学 HashMap 时，要掌握经典条件：

**链表长度达到 8，并且数组容量达到 64，才会进行树化；否则优先扩容。**

这个比单纯知道“Java 8 加红黑树”重要得多。

---

# **十二、永久代 PermGen → 元空间 Metaspace ⭐⭐⭐⭐⭐**

这个属于 **JVM 八股**。

Java 7 时代 HotSpot 有：

```text
Heap
├── Young
├── Old
└── ...

PermGen 永久代
```

Java 8：

```text
永久代被移除

       ↓

Metaspace 元空间
```

最重要区别：

```text
PermGen
  ↓
主要受 JVM 分配的内存空间限制

Metaspace
  ↓
使用本地内存 Native Memory
```

主要用于存储类元数据等。

面试经常问：

Java 8 JVM 最大变化之一是什么？

可以回答：

**HotSpot 在 JDK 8 中移除了永久代，引入元空间 Metaspace，类元数据主要存储在本地内存中。**

这个以后 JVM 专题再详细学。

---

# **十三、其他知道名字即可**

Oracle 官方还列出了：

- 重复注解 `Repeating Annotations`
- 类型注解 `Type Annotations`
- 方法参数反射
- 类型推断增强
- Nashorn JavaScript 引擎
- `StringJoiner`
- `Spliterator`
- 集合 API 增强
- `Map.computeIfAbsent()`、`getOrDefault()` 等

这些确实属于 Java 8 的变化。 

但是你现在准备 **Java 后端实习**，不建议花大量时间背这些。

---

# **最后给你一版「面试回答」**

如果面试官直接问：

**“说一下 Java 8 有哪些新特性？”**

你不要回答十几分钟，第一轮这样说：

Java 8 比较重要的新特性主要有：首先是 **Lambda 表达式和函数式接口**，让 Java 支持更加函数式的编程方式；其次引入了 **Stream API**，可以对集合数据进行过滤、映射、聚合等流水线操作；同时加入了**方法引用**来进一步简化 Lambda。

接口方面支持了 **default 方法和 static 方法**，其中 default 方法可以在不破坏原有实现类的情况下扩展接口。

API 方面还加入了 **Optional** 来更明确地表示一个值可能不存在，以及新的 **java.time 日期时间 API**。

并发方面 Java 8 引入了 **CompletableFuture**，增强了异步任务的组合和编排能力。

另外，Java 8 中 **HashMap 在哈希冲突严重时可以由链表转为红黑树**；HotSpot JVM 中也**移除了永久代并使用 Metaspace 元空间**。

然后停下来。

**面试官对哪个感兴趣，就会往哪个方向追问。**

而这道题最容易形成的追问链是：

```text
Java 8 新特性
   │
   ├── Lambda
   │     ↓
   │   函数式接口是什么？
   │     ↓
   │   Function / Consumer / Supplier / Predicate？
   │
   ├── Stream
   │     ↓
   │   filter / map / reduce？
   │     ↓
   │   中间操作和终止操作？
   │     ↓
   │   parallelStream？
   │
   ├── Optional
   │     ↓
   │   of 和 ofNullable？
   │     ↓
   │   orElse 和 orElseGet？
   │
   ├── CompletableFuture
   │     ↓
   │   Future 有什么问题？
   │     ↓
   │   thenApply / thenCompose？
   │     ↓
   │   默认使用什么线程池？
   │
   ├── HashMap
   │     ↓
   │   数组+链表+红黑树
   │     ↓
   │   为什么树化？
   │     ↓
   │   为什么阈值是8？
   │
   └── JVM
         ↓
       PermGen 和 Metaspace
         ↓
       元空间存在哪里？
```

**先吃透前 6 个：Lambda → 函数式接口 → Stream → 方法引用 → default 方法 → Optional。** 这几个实际上是一整套东西，不要拆成六个互不相关的知识点来背。等进入并发和 JVM，再分别把 `CompletableFuture` 和 Metaspace 补深。