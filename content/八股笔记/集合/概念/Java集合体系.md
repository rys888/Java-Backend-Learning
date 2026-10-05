
# **一、Java 中的集合是什么？**

Java 集合框架主要用于：

**存储和操作一组对象。**

最重要的是先把集合体系记住：

```text
Java 集合框架
│
├── Collection
│     │
│     ├── List
│     │    ├── ArrayList
│     │    └── LinkedList
│     │
│     ├── Set
│     │    ├── HashSet
│     │    ├── LinkedHashSet
│     │    └── TreeSet
│     │
│     └── Queue
│          ├── PriorityQueue
│          └── Deque
│               └── ArrayDeque
│
└── Map
      ├── HashMap
      ├── LinkedHashMap
      ├── TreeMap
      ├── Hashtable
      └── ConcurrentHashMap
```

这里一定注意：

**Map 不属于 Collection。**

Collection 和 Map 是 Java 集合框架中两条重要的体系。

---

# **二、List：有序、可重复**

List 最大特点：

**元素有顺序，可以重复，可以通过索引访问。**

例如：

```java
List<String> list = new ArrayList<>();

list.add("张三");
list.add("李四");
list.add("张三");
```

结果：

```text
0 → 张三
1 → 李四
2 → 张三
```

两个 `"张三"` 可以同时存在。

最重要的两个实现：

```text
List
├── ArrayList
└── LinkedList
```

### **ArrayList ⭐⭐⭐⭐⭐**

底层：

**动态数组。**

特点：

```text
查询快
随机访问快
尾部添加通常快
中间插入/删除可能需要移动元素
```

例如：

```java
list.get(100);
```

可以直接根据索引定位。

这是实际开发中非常常用的 List 实现。

---

### **LinkedList ⭐⭐⭐**

底层：

**双向链表。**

可以理解：

```text
null ← A ⇄ B ⇄ C ⇄ D → null
```

每个节点记录前后节点。

所以：

随机访问需要遍历；在已经定位到节点的情况下，链表结构的插入删除不需要像数组那样整体移动后续元素。

注意不要简单背：

“LinkedList 删除一定比 ArrayList 快。”

因为如果需要先根据索引找到那个元素，LinkedList 本身还需要遍历。

---

# **四、Set：不允许重复**

Set 最大特点：

**不允许保存重复元素。**

例如：

```java
Set<String> set = new HashSet<>();

set.add("张三");
set.add("李四");
set.add("张三");
```

最终只有：

```text
张三
李四
```

最重要：

```text
Set
├── HashSet
├── LinkedHashSet
└── TreeSet
```

### **HashSet ⭐⭐⭐⭐⭐**

底层主要依赖：

**HashMap。**

例如：

```java
Set<User> set = new HashSet<>();
```

判断元素是否重复会涉及：

```text
hashCode()
    ↓
定位
    ↓
equals()
    ↓
判断是否相等
```

所以前面刚学过的：

**为什么重写 equals 通常必须重写 hashCode？**
[[hashcode和equals方法关系]]

在这里就串起来了。

---

### **LinkedHashSet**

特点：

在 HashSet 的基础上维护元素的插入顺序。

---

### **TreeSet**

特点：

可以按照自然顺序或者 Comparator 规则进行排序。

底层基于：

**TreeMap / 红黑树。**

---

# **五、Queue：队列**

Queue 主要用于：

**按照一定规则处理等待中的元素。**

最经典的是：

```text
先进先出 FIFO

进入：
A → B → C →

出去：
A
↓
B
↓
C
```

常见：

```java
Queue<String> queue = new LinkedList<>();

queue.offer("A");
queue.offer("B");

queue.poll();
```

还有：

```java
PriorityQueue
```

优先队列，并不是简单按照插入顺序出队，而是根据优先级规则处理元素。

以及常见的：

```java
Deque
```

双端队列，可以两端添加和删除。

---

# **六、Map：Key-Value**

Map 和前面不同：

**Map 保存的是 Key-Value 键值对。**

例如：

```java
Map<Integer, String> map = new HashMap<>();

map.put(1, "张三");
map.put(2, "李四");
```

结构：

```text
Key       Value

1    →    张三
2    →    李四
```

Key 不能重复。

如果：

```java
map.put(1, "王五");
```

原来的：

```text
1 → 张三
```

会被替换为：

```text
1 → 王五
```

---

# **七、HashMap ⭐⭐⭐⭐⭐**

这是整个 Java 集合八股里**最重要的一个类**。

Java 8 中可以先记成：

**数组 + 链表 + 红黑树。**

大致：

```text
HashMap

table 数组
 │
 ├── [0]
 │
 ├── [1] → Node → Node
 │
 ├── [2]
 │
 ├── [3] → Node → Node → Node
 │
 └── [4]
```

哈希冲突严重、满足相应条件时：

```text
链表
 ↓
红黑树
```

实习面试特别喜欢追：

```text
HashMap底层结构？
        ↓
put流程？
        ↓
怎么确定数组下标？
        ↓
什么是哈希冲突？
        ↓
为什么用链表？
        ↓
为什么Java 8引入红黑树？
        ↓
什么时候树化？
        ↓
为什么容量通常是2的幂？
        ↓
什么时候扩容？
        ↓
负载因子为什么默认0.75？
        ↓
HashMap线程安全吗？
        ↓
ConcurrentHashMap怎么实现线程安全？
```

---

# **八、你准备八股时应该重点掌握哪些？**

不用平均学习所有集合。

按照 Java 后端实习优先级，我建议：

**第一梯队 ⭐⭐⭐⭐⭐：**

```text
ArrayList
HashMap
ConcurrentHashMap
HashSet
```

**第二梯队 ⭐⭐⭐⭐：**

```text
LinkedList
TreeMap
ArrayDeque
PriorityQueue
```

**第三梯队 ⭐⭐⭐：**

```text
TreeSet
LinkedHashMap
LinkedHashSet
Hashtable
Vector
```

尤其是：

**ArrayList + HashMap + ConcurrentHashMap**

这三个建议深入到底层实现。

---

## **面试：“介绍一下 Java 集合？”**

可以这样回答：

Java 集合框架主要用于存储和操作一组对象，主要可以分为 Collection 和 Map 两大体系。

Collection 下面主要包括 List、Set 和 Queue。List 中的元素有序并且可以重复，常见实现有 ArrayList 和 LinkedList；Set 不允许元素重复，常见实现有 HashSet、TreeSet；Queue 主要用于队列场景。

Map 不属于 Collection，它用于保存 Key-Value 键值对，常见实现包括 HashMap、TreeMap、LinkedHashMap 和 ConcurrentHashMap。

实际开发中比较常见的是 ArrayList、HashMap、HashSet 和 ConcurrentHashMap，其中 HashMap 和 ConcurrentHashMap 也是 Java 集合相关面试的重点。