
Java 集合框架（Java Collections Framework，JCF）主要分为 **Collection 和 Map 两大体系**。

它们最核心的区别是：

- **Collection：存储单个元素**，例如 List、Set、Queue。
- **Map：存储键值对（Key-Value）**，例如 HashMap、TreeMap、ConcurrentHashMap。

注意：**Map 不继承 Collection，它们是两套独立的接口体系。**

## **一、Java 集合框架整体结构 ⭐⭐⭐⭐⭐**

```text
Java 集合框架
│
├── Collection 接口
│   │
│   ├── List 接口（有序、可重复）
│   │   ├── ArrayList
│   │   ├── LinkedList
│   │   └── Vector
│   │       └── Stack
│   │
│   ├── Set 接口（元素不重复）
│   │   ├── HashSet
│   │   │   └── LinkedHashSet
│   │   └── SortedSet
│   │       └── NavigableSet
│   │           └── TreeSet
│   │
│   └── Queue 接口（队列）
│       ├── PriorityQueue
│       └── Deque 接口（双端队列）
│           ├── ArrayDeque
│           └── LinkedList
│
└── Map 接口
    │
    ├── HashMap
    │   └── LinkedHashMap
    │
    ├── Hashtable
    │
    ├── SortedMap
    │   └── NavigableMap
    │       └── TreeMap
    │
    └── ConcurrentMap
        └── ConcurrentHashMap
```

这里展示的是主要接口和实现类，并非完整继承图。例如 `LinkedList` 同时实现了 `List` 和 `Deque`，`LinkedHashSet` 继承 `HashSet`。

---

## **二、Collection 体系**

Collection 用于存储一组独立元素，主要包含三个子接口：**List、Set、Queue**。

### **1. List：有序、可重复**

List 的特点：

- 元素按照插入位置保持顺序。
- 允许重复元素。
- 可以通过索引访问元素。

例如：

```java
List<String> list = new ArrayList<>();

list.add("Java");
list.add("Redis");
list.add("Java");

System.out.println(list);
// [Java, Redis, Java]
```

常见实现类：

|**实现类**|**底层结构**|**特点**|
|---|---|---|
|ArrayList|动态数组|随机访问快，尾部添加通常较快|
|LinkedList|双向链表|已定位节点后的插入删除较方便|
|Vector|动态数组|方法大多使用 synchronized，属于较老的实现|

**面试重点：ArrayList 和 LinkedList 的区别。**

ArrayList 根据索引访问的时间复杂度为 O(1)，而 LinkedList 根据索引访问通常为 O(n)。

但不要简单认为 LinkedList 的插入删除一定比 ArrayList 快，因为 LinkedList 查找插入位置也需要时间。

### **2. Set：元素不重复**

Set 的核心特点是**不允许重复元素**。

```java
Set<String> set = new HashSet<>();

set.add("Java");
set.add("Redis");
set.add("Java");

System.out.println(set.size()); // 2
```

常见实现类：

|**实现类**|**底层结构**|**特点**|
|---|---|---|
|HashSet|HashMap|不保证遍历顺序，查找通常为 O(1)|
|LinkedHashSet|LinkedHashMap|按插入顺序遍历|
|TreeSet|红黑树|按自然顺序或比较器排序|

这里有一个重要知识点：

**HashSet 底层实际上使用 HashMap 存储元素。**

HashSet 将元素作为 HashMap 的 Key，使用一个固定对象作为 Value。

因此，HashSet 判断元素是否重复，依赖 `hashCode()` 和 `equals()`。

### **3. Queue：队列**

Queue 主要用于按照一定规则处理元素。

常见实现类：

- `PriorityQueue`：优先队列，底层使用堆，按优先级出队。
- `ArrayDeque`：基于可扩容数组实现的双端队列。
- `LinkedList`：也实现了 Deque 接口。

例如：

```java
Queue<Integer> queue = new ArrayDeque<>();

queue.offer(10);
queue.offer(20);

System.out.println(queue.poll()); // 10
```

普通 FIFO 队列遵循先进先出，但 PriorityQueue 不按照插入顺序出队。

---

## **三、Map 体系 ⭐⭐⭐⭐⭐**

Map 与 Collection 不同，它存储的是 **Key-Value 键值对**。

例如：

```java
Map<Integer, String> map = new HashMap<>();

map.put(1001, "张三");
map.put(1002, "李四");

System.out.println(map.get(1001)); // 张三
```

Map 有两个重要特点：

**① Key 不允许重复**

```java
map.put(1001, "张三");
map.put(1001, "王五");
```

第二次 `put()` 会覆盖第一个 Key 对应的 Value。

**② Value 可以重复**

```java
map.put(1001, "张三");
map.put(1002, "张三");
```

这是允许的。

### **Map 常见实现类**

|**实现类**|**底层结构**|**特点**|
|---|---|---|
|HashMap|数组 + 链表 + 红黑树（JDK 8）|无序，非线程安全|
|LinkedHashMap|HashMap + 双向链表|可维护插入顺序或访问顺序|
|TreeMap|红黑树|根据 Key 排序|
|Hashtable|哈希表|方法大多同步，较老的线程安全实现|
|ConcurrentHashMap|哈希表及并发控制机制|支持高并发访问|

其中最重要的是 **HashMap 和 ConcurrentHashMap**。

#### **HashMap 的底层结构**

以 JDK 8 为例：

```text
HashMap
   │
   ▼
Node 数组
   │
   ├── bucket[0] → Node → Node
   │
   ├── bucket[1] → Node
   │
   ├── bucket[2] → 红黑树
   │
   └── bucket[3] → null
```

HashMap 首先根据 Key 的哈希值定位数组下标。

如果发生哈希冲突，多个元素可能存储在同一个桶中。

JDK 8 中，当链表长度达到树化条件，且数组容量达到 64 时，链表可以转换为红黑树，以提高严重哈希冲突情况下的查询效率。

---

## **四、Collection 和 Map 的核心区别**

这是面试最需要掌握的部分。

|**对比维度**|**Collection**|**Map**|
|---|---|---|
|存储内容|单个元素|Key-Value 键值对|
|顶层接口|Collection|Map|
|主要子接口|List、Set、Queue|SortedMap、ConcurrentMap 等|
|是否允许重复|取决于具体实现|Key 不重复，Value 可重复|
|访问方式|索引、迭代器等|通过 Key 查找 Value|
|常见实现|ArrayList、HashSet、ArrayDeque|HashMap、TreeMap、ConcurrentHashMap|
|典型场景|用户列表、去重集合、任务队列|用户 ID 与用户信息的映射|

### **一个例子理解**

假设开发一个用户管理系统。

**场景一：存储所有用户**

```java
List<User> users = new ArrayList<>();
```

因为需要保存一组用户对象。

**场景二：用户去重**

```java
Set<Long> userIds = new HashSet<>();
```

因为不希望出现重复的用户 ID。

**场景三：根据用户 ID 查询用户**

```java
Map<Long, User> userMap = new HashMap<>();
```

例如：

```java
User user = userMap.get(1001L);
```

可以根据用户 ID 快速获取对应的用户对象。

这就是 Collection 和 Map 在实际开发中的不同用途。

---

## **五、Collection 和 Collections 有什么区别？**

这也是面试官很喜欢追问的问题。

注意区分：

**Collection 是接口，Collections 是工具类。**

Collection：

```java
Collection<String> collection = new ArrayList<>();
```

Collections：

```java
List<Integer> list = new ArrayList<>(
    Arrays.asList(3, 1, 2)
);

Collections.sort(list);

System.out.println(list);
// [1, 2, 3]
```

`Collections` 提供了排序、反转、查找、包装集合等静态工具方法。

例如：

```java
Collections.sort(list);
Collections.reverse(list);
Collections.synchronizedList(list);
```

---

## **六、面试怎么回答？⭐⭐⭐⭐⭐**

Java 集合框架主要分为 Collection 和 Map 两大体系，它们是相互独立的接口。

Collection 用于存储单个元素，主要包括 List、Set 和 Queue。

List 的特点是有序、可重复，常见实现有 ArrayList 和 LinkedList；Set 不允许重复元素，常见实现有 HashSet、LinkedHashSet 和 TreeSet；Queue 主要用于队列场景，常见实现有 PriorityQueue 和 ArrayDeque。

Map 则用于存储 Key-Value 键值对，其中 Key 不允许重复，Value 可以重复。常见实现包括 HashMap、LinkedHashMap、TreeMap 和 ConcurrentHashMap。

从底层实现来看，ArrayList 使用动态数组，LinkedList 使用双向链表，HashMap 在 JDK 8 中使用数组、链表和红黑树，TreeMap 使用红黑树。

在实际开发中，如果需要存储一组对象，可以选择 List；如果需要去重，可以选择 Set；如果需要根据 Key 快速查找 Value，可以选择 Map。

### **最后总结**

**Java 集合框架可以记成两条主线：**

```text
Collection：存储单个元素
    │
    ├── List  → 有序、可重复
    ├── Set   → 不重复
    └── Queue → 队列

Map：存储 Key-Value
    │
    ├── HashMap           → 普通键值映射
    ├── LinkedHashMap     → 有序遍历
    ├── TreeMap           → Key 排序
    └── ConcurrentHashMap → 并发访问
```

**面试中最重要的四个集合是：ArrayList、HashSet、HashMap、ConcurrentHashMap。**