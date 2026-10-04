这三个都是 Java 中**处理字符串**的类。面试里最重要的是抓住两个关键词：**可变性 + 线程安全性**。

### **1. String：不可变字符串**

`String` 创建之后，它里面的字符串内容**不能被修改**。

```java
String s = "hello";
s = s + " world";
```

看起来 `"hello"` 被修改成了 `"hello world"`，实际上不是。

```text
原来：
s ──→ "hello"

执行 s = s + " world"

       "hello"        ← 原来的对象没有修改
       
s ──→ "hello world"  ← 创建了新的 String 对象
```

**String 是不可变的，每次对字符串内容进行修改，本质上往往会产生新的 String 对象。**

因此，如果大量进行字符串拼接：

```java
String s = "";

for (int i = 0; i < 10000; i++) {
    s = s + i;
}
```

可能产生很多中间对象，效率较低。

---

### **2. StringBuilder：可变字符串**

`StringBuilder` 内部内容可以直接修改，不会创建新对象：

```java
StringBuilder sb = new StringBuilder("hello");

sb.append(" world");
sb.append("!");
```

可以简单理解成：

```text
String：

"hello"
   ↓ 创建新对象
"hello world"
   ↓ 创建新对象
"hello world!"


StringBuilder：

["hello"]
    ↓ 直接追加
["hello world"]
    ↓ 直接追加
["hello world!"]
```

最后如果需要 `String`：

```java
String result = sb.toString();
```

所以大量字符串拼接通常推荐：

```java
StringBuilder sb = new StringBuilder();

for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
```

---

### **3. StringBuffer：线程安全版 StringBuilder**

`StringBuffer` 和 `StringBuilder` 非常像：

```java
StringBuffer sb = new StringBuffer("hello");
sb.append(" world");
```

最大的区别是：

StringBuffer 的很多方法使用了 `synchronized` 等同步机制，因此线程安全。

例如可以简单理解成：

```java
StringBuilder
    ↓
可变
速度快
线程不安全

StringBuffer
    ↓
可变
有同步保护
线程安全
但通常性能相对低一些
```

---

### **三者直接这样记**

|**特点**|**String**|**StringBuilder**|**StringBuffer**|
|---|---|---|---|
|字符串是否可变|❌ 不可变|✅ 可变|✅ 可变|
|线程安全|因不可变而天然适合共享|❌ 非线程安全|✅ 线程安全|
|拼接性能|大量反复拼接较差|⭐⭐⭐ 高|⭐⭐ 相对低|
|常见场景|普通字符串|单线程大量拼接|多线程共享可变字符串|

### **面试怎么回答？**

面试官问：

String、StringBuilder、StringBuffer 有什么区别？

你可以直接回答：

**String 是不可变字符串，每次修改通常会产生新的 String 对象；StringBuilder 和 StringBuffer 都是可变字符串，适合频繁进行字符串拼接。StringBuilder 非线程安全，但性能通常更好；StringBuffer 的方法有同步机制，因此线程安全，但同步会带来一定性能开销。一般单线程字符串拼接使用 StringBuilder，需要共享可变字符串且要求线程安全时才考虑 StringBuffer。**

再压缩成口诀就是：

**String：不可变**  
**StringBuilder：可变、快、不保证线程安全**  
**StringBuffer：可变、线程安全、相对慢**

这是 Java 实习面试里比较典型的八股题，掌握到这个程度基本够用。