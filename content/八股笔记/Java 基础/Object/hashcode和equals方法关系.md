这段话的核心其实就一句：
 `hashCode()`  **负责快速找到对象可能在哪，**** `equals()`  **负责最终确认是不是同一个“逻辑对象”。**
可以结合 `HashMap` 来理解。
假设：
```java
Person p1 = new Person(1, "张三");
Person p2 = new Person(1, "张三");
```
我们重写了方法，规定：**id 和 name 一样，就认为两个 Person 相等。**
那么：
```java
p1.equals(p2)    // true
```
既然逻辑上已经认为它们相等，那么：
```java
p1.hashCode() == p2.hashCode()
```
也必须成立。
### **为什么必须这样？**
因为 `HashMap` 查找一个 key，大致是：
```text
key
 ↓
① 计算 hashCode
 ↓
② 根据 hashCode 找到对应位置/桶
 ↓
③ 再使用 equals 比较
 ↓
④ 确认是不是要找的对象
```
假如出现这种情况：
```text
p1.equals(p2) = true

但是：

p1.hashCode() = 100
p2.hashCode() = 200
```
那么它们可能被分到**不同的桶**：
```text
HashMap

桶1 ← p1（hashCode = 100）

桶2 ← p2（hashCode = 200）
```
这就出问题了：明明 `equals()` 认为它俩一样，HashMap 却可能根本不会到同一个地方比较它们。

---

而反过来：
```java
p1.hashCode() == p2.hashCode()
```
**不能说明：**
```java
p1.equals(p2) == true
```
因为 `hashCode()` 只有 `int` 这么大的取值范围，而对象可以有无数种，所以不同对象完全可能算出同一个数字。
例如：
```text
Person A → hashCode = 666
Person B → hashCode = 666

但：

A.equals(B) → false
```

这就是**哈希冲突**。
所以八股直接记这三句话：
**① equals 相等 → hashCode 必须相等。**  
**② hashCode 相等 → equals 不一定相等，因为可能哈希冲突。**  
**③ HashMap 中 hashCode 用于快速定位，equals 用于最终确认。**

因此，**重写**  equals()时必须配套重写hashCode()，让二者的“相等标准”保持一致。