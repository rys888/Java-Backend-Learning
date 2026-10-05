
`List` 和 `Set` 都属于 Java `Collection` 体系，最核心的区别就两点：

**List：有序、可重复。**  
**Set：不允许重复，通常不能通过下标访问。**

具体看：

|**对比**|**List**|**Set**|
|---|---|---|
|元素是否可重复|✅ 可以|❌ 不可以|
|是否有索引|✅ 有|❌ 没有|
|能否 `get(index)` |✅ 可以|❌ 不可以|
|顺序|按 List 中的位置保存|取决于具体实现|
|常见实现|ArrayList、LinkedList|HashSet、LinkedHashSet、TreeSet|

比如 `List`：

```java
List<String> list = new ArrayList<>();

list.add("Java");
list.add("MySQL");
list.add("Java");

System.out.println(list);
```

可以保存重复元素：

```text
[Java, MySQL, Java]
```

并且可以：

```java
list.get(0); // Java
list.get(2); // Java
```

而 `Set`：

```java
Set<String> set = new HashSet<>();

set.add("Java");
set.add("MySQL");
set.add("Java");

System.out.println(set);
```

最终只有两个元素，因为：

```text
"Java" 重复了
      ↓
Set 不允许重复
      ↓
不会再次加入
```

### **Set 怎么判断重复？⭐⭐⭐⭐⭐**

这个是面试很容易顺着问的。

以 `HashSet` 为例，它底层基于 `HashMap`，判断元素是否重复会涉及：

```text
元素
 ↓
hashCode()
 ↓
确定可能的位置
 ↓
equals()
 ↓
进一步判断是否相等
```

这就和你前面学的 `equals()`、`hashCode()` 串起来了。

例如两个 `User`：

```java
User u1 = new User(1, "张三");
User u2 = new User(1, "张三");
```

如果业务上希望：

```text
id 和 name 相同
→ 就认为是同一个 User
→ HashSet 中不能重复
```

那么通常就需要正确重写：

```java
equals()
hashCode()
```

### **Set 也不是简单的“无序”**

这里八股要说准确一点。

不同 Set 实现不同：

```text
HashSet
→ 不保证元素的迭代顺序

LinkedHashSet
→ 维护插入顺序

TreeSet
→ 根据自然顺序或 Comparator 排序
```

所以不要直接死记：

Set = 无序 ❌

更准确：

**Set 的核心特征是不允许重复；具体是否维护某种顺序取决于实现类。**

### Q：**List 和 Set 有什么区别？**

List 和 Set 都属于 Collection 体系。List 中的元素可以重复，并且元素具有位置顺序，可以通过索引访问，常见实现有 ArrayList 和 LinkedList。Set 的核心特点是不允许重复元素，也不能通过索引访问，常见实现有 HashSet、LinkedHashSet 和 TreeSet。其中 HashSet 不保证迭代顺序，LinkedHashSet 可以维护插入顺序，而 TreeSet 可以进行排序。