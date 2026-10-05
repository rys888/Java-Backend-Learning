ArrayList 的扩容机制是集合八股里的**高频题**。

**ArrayList 底层是动态数组，当数组空间不够时，会创建一个更大的新数组，通常扩容为原容量的 1.5 倍，再把旧数组的数据复制过去。**

下面以常见的 **JDK 8**  `ArrayList` 实现思路来讲。

以下是示意图：

![[Pasted image 20261004172802.png]]

### **1. ArrayList 底层是什么？**

核心就是一个数组：

```java
transient Object[] elementData;
```

比如：

```java
List<String> list = new ArrayList<>();
```

可以理解成：

```text
ArrayList
   ↓
elementData
   ↓
Object[]
```

真正的数据都是存在 `elementData` 中。

### **2. 默认容量是多少？**

这是一个容易答错的地方。

```java
new ArrayList<>();
```

**刚创建时，并不是马上创建长度为 10 的数组。**

JDK 8 中采用了**懒加载**思想：

```text
new ArrayList<>()
      ↓
底层先使用空数组
      ↓
第一次 add()
      ↓
真正分配容量
      ↓
默认容量 10
```

所以更准确的说法是：

**无参构造的 ArrayList 初始底层数组为空，第一次添加元素时容量扩展为默认的 10。**

例如：

```java
List<Integer> list = new ArrayList<>();

list.add(1);
```

第一次 `add()` 后，可以粗略理解：

```text
size = 1

elementData：

[1][ ][ ][ ][ ][ ][ ][ ][ ][ ]
 ↑
容量 capacity = 10
```

注意两个概念：

```text
size = 实际存了多少元素
capacity = 底层数组能装多少元素
```

比如：

```text
size = 3
capacity = 10

[A][B][C][ ][ ][ ][ ][ ][ ][ ]
```

---

### **3. 什么时候扩容？**

不断：

```java
list.add(...)
```

直到：

```text
capacity = 10
size = 10

[A][B][C][D][E][F][G][H][I][J]
```

现在再添加第 11 个：

```java
list.add("K");
```

发现：

```text
当前需要的最小容量 = 11
当前数组容量 = 10

11 > 10
```

空间不够，于是触发扩容。

---

### **4. 扩容多少？⭐⭐⭐⭐⭐**

JDK 8 中核心计算可以简化理解为：

```java
int oldCapacity = elementData.length;

int newCapacity =
        oldCapacity + (oldCapacity >> 1);
```

重点就是：

```java
oldCapacity >> 1
```

相当于大约：

```text
oldCapacity / 2
```

因此：

```text
newCapacity
= oldCapacity + oldCapacity / 2
≈ oldCapacity × 1.5
```

例如原来：

```text
10
```

扩容：

```text
10 + 10 / 2
= 15
```

所以：

```text
10 → 15
```

下一次：

```text
15 + 15 / 2
= 22
```

注意整数运算：

```text
15 / 2 = 7

所以：

15 → 22
```

再下一次：

```text
22 → 33
```

因此大致：

```text
10 → 15 → 22 → 33 → 49 → ...
```

所以面试里通常说：

**ArrayList 每次扩容大约扩为原来的 1.5 倍。**

---

### **5. 扩容不是把原数组“拉长”**

数组创建后：

```java
Object[10]
```

长度是不能改变的。

所以所谓“扩容”实际上是：

```text
旧数组 capacity = 10

[A][B][C][D][E][F][G][H][I][J]

              ↓

创建一个新数组 capacity = 15

[ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]

              ↓

复制旧数组元素

[A][B][C][D][E][F][G][H][I][J][ ][ ][ ][ ][ ]

              ↓

elementData 指向新数组
```

源码层面最终会涉及类似：

```java
Arrays.copyOf(elementData, newCapacity);
```

所以：

**ArrayList 扩容本质 = 创建更大的数组 + 复制旧数据 + 替换数组引用。**

这也是为什么扩容有性能开销。

---

### **6. 为什么不是每次只增加 1？**

假设每次空间不够只增加一个：

```text
10 → 11 → 12 → 13 → 14 → 15...
```

那么不断 `add()`：

```text
创建新数组
复制

创建新数组
复制

创建新数组
复制
...
```

成本很高。

所以 ArrayList 会一次多申请一些空间：

```text
10 → 15 → 22 → 33...
```

用一部分额外空间换取：

**减少扩容和数组复制次数。**

---

### **7. 如果一开始就知道要存很多数据呢？**

比如你明确知道：

我要存 100 万条数据。

如果：

```java
List<User> users = new ArrayList<>();
```

中间会经历多次扩容。

可以直接：

```java
List<User> users = new ArrayList<>(1_000_000);
```

预先指定容量。

这样可以减少：

```text
扩容
+
数组复制
```

带来的开销。

---

## Q：ArrayList 的扩容机制说一下？

ArrayList 底层是 Object 数组。以 JDK 8 为例，通过无参构造创建 ArrayList 时，底层一开始是空数组，在第一次添加元素时会分配默认容量 10。

当添加元素发现当前数组容量不足时，就会触发扩容。新的容量通常按照 `oldCapacity + oldCapacity / 2` 计算，也就是原容量的约 1.5 倍。

扩容之后会创建一个新的、更大的数组，并通过数组复制把原来的元素复制到新数组中，最后让 `elementData` 指向新数组。因此扩容本身存在一定的性能开销，如果提前知道数据量，可以通过构造方法指定初始容量来减少扩容次数。

最后记这一条链就够了：

```text
ArrayList
   ↓
底层 Object[]
   ↓
无参创建：先空数组
   ↓
第一次 add
   ↓
默认容量 10
   ↓
容量不足
   ↓
扩容约 1.5 倍
   ↓
创建新数组
   ↓
复制旧元素
   ↓
elementData 指向新数组
```

这已经是 Java 后端实习面试里比较完整的回答了。