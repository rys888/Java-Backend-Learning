
对 `Set` 排序，最常见的方式有两种：

使用 `TreeSet` 自动排序，或者把 Set 转成 List 后再排序。
### **1. 使用 TreeSet**

例如原来：

```java
Set<Integer> set = new HashSet<>();

set.add(5);
set.add(2);
set.add(8);
set.add(1);
```

`HashSet` 本身不保证排序。

转换成 `TreeSet`：

```java
Set<Integer> sortedSet = new TreeSet<>(set);

System.out.println(sortedSet);
```

结果：

```text
[1, 2, 5, 8]
```

`TreeSet` 默认按照元素的**自然顺序**排序。

比如 `String`：

```java
Set<String> set = new TreeSet<>();

set.add("Java");
set.add("Apple");
set.add("Redis");

System.out.println(set);
```

会按照字符串的自然顺序排列。

### **2. 自定义排序规则**

比如希望数字**从大到小**：

```java
Set<Integer> set = new TreeSet<>((a, b) -> b - a);

set.add(5);
set.add(2);
set.add(8);
set.add(1);
```

`(a, b) -> b - a` 是什么

这是**自定义比较器 Comparator**

- `a - b`：升序（小在前，大在后，默认 TreeSet 规则）
- `b - a`：**降序**（大在前，小在后）

得到：

```text
[8, 5, 2, 1]
```

更推荐写：

```java
Set<Integer> set =
        new TreeSet<>(Comparator.reverseOrder());
```

这里使用的就是 `Comparator`。

如果是对象：

```java
class User {
    private String name;
    private int age;
}
```

按照年龄排序：

```java
Set<User> set =
    new TreeSet<>(Comparator.comparingInt(User::getAge));
```

这里就把你前面学的东西串起来了：

```text
TreeSet
   ↓
Comparator
   ↓
Lambda / 方法引用
```

### **3. Set 转 List 再排序**

如果只是想**把 Set 中的数据拿出来排序**，但并不需要一个始终有序的 Set，可以：

```java
Set<Integer> set = new HashSet<>();
set.add(5);
set.add(2);
set.add(8);

List<Integer> list = new ArrayList<>(set);

Collections.sort(list);
```

结果：

```text
[2, 5, 8]
```

Java 8 也可以：

```java
List<Integer> list = set.stream()
        .sorted()
        .collect(Collectors.toList());
```

---

## Q： **“如何对 Set 排序？”**

HashSet 本身不提供排序保证。如果希望集合中的元素按照一定规则维护顺序，可以使用 TreeSet。TreeSet 可以按照元素的自然顺序排序，也可以传入 Comparator 自定义排序规则。如果只是临时需要排序结果，也可以将 Set 转成 List 后使用 Collections.sort，或者通过 Stream 的 sorted 方法进行排序。