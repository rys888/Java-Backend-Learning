
**HashMap 本质上是通过** `hashCode` 快速确定 Key 应该存在哪个位置，再通过`equals` 确认 Key 是否相同的 Key-Value 数据结构。

JDK 1.7 和 JDK 1.8 最大区别可以先记：

```text
JDK 1.7：
数组 + 链表

JDK 1.8：
数组 + 链表 + 红黑树
```

---
# **一、先理解 HashMap 到底长什么样**

例如：

```java
Map<String, Integer> map = new HashMap<>();

map.put("Java", 100);
map.put("MySQL", 200);
map.put("Redis", 300);
```

HashMap 不是简单按照：

```text
Java
MySQL
Redis
```

顺序存进去。

它底层首先有一个数组。

JDK 8 可以粗略理解：

```text
table 数组

下标
 0  → null
 1  → Node
 2  → null
 3  → Node
 4  → Node
 5  → null
 ...
15  → null
```

每一个位置通常称为一个：

**桶 Bucket**

一个 Key 放哪个桶，主要由 Key 的 `hashCode()` 经过扰动后，再结合数组长度计算得到。

---
# **二、为什么还需要链表？**

因为可能发生：

**哈希冲突。**

假设：

```text
key A
 ↓
hash计算
 ↓
数组下标 3

key B
 ↓
hash计算
 ↓
数组下标 3
```

A 和 B 是不同的 Key，却落到了同一个桶。

这就是哈希冲突。

所以不能：

```text
table[3] → A

B来了直接把A覆盖掉 ❌
```

需要让它们共存。

JDK 7 使用：

```text
table[3]
   ↓
 Node A
   ↓
 Node B
   ↓
 Node C
```

也就是：

**数组 + 链表解决哈希冲突。**

---
# **三、JDK 1.7 HashMap：数组 + 链表**

JDK 7 底层核心结构可以理解成：

```text
Entry[] table

0 → null

1 → Entry → Entry → Entry

2 → null

3 → Entry → Entry

4 → Entry

5 → null
```

每一个 `Entry` 保存：

```text
Entry

key
value
hash
next
```

可以粗略理解：

```java
class Entry<K,V> {
    K key;
    V value;

    int hash;

    Entry<K,V> next;
}
```

`next` 就是：

指向链表中的下一个 Entry。

---
# **四、JDK 7 的 put 流程**

假设：

```java
map.put("Java", 100);
```

大致经历：

```text
"Java"
   ↓
① 获取 hashCode
   ↓
② 进行 hash 扰动
   ↓
③ 根据 hash 和数组长度计算桶下标
   ↓
④ 找到 table[index]
   ↓
⑤ 判断有没有相同 Key
   ↓
有 → 更新 value

没有 → 插入新 Entry
```

最重要的是前三步。

---
# **五、HashMap 怎么计算数组下标？⭐⭐⭐⭐⭐**

JDK 8 中经典计算方式：

```java
(n - 1) & hash
```

其中：

```text
n = table 数组长度
```

例如：

```text
数组长度 n = 16
```

那么：

```text
index = (16 - 1) & hash
      = 15 & hash
```

为什么可以这么算？

因为 HashMap 数组长度设计成：

**2 的幂。**

例如：

```text
16 = 10000

15 = 01111
```

执行：

```text
hash
&
01111
```

实际上就相当于利用 hash 的低位确定：

```text
0 ~ 15
```

之间的数组下标。

所以 HashMap 经典追问：

为什么 HashMap 的容量通常是 2 的幂？

一个重要原因就是：

**可以通过** ** `(n - 1) & hash` ** **高效计算桶下标，同时有利于让哈希分布更合理。**

---
# **六、为什么还要对 hashCode 进行扰动？**

JDK 8 中有个经典操作：

```java
(h = key.hashCode()) ^ (h >>> 16)
```

也就是：

```text
原始 hashCode

高16位     低16位
 ↓          ↓

      XOR 异或

        ↓

新的 hash
```

为什么？

因为计算数组下标：

```java
(n - 1) & hash
```

如果数组比较小，例如长度 16，那么真正直接参与桶定位的主要是 hash 的低位。

所以把：

```text
高位信息
   ↓
通过 XOR
   ↓
混入低位
```

可以让 hash 的高位也参与桶位置计算，减少一些碰撞情况。

面试简单说：

**HashMap 会对 Key 的 hashCode 进行扰动，让高位信息也参与桶下标计算，从而改善哈希分布。**

够了。

---
# **七、JDK 7 最大的问题：链表可能太长**

例如大量 Key 都落在同一个桶：

```text
table[3]
   ↓
 A
 ↓
 B
 ↓
 C
 ↓
 ...
```

查一个 Key：

```text
A → 不是
↓
B → 不是
↓
C → 不是
↓
D → ...
```

极端情况下：

```text
O(n)
```

HashMap 原本希望：

```text
O(1)
```

结果冲突严重后退化成链表查找。

于是 JDK 8 做了一个重要优化。

---
# **八、JDK 1.8：数组 + 链表 + 红黑树 ⭐⭐⭐⭐⭐**

JDK 8：

```text
table[]
 │
 ├── [0] null
 │
 ├── [1] Node → Node
 │
 ├── [2] null
 │
 ├── [3] Node → Node → Node
 │
 └── [4]
       ↓
     红黑树
```

所以：

**JDK 8 在数组 + 链表基础上增加了红黑树。**

当某个桶中的链表过长，并满足条件后：

```text
链表
 ↓
红黑树
```

从而提高冲突严重情况下的查询效率。

---
# **九、什么时候链表变红黑树？⭐⭐⭐⭐⭐**

两个条件必须重点背：

```text
链表节点数量达到 8
+
数组容量 >= 64
```

也就是：

```java
TREEIFY_THRESHOLD = 8
MIN_TREEIFY_CAPACITY = 64
```

如果：

```text
链表已经达到 8

但是：

table.length < 64
```

HashMap 通常不会马上树化，而是：

**优先扩容。**

因为数组太小时出现长链表，有可能只是：

桶数量太少。

扩容后重新分布，可能自然就把冲突缓解了。

所以：

```text
链表长度达到 8
        ↓
table.length >= 64？
     ↙        ↘
   否          是
   ↓           ↓
优先扩容      树化
              ↓
           红黑树
```

这张逻辑图建议你背下来。

---
# **十、为什么是红黑树？**

普通链表查询：

```text
O(n)
```

红黑树查询：

```text
O(log n)
```

所以哈希冲突非常严重时：

```text
链表
O(n)

 ↓ 树化

红黑树
O(log n)
```

提高最坏情况下的查找性能。

---
# **十一、JDK 8 的 put() 流程 ⭐⭐⭐⭐⭐**

这个是 HashMap 最核心的八股。

假设：

```java
map.put(key, value);
```

你可以按照下面理解：

```text
                put(key,value)
                       ↓
                 计算 key 的 hash
                       ↓
                 table 是否为空？
                  ↓是        ↓否
                 初始化
                       ↓
          根据 (n-1)&hash 找桶位置
                       ↓
                 桶是否为空？
                ↙           ↘
              是              否
              ↓               ↓
         直接创建Node      发生hash冲突
                              ↓
                      判断Key是否相同
                         ↙         ↘
                       是           否
                       ↓            ↓
                   覆盖value     判断桶结构
                                   ↓
                          ┌────────┴────────┐
                          ↓                 ↓
                        链表              红黑树
                          ↓                 ↓
                      遍历/插入          树中插入
                          ↓
                     链表过长？
                          ↓
                   满足条件则树化
                          ↓
                      size++
                          ↓
                 超过扩容阈值？
                    ↙        ↘
                  是          否
                  ↓
                resize       完成
```

这个流程非常值得你记。

---
# **十二、HashMap 怎么判断两个 Key 是不是同一个？**

这里就和你之前学的 `hashCode()` + `equals()` 完全串起来了。

大致判断逻辑：

```text
先比较 hash
     ↓
hash 相同
     ↓
再判断：
key1 == key2
或者
key1.equals(key2)
```

所以：

```text
hashCode
   ↓
快速定位桶

equals
   ↓
最终确认是不是同一个逻辑 Key
```

这就是为什么：

**重写 equals() 通常必须同时重写 hashCode()。**

否则：

```text
equals认为两个Key相同

但是：

hashCode不同
 ↓
可能进入不同桶
 ↓
HashMap行为异常
```

你之前学的 `equals/hashCode` 到这里才真正串起来。

---
# **十三、HashMap 的扩容机制 ⭐⭐⭐⭐⭐**

假设默认：

```text
capacity = 16
```

默认负载因子：

```text
loadFactor = 0.75
```

扩容阈值：

```text
threshold
=capacity × loadFactor
=16 × 0.75
=12
```

也就是说，当元素数量超过相应阈值后，会触发扩容。

一般：

```text
16 → 32 → 64 → 128
```

也就是：

**容量通常扩大为原来的 2 倍。**

注意和你刚学的 ArrayList 区分：

```text
ArrayList：
大约 1.5 倍

HashMap：
通常 2 倍
```

---
# **十四、为什么负载因子默认 0.75？**

这也是经典八股。

如果负载因子太小，例如：

```text
0.1
```

数组：

```text
只用了很少
 ↓
就开始扩容
 ↓
空间浪费严重
```

如果负载因子太大，例如：

```text
1.0
```

数组非常满：

```text
大量 Key
 ↓
更容易发生哈希冲突
 ↓
链表/树变多
 ↓
查询性能受到影响
```

所以：

```text
空间利用率 ←──── 0.75 ────→ 哈希冲突概率
```

`0.75` 是一个比较合理的：

**时间和空间之间的折中。**

---
# **十五、JDK 8 扩容还有一个很巧妙的优化**

假设旧数组容量：

```text
oldCap = 16
```

扩容：

```text
newCap = 32
```

JDK 8 不需要像一些旧实现思路那样重新完整计算每个元素的桶位置。

一个节点扩容后的新位置通常只有两种：

```text
① 原来的位置

或者

② 原位置 + oldCap
```

例如：

```text
原来 index = 5

扩容后：

可能还是 5

或者：

5 + 16 = 21
```

判断主要利用：

```java
e.hash & oldCap
```

所以：

```text
扩容 16 → 32

原桶 index = 5

        ↓

      节点
     ↙    ↘
hash & 16
= 0       != 0
 ↓          ↓
仍然5       21
```

这是 JDK 8 HashMap 扩容机制里非常经典的优化。

---
# **十六、JDK 7 和 JDK 8 插入链表方式也有区别**

这个八股也经常出现。

### **JDK 7：头插法**

新节点插到链表头部：

```text
原来：

A → B → C

加入 X：

X → A → B → C
```

### **JDK 8：尾插法**

新节点通常加到链表尾部：

```text
原来：

A → B → C

加入 X：

A → B → C → X
```

为什么这个区别经常被问？

因为 JDK 7 在多线程并发扩容情况下，头插等实现细节曾可能导致链表形成环，从而出现严重问题。

JDK 8 调整了相关实现。

但一定注意：

**JDK 8 的 HashMap 仍然不是线程安全的。**

不能说：

“改成尾插以后 HashMap 就线程安全了。” ❌

并发场景通常应该考虑：

```java
ConcurrentHashMap
```

---
# **十七、JDK 7 vs JDK 8 汇总**

|**对比**|**JDK 7**|**JDK 8**|
|---|---|---|
|数据结构|数组 + 链表|数组 + 链表 + 红黑树|
|节点| `Entry` | `Node` / `TreeNode` |
|链表插入|头插|尾插|
|长链表查询|O(n)|树化后 O(log n)|
|树化|❌|✅|
|树化阈值|无|8|
|树化最小数组容量|无|64|
|扩容|通常 2 倍|通常 2 倍|
|线程安全|❌|❌|

---
# **十八、HashMap 为什么线程不安全？**

和 ArrayList 一样：

```text
多个线程
   ↓
同时 put()
   ↓
同时修改
table / 节点 / size / 扩容状态
   ↓
产生竞争
```

JDK 7 尤其著名的问题是并发扩容时可能出现链表结构异常。

JDK 8 虽然修改了很多实现：

```text
红黑树
尾插
新的 resize 逻辑
```

但是：

**HashMap 依然没有提供完整的并发同步保证。**

所以：

```text
单线程/无共享并发修改
        ↓
     HashMap

并发访问并修改
        ↓
ConcurrentHashMap
```

---
# **十九、面试怎么回答“HashMap 的实现原理？”**

不要一上来讲十分钟。先用这一分钟版本：

HashMap 是基于哈希表实现的 Key-Value 数据结构。它会先获取 Key 的 hashCode，并经过扰动计算得到 hash，再通过 `(n - 1) & hash` 确定元素所在的桶位置。如果发生哈希冲突，会在同一个桶中进一步处理，并通过 hash 和 equals 判断 Key 是否相同。

JDK 1.7 中 HashMap 的底层结构主要是**数组加链表**；JDK 1.8 在此基础上增加了**红黑树**。当某个桶中的链表节点达到树化阈值，并且数组容量至少为 64 时，可以转换为红黑树，将严重哈希冲突情况下的查询复杂度从 O(n) 优化到 O(log n)。

HashMap 默认负载因子是 0.75，容量不足时通常扩容为原来的 2 倍。JDK 8 扩容时，节点的新位置可以根据 hash 判断为原位置或者 `原位置 + oldCap`。

另外 HashMap 本身不是线程安全的，并发场景下一般使用 ConcurrentHashMap。