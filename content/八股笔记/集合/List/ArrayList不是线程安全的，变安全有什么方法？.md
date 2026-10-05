### **为什么 ArrayList 不线程安全？**

主要有三个问题：
- 部分值为 null（没有 add null 进去）
- 索引越界异常
- size 与 add 的数量不符情况

可以从 `ArrayList.add()` **不是一个原子操作**来理解。多个线程同时 `add()` 时，它们会共同读写 `size` 和底层数组 `elementData`，而这些操作没有同步保护。

先把 `add()` 极度简化成：

```java
public boolean add(E e) {
    // ① 检查/扩容
    if (size == elementData.length) {
        扩容();
    }

    // ② 放入元素
    elementData[size] = e;

    // ③ size 增加
    size++;

    return true;
}
```

实际 JDK 实现细节会因版本不同而不同，但理解并发问题，用这个模型就够了。

### **1. 为什么 `size` 会小于实际 `add` 次数？

假设现在：

```text
size = 5
```

线程 A 和线程 B 同时执行 `add()`。

两边都可能先读到：

```text
线程A：size = 5
线程B：size = 5
```

于是都准备操作位置 5：

```text
线程A：elementData[5] = "A"

线程B：elementData[5] = "B"
```

可能发生覆盖：

```text
原本：

[0][1][2][3][4][ ]

线程A：
[0][1][2][3][4][A]

线程B：
[0][1][2][3][4][B]
                 ↑
               A被覆盖
```

同时，类似 `size++` 这种操作也不是一个不可分割的原子动作，可以理解为：

```text
读取 size
   ↓
size + 1
   ↓
写回 size
```

两个线程都可能：

```text
线程A：读取5 → 计算6 → 写入6
线程B：读取5 → 计算6 → 写入6
```

最终：

```text
执行了两次 add

理论：
size = 7

实际可能：
size = 6
```

这就是**丢失更新（Lost Update）**。

---
### **2. 为什么可能出现 `null` ？

这个稍微复杂一点，通常与**并发修改内部状态、扩容/数组替换，以及读取方没有同步保证**有关。

比如底层数组满了：

```text
elementData：

[A][B][C][D]
             size = 4
```

此时多个线程同时 `add()`，可能同时涉及：

```text
检查容量
   ↓
扩容
   ↓
复制旧数组
   ↓
替换 elementData
   ↓
写入新元素
   ↓
修改 size
```

而这些步骤整体并没有锁保护。

于是一个线程可能正在修改：

```text
elementData
size
```

另一个线程同时又在读取/修改这些状态。

因此可能观察到**不一致的内部状态**，例如逻辑上的 `size` 与数组中实际已经安全可见的元素状态不一致，从而可能读到本不应该出现的 `null`。

这里面还涉及 Java 内存模型的**可见性**问题：

```text
线程A
 ↓
修改数组 / size

      没有 synchronized / volatile 等同步关系

线程B
 ↓
不保证以一致的方式观察到线程A的修改
```

所以本质：

**ArrayList 的内部数组和 size 没有为并发读写提供同步保证，因此并发修改时内部状态可能不一致。**

---

### **3. 为什么可能数组越界？**

这个尤其容易出现在**并发扩容和修改**过程中。

正常情况下：

```text
size == 数组容量
       ↓
先扩容
       ↓
再写入 elementData[size]
```

单线程时这个流程没有问题。

但是多线程同时执行：

```text
线程A ──→ 检查容量 ──→ 扩容 ──→ 写入
                       ↑
线程B ──→ 检查容量 ─────────→ 写入
```

由于：

```text
size
elementData
```

都在被多个线程无同步地修改，某个线程使用的 `size`、容量判断以及当前底层数组状态可能不一致。

最终就可能出现：

```java
elementData[index] = e;
```

这里的：

```text
index >= elementData.length
```

从而抛出类似：

```text
ArrayIndexOutOfBoundsException
```

核心问题只有一个：

```text
多个线程
   ↓
同时操作 ArrayList
   ↓
共同修改
size + elementData
   ↓
add不是整体原子操作
+ 没有同步保护
   ↓
竞态条件 Race Condition
   ↓
内部状态可能不一致
```

### Q：**为什么 ArrayList 线程不安全？**

ArrayList 内部主要维护了 `elementData` 数组和 `size`，它的 `add` 等修改操作没有使用同步机制。在多个线程同时执行 add 时，对 size 的读取、修改以及对数组的写入、扩容都可能发生竞争。比如两个线程可能读取到相同的 size，并对同一个数组位置写入，产生元素覆盖和 size 丢失更新；在并发扩容、读写时还可能观察到不一致的内部状态。因此 ArrayList 不适合在没有额外同步措施的情况下被多个线程并发修改。

---
## 解决方法
### **第一种：`Collections.synchronizedList()` 

代码完整写法类似：

```java
List<String> arrayList = new ArrayList<>();

List<String> synchronizedList =
        Collections.synchronizedList(arrayList);
```

它的思想非常简单：

**给普通 List 包一层同步包装。**

调用方法时候相当于获取了互斥锁！

可以粗略理解：

```text
原来的：

线程1 ─┐
       ├──→ ArrayList
线程2 ─┘


包装以后：

线程1 ─┐
       ↓
   synchronized
       ↓
   ArrayList
       ↑
线程2 ─┘
```

比如调用：

```java
synchronizedList.add("Java");
```

内部会进行同步控制，避免多个线程同时执行关键修改操作。

**普通 List + synchronized 包装 = 线程安全 List。**

---

### **第二种：**`CopyOnWriteArrayList` **⭐⭐⭐⭐⭐**

这个比 `Vector` 更值得你重点学。

```java
CopyOnWriteArrayList<String> list =
        new CopyOnWriteArrayList<>();
```

名字就告诉了你原理：

**Copy On Write = 写的时候复制。**

假设现在：

```text
原数组：

[A, B, C]
```

线程想加入 D：

```text
[A, B, C]
     ↓
   复制
     ↓
[A, B, C, D]
     ↓
替换内部数组引用
```

也就是说，写操作不会直接在原数组上随意修改，而是创建新的数组并完成修改，再更新引用；写入过程还会有相应的并发控制。

最大的好处是：

**读操作通常不需要像 synchronizedList 那样获取同一个互斥锁。**

因此特别适合：

```text
读操作：⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐
写操作：⭐⭐
```

也就是：

**读多写少的并发场景。**

例如系统里有一个配置列表：

```java
CopyOnWriteArrayList<String> configs =
        new CopyOnWriteArrayList<>();
```

大量线程不断读取配置，但配置偶尔才更新一次，这种场景就比较合适。

但如果：

```text
add
remove
add
remove
add
remove
...
```

写操作非常频繁，就不适合，因为每次写都涉及数组复制，成本较高。

所以直接记：

**CopyOnWriteArrayList：线程安全 + 写时复制 + 读多写少。**

---

### **第三种：Vector**

```java
Vector<String> vector = new Vector<>();
```

刚刚已经学过它。

它也是：

**动态数组 + 线程安全。**

它的很多方法使用 `synchronized`：

```java
public synchronized boolean add(E e) {
    ...
}
```

可以粗略理解：

```text
线程1 ──→ synchronized add()
                    ↓
                  Vector
                    ↑
线程2 ──→ 等待
```

因此：

```text
ArrayList
动态数组
线程不安全

Vector
动态数组
很多方法 synchronized
线程安全
```

但 `Vector` 是比较老的集合类，现在通常不会因为需要并发安全就优先选择它。

---

### **三种方案放一起理解**

|**方案**|**核心原理**|**特点**|
|---|---|---|
| `Collections.synchronizedList()` |synchronized 包装普通 List|简单直接|
| `CopyOnWriteArrayList` |写时复制|⭐ 适合读多写少|
| `Vector` |很多方法 synchronized|老牌线程安全集合|

所以这张图你最终记成：

```text
ArrayList
   ↓
线程不安全
   ↓
需要线程安全怎么办？
   │
   ├── Collections.synchronizedList()
   │         ↓
   │     同步包装
   │
   ├── CopyOnWriteArrayList ⭐
   │         ↓
   │     写时复制
   │     适合读多写少
   │
   └── Vector
             ↓
       synchronized
       较老
```

### Q：

ArrayList 本身不是线程安全的。如果需要线程安全的 List，可以通过 `Collections.synchronizedList()` 对 ArrayList 进行同步包装，也可以使用 `CopyOnWriteArrayList`，它采用写时复制机制，比较适合读多写少的并发场景。另外 Vector 也是线程安全的 List 实现，它的很多方法通过 synchronized 保证线程安全，但现在使用相对较少。


⚠️：gpt 老师和我说尤其要把 `CopyOnWriteArrayList` 记住，因为后面学 `ConcurrentHashMap` 时，会一起进入 Java **JUC 并发集合**这一块。