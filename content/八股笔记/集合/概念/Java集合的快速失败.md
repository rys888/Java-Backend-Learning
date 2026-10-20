
## Q：集合里面的快速失败是什么？

Java 集合中的快速失败机制，是指在使用迭代器遍历集合时，如果检测到集合发生了非预期的结构性修改，就会抛出 `ConcurrentModificationException`。

以 ArrayList 为例，它通过 `modCount` 和 `expectedModCount` 实现。前者记录集合结构性修改的次数，后者记录迭代器预期的修改次数。

在迭代器执行 `next()` 等操作时，会比较这两个值，如果不相等，就说明集合被非预期地修改，从而触发快速失败。

如果需要在遍历过程中删除元素，可以使用 `Iterator.remove()`，它会同步更新 `expectedModCount`。

需要注意，快速失败只是一种尽力检测错误的机制，并不能保证发现所有并发修改，也不能用来保证线程安全。

---

Java 集合中的**快速失败（Fail-Fast）机制**，是指在遍历集合的过程中，如果检测到集合被其他操作进行了不符合迭代器规则的结构性修改，就会尽早抛出 `ConcurrentModificationException`，避免继续在可能不一致的状态下遍历。

它主要存在于 **ArrayList、HashMap、HashSet 等集合的迭代器中**。

## **一、为什么需要快速失败机制？**

假设我们有一个 ArrayList：

```java
List<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.add(3);

for (Integer num : list) {
    if (num == 2) {
        list.remove(num);
    }
}
```

这里的增强 for 循环，底层实际上使用了 `Iterator` 迭代器。

问题在于：

**迭代器正在遍历集合，而我们却直接通过集合的** `remove()` **方法修改了集合结构。**

这可能导致迭代器维护的遍历状态与集合实际状态不一致。

因此，Java 提供了快速失败机制，在检测到不符合规则的结构性修改时抛出：

```java
java.util.ConcurrentModificationException
```

注意：上面这个具体示例不一定抛出异常，因为 ArrayList 的迭代器存在边界情况。快速失败并不是对所有修改都能检测到。

---

## 二、快速失败是怎么实现的？

核心是两个变量：

- **modCount**：集合发生结构性修改的次数。
- **expectedModCount**：迭代器创建时记录的预期修改次数。

以 ArrayList 为例。

### **① 创建迭代器**

```java
Iterator<Integer> iterator = list.iterator();
```

假设此时：

```text
modCount = 3
expectedModCount = 3
```

两个值相同，可以正常遍历。

### **② 集合发生结构性修改**

```java
list.add(4);
```

此时：

```text
modCount = 4
expectedModCount = 3
```

因为直接调用集合的 `add()`，修改了集合结构。

但迭代器内部的 `expectedModCount` 没有同步更新。

### **③ 迭代器继续遍历**

```java
iterator.next();
```

ArrayList 迭代器内部会进行类似下面的检查：

```java
final void checkForComodification() {
    if (modCount != expectedModCount) {
        throw new ConcurrentModificationException();
    }
}
```

由于：

```text
modCount != expectedModCount
```

因此抛出异常。

**快速失败的本质，就是通过比较 modCount 和 expectedModCount，检测集合是否发生了非预期的结构性修改。**

---

## **三、如何避免快速失败？**

### **方法一：使用 Iterator.remove()（推荐）**

如果需要在遍历过程中删除元素，应该使用迭代器自己的 `remove()` 方法。

```java
List<Integer> list = new ArrayList<>(
    Arrays.asList(1, 2, 3, 4)
);

Iterator<Integer> iterator = list.iterator();

while (iterator.hasNext()) {
    Integer num = iterator.next();

    if (num == 2) {
        iterator.remove();
    }
}

System.out.println(list); // [1, 3, 4]
```

为什么不会触发快速失败？

因为 `Iterator.remove()` 删除元素后，会同步更新迭代器的 `expectedModCount`，使其与集合的 `modCount` 保持一致。

### **方法二：使用 removeIf()**

Java 8 提供了更简洁的方式：

```java
list.removeIf(num -> num == 2);
```

适合根据条件批量删除元素。

### **方法三：使用并发集合**

如果涉及多线程并发修改，可以根据场景选择：

- `CopyOnWriteArrayList`：采用快照迭代器，遍历时不受后续修改影响。
- `ConcurrentHashMap`：采用弱一致性迭代器，允许并发修改，不会因为并发结构性修改而抛出 `ConcurrentModificationException`。

但两者的迭代一致性语义不同，不能混为一谈。

---

## **四、快速失败和安全失败有什么区别？**

面试中经常会一起问。

|**对比**|**快速失败（Fail-Fast）**|**常说的安全失败（Fail-Safe）**|
|---|---|---|
|代表集合|ArrayList、HashMap|CopyOnWriteArrayList、ConcurrentHashMap|
|遍历时修改集合|可能抛出异常|通常不会因此抛出异常|
|实现方式|modCount 检测|快照或弱一致性遍历|
|是否保证线程安全|不保证|具体集合支持并发访问|
|遍历结果|检测到修改后中断|可能无法反映全部最新修改|

注意：**Fail-Safe 并不是 Java 集合框架中严格统一的官方迭代器分类。** CopyOnWriteArrayList 的快照迭代和 ConcurrentHashMap 的弱一致性迭代，实际上是两种不同机制。

另外，快速失败也不代表线程安全。即使在单线程中，只要遍历期间直接修改集合，也可能触发异常。

---


