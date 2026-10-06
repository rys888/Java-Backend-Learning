
**HashMap 追求高效，但不保证多线程安全；ConcurrentHashMap 在尽量保持高并发性能的同时，保证并发访问安全。**

而且这个题一定要分 **JDK 1.7 和 JDK 1.8** 来讲，因为实现变化很大：

```text
JDK 1.7：
Segment 分段锁

JDK 1.8：
Node数组 + 链表/红黑树
+ CAS + synchronized
```

## **一、先看 JDK 1.7：Segment 分段锁**

JDK 7 的 ConcurrentHashMap 可以粗略理解：

```text
ConcurrentHashMap
        │
        ↓
  Segment[] 数组
        │
 ┌──────┼──────┬──────┐
 ↓      ↓      ↓      ↓
Seg0   Seg1   Seg2   Seg3
 │      │      │      │
Hash   Hash   Hash   Hash
Table  Table  Table  Table
```

每个 `Segment` 管理一部分数据。

而 `Segment` 本身类似：

```java
static final class Segment<K,V>
        extends ReentrantLock {
    ...
}
```

也就是说：

**每一个 Segment 都可以看成一把锁。**

假设两个线程：

```text
线程 A → 修改 Segment 1
线程 B → 修改 Segment 3
```

因为不是同一个 Segment：

```text
线程A ─→ Segment1 🔒

线程B ─→ Segment3 🔒
```

可以同时操作。

只有：

```text
线程A ─┐
       ├→ Segment1
线程B ─┘
```

才会发生锁竞争。

这就是所谓的：

**分段锁 Segment Lock。**

相比于直接给整个 Map 加一把大锁：

```text
          整个 Map 🔒
          ↑       ↑
       线程A     线程B
```

并发度高很多。

---

## **二、JDK 1.8 为什么取消 Segment？**

JDK 8 进一步把锁的粒度降低了。

底层结构和 JDK 8 HashMap 很像：

```text
ConcurrentHashMap

table[]
 │
 ├── [0] null
 │
 ├── [1] Node → Node → Node
 │
 ├── [2] null
 │
 ├── [3] Node → Node
 │
 └── [4] TreeBin
             ↓
           红黑树
```

也就是：

**数组 + 链表 + 红黑树**

但是线程安全机制变成：

**CAS + synchronized + volatile 等并发机制。**

你现在重点学 JDK 8 就行。

---

# **三、JDK 8 ConcurrentHashMap 怎么保证线程安全？⭐⭐⭐⭐⭐**

先记住一句：

**空桶插入主要通过 CAS；桶内已有数据时，主要通过 synchronized 锁住桶头节点进行修改。**

假设：

```text
table

0 → null

1 → A → B

2 → null

3 → C → D → E
```

现在：

```text
线程1 put(X)
线程2 put(Y)
线程3 put(Z)
```

---

## **四、情况一：桶是空的 → CAS**

假设线程 A：

```java
map.put("Java", 100);
```

计算出来：

```text
index = 2
```

发现：

```text
table[2] == null
```

这时候没有必要：

```text
加锁
↓
创建Node
↓
解锁
```

ConcurrentHashMap 会尝试通过 **CAS** 把节点放进去。

概念上：

```text
table[2]

期望值：null
新值：Node(Java,100)

        ↓ CAS

如果table[2]仍然是null
        ↓
    插入成功
```

---

# **五、CAS 是什么意思？**

CAS：

**Compare And Swap，比较并交换。**

可以简单理解：

```text
我认为这个位置现在还是 null
          ↓
实际检查一下
          ↓
    ┌─────┴─────┐
    ↓           ↓
确实null      已被别人修改
    ↓           ↓
写入Node       CAS失败
```

比如线程 A、B 同时发现：

```text
table[2] = null
```

都准备插入：

```text
线程A：
null → Node A

线程B：
null → Node B
```

如果 A 先 CAS 成功：

```text
table[2] → Node A
```

B 再执行 CAS：

```text
期望：null
实际：Node A

      ↓

CAS失败
```

所以不会出现：

```text
A写进去
↓
B直接把A覆盖
```

B 会重新进入相应处理流程。

因此：

**空桶不需要 synchronized，CAS 就能完成安全插入。**

---

# **六、情况二：桶不为空 → synchronized**

假设：

```text
table[3]

   ↓

   A → B → C
```

线程准备往这个桶插入 D。

由于现在要操作已有链表，单纯一个 CAS 就不好处理整个链表修改过程。

所以会：

```java
synchronized (f) {
    // 操作这个桶
}
```

这里 `f` 可以理解成：

当前桶的头节点。

所以：

```text
table[3]
   ↓
  A 🔒 → B → C
```

锁住 A，相当于控制对这个桶结构的并发修改。

---

# **七、是不是把整个 ConcurrentHashMap 锁住？**

**不是。**

这是最重要的地方。

假设：

```text
table

0 → A → B

1 → C → D

2 → E → F

3 → G → H
```

线程 1 修改：

```text
桶0
```

锁：

```text
A 🔒
```

线程 2 修改：

```text
桶3
```

锁：

```text
G 🔒
```

于是：

```text
线程1 → 桶0 🔒
线程2 → 桶3 🔒
```

两个线程可以并行。

只有两个线程同时修改**同一个桶**：

```text
线程1 ─┐
       ↓
       A 🔒 → B → C
       ↑
线程2 ─┘
```

才会发生明显锁竞争。

所以 JDK 8 相比 JDK 7：

```text
JDK 7：

锁粒度 ≈ Segment


JDK 8：

锁粒度进一步细化到桶级别
```

这也是 JDK 8 ConcurrentHashMap 高并发性能的重要原因。

---

# **八、读取 get() 需要加锁吗？**

通常：

**不需要。**

例如：

```java
map.get("Java");
```

不会先：

```java
synchronized (...)
```

再读取。

ConcurrentHashMap 内部通过 `volatile`、安全发布等机制保证必要的可见性。

你现在可以先理解成：

```text
写：

CAS / synchronized
        ↓
安全修改数据


读：

通常不加锁
        ↓
直接读取
```

所以：

**ConcurrentHashMap 不是“所有操作都加 synchronized”。**

如果所有读写都加一把大锁，那并发性能就没那么好了。

---

# **九、把 put() 流程串起来 ⭐⭐⭐⭐⭐**

面试非常重要。

假设：

```java
map.put(key, value);
```

可以先按这个简化流程理解：

```text
              put(key,value)
                     ↓
                计算 hash
                     ↓
              table 是否初始化？
                ↓否      ↓是
              初始化
                     ↓
              找到对应桶位置
                     ↓
                桶是否为空？
              ↙           ↘
            是              否
            ↓               ↓
         CAS插入         判断特殊节点
            ↓               ↓
          成功？        普通链表/树结构
         ↙    ↘              ↓
       是      否        synchronized
       ↓       ↓          锁桶头节点
      完成    重试            ↓
                         再次确认桶没变
                              ↓
                         链表/红黑树
                           插入/更新
                              ↓
                         必要时树化
```

实际源码还涉及初始化、扩容协助、计数等更复杂逻辑，但实习八股先把这个骨架吃透。

---

# **十、ConcurrentHashMap 怎么扩容？**

这也是 JDK 8 很漂亮的设计。

普通 HashMap：

```text
一个执行线程
    ↓
resize
    ↓
迁移所有桶
```

ConcurrentHashMap 支持：

**多个线程协助扩容。**

例如旧数组：

```text
table

0
1
2
3
4
5
6
7
```

线程 A：

```text
迁移 6、7
```

线程 B 发现正在扩容：

```text
我也来帮忙
↓
迁移 4、5
```

线程 C：

```text
迁移 2、3
```

可以粗略理解：

```text
旧 table
┌──────────┐
│ 0  1     │ ← Thread C
│ 2  3     │ ← Thread B
│ 4  5     │ ← Thread A
│ 6  7     │
└──────────┘

多个线程协作
      ↓
   newTable
```

实际任务划分不是简单固定成我这里画的每线程两个桶，这只是帮助你理解。

---

# **十一、扩容时别人来操作这个桶怎么办？**

ConcurrentHashMap 会使用一种特殊节点：

```text
ForwardingNode
```

你可以理解成：

**“这个桶的数据已经搬走了，请去新数组找。”**

例如：

```text
旧table[3]

原来：
A → B → C

迁移以后：

旧table[3]
     ↓
ForwardingNode
     ↓
“数据去 newTable 了”
```

其他线程发现：

```text
hash == MOVED
```

就知道：

正在发生扩容。

写线程可能参与帮助迁移；读取也可以沿相应机制到新表继续查找。

所以它不像：

```text
整个Map扩容
↓
所有线程全部停下来
```

而是设计了并发迁移机制。

---

# **十二、为什么 ConcurrentHashMap 不允许 null？⭐⭐⭐⭐**

这个也是经典追问。

HashMap：

```java
map.put(null, value); // 可以
map.put(key, null);   // 可以
```

ConcurrentHashMap：

```java
map.put(null, value); // ❌
map.put(key, null);   // ❌
```

其中一个重要原因是：

在并发环境下，如果：

```java
V value = map.get(key);
```

返回：

```text
null
```

如果允许存 null，你就难以仅凭这次 `get` 区分：

```text
情况1：
这个 key 不存在

情况2：
这个 key 存在
但是 value == null
```

在普通 Map 中还能结合 `containsKey()`：

```java
map.containsKey(key);
```

但在并发 Map 中：

```text
get(key)
      ↓
另一个线程修改Map
      ↓
containsKey(key)
```

两个操作之间状态可能已经变化。

所以 ConcurrentHashMap 直接规定：

**Key 和 Value 都不能为 null。**

这样：

```text
get(key) == null
```

就可以明确表达当前读取语义下没有对应映射。

---

# **十四、把 HashMap 和 ConcurrentHashMap 对起来**

你现在已经学过 HashMap，所以最好这样记：

```text
                 Map
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
     HashMap        ConcurrentHashMap
        │                   │
   线程不安全             线程安全
        │                   │
 JDK8：数组             JDK8：数组
 +链表+红黑树           +链表+红黑树
                            │
                      ┌─────┴─────┐
                      ↓           ↓
                    空桶         非空桶
                      ↓           ↓
                     CAS      synchronized
                                  ↓
                              锁桶头节点
```

---

## Q：ConcurrentHashMap 是怎么实现线程安全的？

ConcurrentHashMap 在 JDK 7 和 JDK 8 中实现不同。JDK 7 主要采用 Segment 分段锁，每个 Segment 继承 ReentrantLock，不同 Segment 可以并发操作，从而提高并发度。

JDK 8 取消了 Segment，底层采用 Node 数组、链表和红黑树，主要通过 CAS、synchronized 以及 volatile 等机制保证并发安全。put 时，如果目标桶为空，可以通过 CAS 尝试插入；如果桶中已经存在节点，则通常使用 synchronized 锁住桶头节点，再进行链表或者红黑树的修改，因此锁粒度比较细。读取操作通常不需要加锁。

另外 JDK 8 的 ConcurrentHashMap 在扩容时支持多个线程协助迁移，并通过 ForwardingNode 标识已经迁移的桶，从而提高并发扩容效率。


**JDK 7：Segment 分段锁。**  
**JDK 8：CAS + synchronized。**  
**空桶 CAS，非空桶锁桶头。**  
**读通常不加锁，扩容可以多线程协助。**