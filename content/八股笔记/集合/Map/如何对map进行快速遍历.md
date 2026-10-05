- 使用 for-each 循环和 entrySet()方法
- 使用 for-each 循环和 keySet()方法
- 使用迭代器
- 使用 Lambda 表达式和 forEach()方法
- 使用 Stream API

可以继续用同一个 `Map` 来看这 5 种遍历方式，这样最好理解。

假设：

```java
Map<Integer, String> map = new HashMap<>();

map.put(1, "Java");
map.put(2, "MySQL");
map.put(3, "Redis");
```

里面可以理解为：

```text
1 → Java
2 → MySQL
3 → Redis
```



## **1.** `for-each + entrySet()` **⭐⭐⭐⭐⭐**

这是最推荐掌握的一种：

```java
for (Map.Entry<Integer, String> entry : map.entrySet()) {
    Integer key = entry.getKey();
    String value = entry.getValue();

    System.out.println(key + " -> " + value);
}
```

这里：

```java
map.entrySet()
```

会得到一组 `Entry`：

```text
Entry(1, Java)
Entry(2, MySQL)
Entry(3, Redis)
```

每个 `Entry` 同时包含：

```text
Entry
 ├── getKey()
 └── getValue()
```

所以如果遍历时**同时需要 key 和 value**，优先：

```java
entrySet()
```

---
## **2.** `for-each + keySet()` 

`keySet()` 获取所有 Key：

```java
for (Integer key : map.keySet()) {
    String value = map.get(key);

    System.out.println(key + " -> " + value);
}
```

过程相当于：

```text
map.keySet()
    ↓
[1, 2, 3]

第一次：
key = 1
map.get(1) → Java

第二次：
key = 2
map.get(2) → MySQL
```

如果**只需要 Key**，`keySet()` 很合适：

```java
for (Integer key : map.keySet()) {
    System.out.println(key);
}
```

但如果 **Key 和 Value 都需要**：

```java
for (Integer key : map.keySet()) {
    String value = map.get(key);
}
```

通常不如直接 `entrySet()`，因为还需要额外执行 `map.get(key)` 查找 value。

所以记：

**只需要 Key →** ** `keySet()` ****；Key + Value 都需要 →** ** `entrySet()` ****。**

---

## **3. Iterator 迭代器**

通常也是遍历 `entrySet()`：

```java
Iterator<Map.Entry<Integer, String>> iterator =
        map.entrySet().iterator();

while (iterator.hasNext()) {

    Map.Entry<Integer, String> entry = iterator.next();

    System.out.println(
        entry.getKey() + " -> " + entry.getValue()
    );
}
```

流程：

```text
iterator
   ↓
hasNext()
   ↓
next()
   ↓
Entry
 ├─ key
 └─ value
```

Iterator 一个重要用途是：

**遍历过程中需要删除当前元素时，可以使用** ** `iterator.remove()` ****。**

例如：

```java
Iterator<Map.Entry<Integer, String>> iterator =
        map.entrySet().iterator();

while (iterator.hasNext()) {

    Map.Entry<Integer, String> entry = iterator.next();

    if (entry.getKey() == 2) {
        iterator.remove();
    }
}
```

这样可以安全删除当前遍历到的元素。

---
## **4. Lambda + `forEach()` **⭐⭐⭐⭐⭐**

Java 8 之后非常简洁：

```java
map.forEach((key, value) -> {
    System.out.println(key + " -> " + value);
});
```

这里：

```java
(key, value) -> {
    ...
}
```

就是你前面学过的 **Lambda 表达式**。

比如：

```java
map.forEach((k, v) ->
        System.out.println(k + "=" + v)
);
```

代码非常简洁。

所以日常业务代码中，如果只是简单遍历处理：

```java
map.forEach((key, value) -> ...)
```

非常常见。

---

## **5. Stream API**

Map 本身不能直接：

```java
map.stream(); // ❌
```

通常需要通过：

```java
map.entrySet().stream()
```

例如：

```java
map.entrySet()
   .stream()
   .forEach(entry -> {
       System.out.println(
           entry.getKey() + " -> " + entry.getValue()
       );
   });
```

但如果你只是单纯遍历，这样写没什么必要。

Stream 真正适合的是**遍历之前还要过滤、转换等处理**。

比如：

只处理 Key 大于 1 的数据：

```java
map.entrySet()
   .stream()
   .filter(entry -> entry.getKey() > 1)
   .forEach(entry ->
       System.out.println(
           entry.getKey() + " -> " + entry.getValue()
       )
   );
```

过程：

```text
Map

1 → Java
2 → MySQL
3 → Redis

   ↓ entrySet().stream()

Stream<Entry>

   ↓ filter(key > 1)

2 → MySQL
3 → Redis

   ↓ forEach

输出
```

---

### **五种方式怎么选？**

|**方法**|**使用场景**|
|---|---|
| `entrySet()` + for-each|⭐ **Key + Value 都需要，经典写法**|
| `keySet()` + for-each|只需要 Key|
| `Iterator` |⭐ 遍历过程中需要安全删除|
| `Map.forEach()` |⭐ Java 8，简单遍历非常方便|
|Stream API|⭐ 需要过滤、转换、聚合等流水线操作|

面试官如果问：

**Map 有哪些遍历方式？哪一种比较推荐？**

你可以回答：

Map 可以通过 `entrySet()`、`keySet()`、Iterator、Java 8 的 `forEach()` 以及 Stream API 进行遍历。如果同时需要 Key 和 Value，通常优先使用 `entrySet()`，因为 Entry 中可以直接获得 Key 和 Value，避免通过 Key 再进行一次 `get()` 查询。如果只是简单处理，也可以使用 Java 8 的 `Map.forEach()`；如果还涉及过滤、转换等操作，可以考虑 Stream API。


**只要 Key →**  `keySet()` ****；Key + Value →**  `entrySet()` ****；简单 Java 8 写法 →** `forEach()` ****；过滤转换 →** `Stream` 。
