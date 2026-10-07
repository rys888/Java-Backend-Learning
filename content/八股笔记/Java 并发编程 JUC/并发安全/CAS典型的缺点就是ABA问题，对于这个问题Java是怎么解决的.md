
**ABA 是 CAS 最经典的问题之一**。Java 最典型的解决方案就是：

**给值加一个“版本号”——**** `AtomicStampedReference` ****。**

## **1. ABA 到底是什么？**

CAS 的逻辑是：

```text
我之前看到 value = A

准备修改时：
现在还是 A 吗？

是 → 修改成功
否 → 修改失败
```

问题在于，CAS **只关心现在是不是 A，不知道中间发生过什么**。

比如线程 1：

```text
第一次读取：
A
↓
准备 CAS
```

这时候线程 1 被暂停。

线程 2：

```text
A → B → A
```

然后线程 1 恢复：

```text
之前看到：A
现在看到：A

CAS：
A == A
↓
成功
```

线程 1 会认为：

“值没变过。”

但实际上：

```text
A → B → A
```

已经发生了两次修改。

这就是：

**ABA 问题。**

---

## **2. 为什么 ABA 会有问题？**

假设你只关心一个数字：

```text
100 → 200 → 100
```

有些业务可能确实无所谓。

但如果这个 A 是一个**对象引用、链表节点或者某种状态**，你可能不仅关心：

“现在是不是 A？”

还关心：

**“从我上次读取以后，它有没有被别人修改过？”**

普通 CAS 无法判断这一点。

---

# **3. Java 怎么解决？版本号**

核心思想特别简单：

原来 CAS 比较：

```text
A → B → A

只看 value：

A == A
✅
```

现在给它增加版本号：

```text
A(1)
 ↓
B(2)
 ↓
A(3)
```

线程 1 最开始读取：

```text
value = A
version = 1
```

等它回来以后：

```text
value = A
version = 3
```

虽然：

```text
A == A
```

但是：

```text
1 != 3
```

于是：

**CAS 失败。**

这就发现了 ABA。

---

# # **4. Java 提供*** `AtomicStampedReference` 

Java 中对应的类：

```java
AtomicStampedReference<T>
```

其中：

```text
Reference → 真正的数据
Stamp     → 版本号
```

例如：

```java
AtomicStampedReference<String> ref =
        new AtomicStampedReference<>("A", 1);
```

现在：

```text
value = A
stamp = 1
```

修改：

```java
ref.compareAndSet(
    "A",   // 期望值
    "B",   // 新值
    1,     // 期望版本号
    2      // 新版本号
);
```

它不再只比较：

```text
当前值 == 期望值？
```

而是同时比较：

```text
当前值 == 期望值
        &&
当前stamp == 期望stamp
```

两个都对：

```text
CAS成功
↓
value更新
stamp更新
```

---

# **5. ABA 发生后是什么样？**

最开始：

```text
A(1)
```

线程 1：

```text
读取：
A(1)
```

暂停。

线程 2：

```text
A(1)
 ↓
B(2)
 ↓
A(3)
```

线程 1 回来：

```text
我期望：
A(1)

实际：
A(3)
```

比较：

```text
value：
A == A       ✅

stamp：
1 == 3       ❌

最终：
CAS失败
```

因此：

**虽然值又变回 A，但版本号记录了它曾经发生过变化。**

---

## **6. 还有一个** `AtomicMarkableReference` 

Java 还提供：

```java
AtomicMarkableReference<T>
```

它不是版本号，而是：

```text
Reference + boolean mark
```

例如：

```text
Node + true/false
```

适合你只关心：

**“这个对象是否发生过某种状态变化？”**

而不关心到底改了多少次。

区别：

|**类**|**附加信息**|**适合**|
|---|---|---|
| `AtomicReference` |无|普通引用 CAS|
| `AtomicStampedReference` |int 版本号|防 ABA，追踪版本变化|
| `AtomicMarkableReference` |boolean 标记|只关心某个二元状态|
面试最重要的还是：

`AtomicStampedReference` ****。**

---

# **7. 把它和数据库乐观锁联系起来**

你学 MySQL 后端的话，这个特别好理解。

数据库经常：

```text
id | stock | version
1  | 100   | 5
```

更新：

```sql
UPDATE product
SET stock = 99,
    version = 6
WHERE id = 1
  AND version = 5;
```

其实思想非常像：

```text
CAS：
value + stamp

数据库乐观锁：
data + version
```

都是：

**不仅检查数据，还检查“我读取之后版本有没有变化”。**

---

## Q：CAS 有什么问题？ABA 怎么解决？

CAS 的一个典型问题是 ABA。比如线程第一次读取到 A，在 CAS 之前其他线程将其从 A 修改为 B，再修改回 A，此时 CAS 只比较当前值，会认为值仍然是 A，从而修改成功，但实际上这个值中间已经发生过变化。

Java 可以通过 `AtomicStampedReference` 解决这个问题，它在引用之外增加一个版本号 stamp。每次修改数据时同时修改版本号，因此即使数据发生 `A → B → A`，版本号也会从比如 `1 → 2 → 3`，原线程进行 CAS 时发现版本号不一致，就能识别出数据曾经被修改过。

直接记：

```text
ABA：
A → B → A
看起来没变，实际上变过

解决：
A(1) → B(2) → A(3)

Java：
AtomicStampedReference
= 数据 + 版本号
```

顺便注意：**ABA 只是 CAS 的缺点之一**。面试再问“CAS 还有什么缺点”，通常还要答 **自旋时间过长会浪费 CPU**，以及**普通 CAS 通常只能原子地比较更新一个共享变量/一个内存位置（复杂多变量一致性需要封装或其他同步机制）**。