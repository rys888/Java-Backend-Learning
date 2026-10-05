Java 里 `List` 最常见、面试最需要掌握的实现主要是：

**ArrayList、LinkedList、Vector**

实习八股重点是前两个，尤其是 **ArrayList**。

## **1. ArrayList：动态数组 ⭐⭐⭐⭐⭐**

`ArrayList` 底层核心是**数组**。

```java
List<String> list = new ArrayList<>();

list.add("Java");
list.add("MySQL");
list.add("Redis");
```

可以粗略理解为：

```text
底层数组：

下标     0        1        2        3
       ┌──────┬───────┬───────┬──────┐
       │ Java │ MySQL │ Redis │ null │
       └──────┴───────┴───────┴──────┘
```

### **优点：随机访问快**

比如：

```java
list.get(2);
```

数组可以根据下标直接定位：

```text
get(2)
  ↓
数组下标 2
  ↓
Redis
```

时间复杂度：

```text
O(1)
```

所以：

**ArrayList 查询/随机访问很快。**

### **缺点：中间插入删除可能需要移动元素**

假设：

```text
A B C D E
```

要在 B 后面插入 X：

```text
A B _ C D E
    ↑
    X
```

需要把后面的元素移动：

```text
C D E
 ↓ ↓ ↓
向后移动
```

因此中间位置的插入/删除通常是：

```text
O(n)
```

不过注意：**ArrayList 尾部** ** `add()` ** **通常很快，均摊时间复杂度 O(1)**，不能简单背成“ArrayList 增删都慢”。

---

# **2. LinkedList：双向链表 ⭐⭐⭐⭐**

`LinkedList` 底层是：

**双向链表**

大概：

```text
null ← A ⇄ B ⇄ C ⇄ D → null
```

每个节点可以粗略理解为：

```java
class Node {
    Node prev;
    Object item;
    Node next;
}
```

所以一个节点知道：

```text
前一个节点 ← 当前数据 → 后一个节点
```

### **缺点：随机访问慢**

例如：

```java
list.get(3);
```

不像 ArrayList 能直接根据下标找到。

LinkedList 需要沿着链表寻找节点。

所以随机访问：

```text
O(n)
```

### **优势：定位节点后插入删除方便**

假设：

```text
A ⇄ B ⇄ C
```

在 B 和 C 中间插入 X：

```text
A ⇄ B    C
     ↘  ↗
      X
```

主要调整节点之间的引用即可，不需要像数组一样移动大量元素。

但这里有个非常重要的八股陷阱：

**不能直接说“LinkedList 插入删除一定比 ArrayList 快”。**

例如：

```java
list.remove(5000);
```

LinkedList 得先：

```text
寻找第5000个节点
      ↓
     O(n)
      ↓
找到之后修改指针
```

所以如果包含“根据下标查找节点”的过程，整体仍可能是：

```text
O(n)
```

---

# **3. Vector：线程安全的动态数组 ⭐⭐⭐**

`Vector` 和 `ArrayList` 很像：

**底层也是动态数组。**

例如：

```java
List<String> list = new Vector<>();
```

主要区别在于：

Vector 的很多方法带有  `synchronized` 同步机制，因此它是线程安全的；ArrayList 本身不保证线程安全。

可以粗略理解：

```text
ArrayList
   ↓
动态数组
   ↓
线程不安全
   ↓
通常性能更好


Vector
   ↓
动态数组
   ↓
方法级同步
   ↓
线程安全
   ↓
同步存在额外开销
```

`Vector` 属于比较老的集合类，现在实际开发中通常不会因为需要并发安全就直接首选 Vector，而会根据场景考虑：

```java
Collections.synchronizedList(...)
```

或者：

```java
CopyOnWriteArrayList
```

等方案。

---

# **4. CopyOnWriteArrayList ⭐⭐⭐⭐**

如果面试问：

有哪些线程安全的 List？

这个就很重要。

`CopyOnWriteArrayList` 位于：

```java
java.util.concurrent
```

它是线程安全的 List。

核心思想：

**写时复制 Copy-On-Write。**

例如原来：

```text
数组A：

[A B C]
```

线程要增加 D，不是在原数组直接修改，可以粗略理解为：

```text
原数组A：
[A B C]
   ↓
复制
   ↓
新数组B：
[A B C D]
   ↓
让内部引用指向新数组
```

这样读操作通常可以不加传统意义上的读锁。

所以它比较适合：

**读多写少的并发场景。**

但如果频繁写：

```text
add
remove
add
remove
...
```

不断复制数组会带来明显开销。

---

# **5. 最重要：ArrayList vs LinkedList**

这才是 List 八股的核心。

|**特性**|**ArrayList**|**LinkedList**|
|---|---|---|
|底层结构|动态数组|双向链表|
| `get(index)` |**O(1)**|**O(n)**|
|尾部添加|均摊 **O(1)**|**O(1)**|
|中间插入/删除|O(n)，可能移动元素|找到节点 O(n)，修改链接本身 O(1)|
|内存特点|相对紧凑|每个节点还保存前后引用|
|CPU 缓存局部性|通常较好|通常较差|
|线程安全|❌|❌|
|实际使用|⭐⭐⭐⭐⭐ 很常见|相对少|

所以实际开发中：

**没有特殊需求，一般优先考虑 ArrayList。**

不是因为 LinkedList “不好”，而是很多业务场景以遍历、随机访问、尾部添加为主，ArrayList 通常更合适。

---

# **6. 面试标准回答**

如果面试官问：

**Java 中 List 有哪些常见实现？有什么区别？**

你可以回答：

Java 中常见的 List 实现主要有 ArrayList、LinkedList 和 Vector，并发场景下还有 CopyOnWriteArrayList。

ArrayList 底层是动态数组，支持 O(1) 的随机访问，尾部添加的均摊复杂度也是 O(1)，但是在中间插入或删除元素时可能需要移动后续元素。

LinkedList 底层是双向链表，随机访问需要遍历，所以是 O(n)；如果已经定位到节点，插入和删除只需要修改节点之间的引用。

ArrayList 和 LinkedList 本身都不是线程安全的。Vector 底层也是动态数组，但很多方法进行了同步，所以线程安全，不过现在使用相对较少，**当数组已经满时，会创建新的数组，并拷贝原有数组数据**。

并发环境下还有 CopyOnWriteArrayList，它采用写时复制机制，比较适合读多写少的场景。