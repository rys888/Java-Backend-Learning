
## Q：

Java 规定，如果两个对象通过 `equals()` 判断相等，那么它们的 `hashCode()` 必须相同。

这是因为 HashMap、HashSet 等哈希集合会先通过 `hashCode()` 计算对象的存储位置，再通过 `equals()` 判断对象是否真正相等。

如果只重写 `equals()`，不重写 `hashCode()`，就可能出现两个逻辑上相等的对象具有不同哈希值的情况，导致它们被存储到不同的哈希桶中，从而出现 HashSet 无法正确去重、HashMap 无法正常查找等问题。

需要注意的是，**equals() 相等，hashCode() 必须相同；但 hashCode() 相同，equals() 不一定相等，因为可能发生哈希冲突。**


## **一、先理解 equals() 和 hashCode()**

**① equals()：判断两个对象是否相等**

`Object` 类默认的 `equals()` 比较的是两个对象是否为同一个对象。

```java
public boolean equals(Object obj) {
    return (this == obj);
}
```

但在实际开发中，我们可能希望根据对象的属性判断是否相等。

例如，两个 `User` 对象的 `id` 相同，就认为它们是同一个用户。

**② hashCode()：返回对象的哈希值**

`hashCode()` 返回一个 `int` 类型的哈希值。

HashMap、HashSet 等集合会利用哈希值定位对象的存储位置，再通过 `equals()` 判断对象是否真正相等。

---

## **二、为什么重写 equals() 必须重写 hashCode()？**

假设我们定义一个 `User` 类，只重写 `equals()`：

```java
public class User {

    private Integer id;

    public User(Integer id) {
        this.id = id;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;

        if (!(obj instanceof User)) return false;

        User other = (User) obj;
        return Objects.equals(this.id, other.id);
    }
}
```

现在创建两个对象：

```java
User user1 = new User(1001);
User user2 = new User(1001);

System.out.println(user1.equals(user2)); // true
```

由于两个对象的 `id` 相同，所以 `equals()` 返回 `true`。

但是：

```java
System.out.println(user1.hashCode());
System.out.println(user2.hashCode());
```

由于没有重写 `hashCode()`，仍然使用 `Object` 默认实现。

**两个对象虽然通过 equals() 判断相等，但 hashCode() 可能不同。**

这就违反了 Java 的约定：

如果两个对象通过 equals() 判断相等，那么它们的 hashCode() 必须相同。

### **这会造成什么问题？**

假设使用 HashSet：

```java
Set<User> set = new HashSet<>();

set.add(user1);
set.add(user2);

System.out.println(set.size());
```

按照我们的业务逻辑：

```text
user1.id = 1001
user2.id = 1001

user1.equals(user2) = true
```

两个对象应该被视为同一个用户。

因此，预期：

```text
set.size() = 1
```

但是，由于两个对象的哈希值可能不同，HashSet 可能将它们存储到不同位置。

最终：

```text
set.size() = 2
```

**这就导致 HashSet 无法正确去重。**

---

## **三、为什么 HashSet 会出现这个问题？**

因为 HashSet 底层使用 HashMap 实现。

当执行：

```java
set.add(user1);
```

HashSet 会利用 `hashCode()` 计算哈希值，再确定存储位置。

```text
user1
  │
  ▼
hashCode()
  │
  ▼
计算存储位置
  │
  ▼
存入 HashMap
```

接着执行：

```java
set.add(user2);
```

如果两个对象的哈希值不同，就可能被定位到不同的位置。

```text
user1 → hashCode = 123 → 桶 A

user2 → hashCode = 456 → 桶 B
```

由于位于不同的桶中，HashMap 通常不会调用 `equals()` 将它们进行比较。

因此，即使：

```java
user1.equals(user2) == true
```

HashSet 仍然可能将它们当作两个不同元素。

**关键点：HashMap 并不是直接遍历所有对象调用 equals()，而是先通过 hashCode() 定位，再在必要时通过 equals() 判断。**

---

## **四、正确做法：同时重写两个方法**

```java
public class User {

    private Integer id;

    public User(Integer id) {
        this.id = id;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;

        if (!(obj instanceof User)) return false;

        User other = (User) obj;
        return Objects.equals(this.id, other.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
```

现在：

```java
User user1 = new User(1001);
User user2 = new User(1001);

System.out.println(user1.equals(user2)); // true

System.out.println(user1.hashCode() == user2.hashCode()); // true

Set<User> set = new HashSet<>();

set.add(user1);
set.add(user2);

System.out.println(set.size()); // 1
```

这样就可以正常去重。

---

## **五、equals() 和 hashCode() 的关系 ⭐⭐⭐⭐⭐**

这里有三个非常重要的结论：

|**equals()**|**hashCode()**|**是否可能**|
|---|---|---|
| `true` |相同|必须如此|
| `false` |相同|可以，发生哈希冲突|
| `false` |不同|可以|
| `true` |不同|不允许，违反约定|

**注意：两个对象的 hashCode() 相同，不代表 equals() 一定返回 true。**

例如：

```java
String s1 = "Aa";
String s2 = "BB";

System.out.println(s1.hashCode()); // 2112
System.out.println(s2.hashCode()); // 2112

System.out.println(s1.equals(s2)); // false
```

虽然哈希值相同，但字符串内容不同。

这就是**哈希冲突**。

因此：

- `hashCode()` 主要用于快速定位。
- `equals()` 用于判断对象是否真正相等。

另外，参与 `equals()` 和 `hashCode()` 计算的字段，最好不要在对象作为 HashMap 的 Key 或 HashSet 的元素期间发生变化，否则可能导致对象无法被正常查找。

---
