
`ThreadLocal` 是 Java 多线程里很高频的一道题

**ThreadLocal = 线程本地变量。它给每个线程提供一份独立的数据副本，让线程之间互不干扰。**

它解决问题的思路和 `synchronized` 不一样：

```text
synchronized：
大家共享同一份数据
→ 加锁避免同时修改

ThreadLocal：
干脆每个线程一份数据
→ 线程之间不共享
```


[[#Q：介绍一下 ThreadLocal 的作用、原理以及内存泄漏问题。]]

---

# **一、ThreadLocal 有什么作用？**

假设三个线程都需要保存自己的 `userId`：

如果直接共享：

```java
String userId;
```

可能：

```text
Thread A → userId = "1001"
Thread B → userId = "1002"
Thread C → userId = "1003"

大家修改同一个变量
→ 相互影响
```

使用 ThreadLocal：

```java
ThreadLocal<String> userIdHolder = new ThreadLocal<>();
```

然后：

```text
Thread A → set("1001")
Thread B → set("1002")
Thread C → set("1003")
```

效果：

```text
             userIdHolder

Thread A ─→ "1001"
Thread B ─→ "1002"
Thread C ─→ "1003"

互不影响
```

所以：**ThreadLocal 特别适合保存“属于当前线程上下文”的数据。**

这在Java 后端很常见，比如苍穹外卖和黑马点评：

```java
BaseContext.setCurrentId(employeeId);
```
```java
BaseContext.getCurrentId();
```

很多这类 `BaseContext` 底层就是：

```java
ThreadLocal<Long>
```

---

# **二、ThreadLocal 最容易理解错的地方 ⭐⭐⭐⭐⭐**

很多人会认为：

```java
ThreadLocal<User> local = new ThreadLocal<>();
```

数据存在：ThreadLocal对象里面

其实真正的数据主要存储在：**Thread 对象内部的** `ThreadLocalMap` **中。**

简化结构：

```text
Thread
  │
  └── ThreadLocalMap
          │
          ├── Entry
          │    ├── key
          │    └── value
          │
          ├── Entry
          └── Entry
```

所以：

**每个线程维护自己的 ThreadLocalMap。**

---

# **三、ThreadLocal、Thread、ThreadLocalMap 的关系**

假设：

```java
ThreadLocal<String> userLocal = new ThreadLocal<>();
ThreadLocal<String> traceLocal = new ThreadLocal<>();
```

线程 A：

```java
userLocal.set("Eason");
traceLocal.set("abc123");
```

实际上可以理解：

```text
Thread A
   │
   └── ThreadLocalMap
          │
          ├── Entry
          │     key   = userLocal
          │     value = "Eason"
          │
          └── Entry
                key   = traceLocal
                value = "abc123"
```

线程 B 也有自己的：

```text
Thread B
   │
   └── ThreadLocalMap
          │
          ├── key = userLocal
          │   value = "Tom"
          │
          └── key = traceLocal
              value = "xyz789"
```

注意一个非常关键的地方：

**两个线程可以使用同一个 ThreadLocal 对象作为 key，但是它们查询的是各自 Thread 对象内部的 ThreadLocalMap，所以得到不同 value。**

这就是线程隔离的根本原因。

---

# **四、你问的 Key 和 Value 到底是什么？⭐⭐⭐⭐⭐**

比如：

```java
ThreadLocal<User> local = new ThreadLocal<>();

local.set(user);
```

对应：

```text
ThreadLocalMap

Entry
├── key   → local 这个 ThreadLocal 对象
└── value → user 这个 User 对象
```

所以：

**Key = ThreadLocal 对象本身**  
**Value = 你调用** `set(value)`  **放进去的数据**

例如：

```java
ThreadLocal<Long> USER_ID = new ThreadLocal<>();

USER_ID.set(10086L);
```

可以理解：

```text
当前线程 Thread
       ↓
ThreadLocalMap
       ↓

Entry
│
├── key   = USER_ID这个ThreadLocal对象
│
└── value = 10086L
```

然后：

```java
USER_ID.get();
```

本质上就是：

```text
当前线程
   ↓
找到自己的 ThreadLocalMap
   ↓
拿 USER_ID 当 key
   ↓
找到 Entry
   ↓
返回 value
   ↓
10086L
```

---

# **五、set() 原理**

你写：

```java
local.set(user);
```

可以简化理解：

```text
ThreadLocal.set(user)
        ↓
获取当前线程

Thread.currentThread()
        ↓
获取当前线程的
ThreadLocalMap
        ↓
如果没有 Map
→ 创建

如果有
→ 继续
        ↓
以当前 ThreadLocal 为 key
        ↓
user 为 value
        ↓
存入 Entry
```

也就是说：

```java
local.set(user);
```

不是：

```text
local里面保存user ❌
```

而是：

```text
当前Thread
    ↓
ThreadLocalMap
    ↓
local → user
```

---

# **六、get() 原理**

```java
User user = local.get();
```

简化：

```text
ThreadLocal.get()
      ↓
Thread.currentThread()
      ↓
当前线程的 ThreadLocalMap
      ↓
使用 this ThreadLocal
作为 key 查找 Entry
      ↓
Entry.value
      ↓
返回 User
```

所以为什么线程 A 和 B：

```java
local.get();
```

结果不同？

因为：

```text
同一个 local

         ↓

Thread A              Thread B
   ↓                      ↓
Map A                  Map B
   ↓                      ↓
"Eason"                 "Tom"
```

关键不是 ThreadLocal 自己给数据复制了一份，而是：

**每个 Thread 有自己的 ThreadLocalMap。**

---

# **七、ThreadLocalMap 本质上是什么？**

名字已经告诉你：

```text
ThreadLocalMap
```

它是一种专门给 ThreadLocal 使用的 Map 结构。

可以粗略理解：

```text
ThreadLocalMap

table[]
  │
  ├── Entry
  ├── Entry
  ├── null
  ├── Entry
  └── ...
```

但是它不是你平时使用的：

```java
HashMap
```

而是 ThreadLocal 内部专门实现的一套散列表结构。

---

# **八、最关键来了：Key 是弱引用 ⭐⭐⭐⭐⭐**

ThreadLocal 内存泄漏问题的核心就在这里。

`ThreadLocalMap.Entry` 可以简化理解：

```java
static class Entry extends WeakReference<ThreadLocal<?>> {

    Object value;

}
```

也就是说：

```text
Entry
│
├── key → ThreadLocal
│         弱引用 WeakReference
│
└── value → User
            强引用
```

这句话一定记住：

**ThreadLocalMap 的 Key 对 ThreadLocal 是弱引用，而 Value 是强引用。**

---

# **九、什么叫弱引用？**

正常：

```java
ThreadLocal<User> local = new ThreadLocal<>();
```

假设：

```text
local变量
    │
    ↓ 强引用
ThreadLocal对象

ThreadLocalMap Entry
    │
    ↓ 弱引用
ThreadLocal对象
```

如果：

```java
local = null;
```

或者方法执行结束后没有其他强引用指向这个 ThreadLocal：

```text
ThreadLocal对象
↑
只剩 Entry.key 的弱引用
```

发生 GC：

```text
GC
↓
ThreadLocal对象可以被回收
```

于是 Entry 可能变成：

```text
Entry

key = null

value = User对象
        ↑
        仍然是强引用
```

这就出现问题了。

---

# **十、ThreadLocal 为什么可能内存泄漏？⭐⭐⭐⭐⭐**

来看完整引用链。

原来：

```text
Thread
  ↓
ThreadLocalMap
  ↓
Entry
  ├── key ──弱引用──→ ThreadLocal
  │
  └── value ──强引用──→ User
```

ThreadLocal 被 GC 后：

```text
Thread
  ↓
ThreadLocalMap
  ↓
Entry
  ├── key = null
  │
  └── value ──强引用──→ User
```

问题来了：

Thread 还活着。

那么：

```text
Thread
 ↓
ThreadLocalMap
 ↓
Entry
 ↓
value
 ↓
User
```

这条强引用链仍然存在。

所以 User：

**不能因为 ThreadLocal key 被回收就自动回收。**

这种：

```text
key = null
value != null
```

的 Entry 经常叫：

**stale entry（陈旧 Entry）**

---

# **十一、为什么在线程池中特别危险？⭐⭐⭐⭐⭐**

普通线程：

```text
线程创建
 ↓
执行任务
 ↓
线程结束
 ↓
Thread对象最终可回收
 ↓
ThreadLocalMap一起回收
```

问题可能没那么明显。

但是你刚学了线程池：

```text
ThreadPoolExecutor

Thread-1
Thread-2
Thread-3
Thread-4
```

这些线程会：

**长期存活、不断复用。**

假设一个请求：

```java
userLocal.set(user);
```

请求处理结束：

```text
任务结束

但是 Thread-1 没死！
↓
回到线程池
↓
等待下一个任务
```

Thread-1：

```text
Thread-1
   ↓
ThreadLocalMap
   ↓
Entry
   ↓
User
```

如果你一直没有清理：

**数据可能长时间留在线程的 ThreadLocalMap 里。**

因此线程池 + ThreadLocal 是面试特别喜欢一起问的。

---

# **十二、不只是内存泄漏，还有数据串用问题**

这在 Java Web 开发里甚至更值得注意。

假设线程池只有：

```text
Thread-1
```

请求 A：

```java
userLocal.set("张三");
```

处理结束忘记：

```java
userLocal.remove();
```

Thread-1 回到线程池。

下一次：

```text
请求B
 ↓
刚好还是 Thread-1
```

如果某些代码直接：

```java
userLocal.get();
```

可能拿到之前残留的数据：

```text
"张三"
```

于是：

```text
请求A
用户：张三
   ↓
Thread-1
   ↓
ThreadLocal = 张三

请求结束
❌ 没 remove


Thread-1 被复用


请求B
用户：李四
   ↓
Thread-1
   ↓
可能残留 张三
```

这就是非常严重的：

**线程复用导致上下文污染/数据串用风险。**

---

# **十三、怎么解决？⭐⭐⭐⭐⭐**

最重要就一句：

**用完一定**  `remove()` ****。**

经典写法：

```java
try {

    userLocal.set(user);

    // 业务逻辑

} finally {

    userLocal.remove();
}
```

为什么一定放：

```java
finally
```

因为业务代码可能：

```text
正常执行
↓
remove()

没问题
```

但是：

```text
执行业务
↓
突然异常 💥
↓
直接跳出去
↓
remove 没执行
```

所以：

```java
try {
    local.set(value);

    // 使用
} finally {
    local.remove();
}
```

无论：

```text
正常结束
还是
抛异常
```

都清理。

这个和你刚学 ReentrantLock：

```java
lock.lock();

try {
    ...
} finally {
    lock.unlock();
}
```

特别像。

可以一起记：

```text
ReentrantLock
↓
lock()
try
finally → unlock()


ThreadLocal
↓
set()
try
finally → remove()
```

---

# **十四、ThreadLocal 自己也会清理 stale Entry**

这里面试稍微深入一点可能会问：

“ThreadLocalMap 难道自己完全不清理吗？”

不是。

ThreadLocal 在执行：

```java
set()
get()
remove()
```

等操作过程中，会有机会清理：

```text
key = null
```

的陈旧 Entry。

但是：

**这种清理不是你可以依赖的确定性、即时清理。**

尤其线程长期存活而后续又没有触发合适的 ThreadLocalMap 操作时，value 仍可能长时间被引用。

所以规范仍然是：

**业务使用完成后主动** `remove()` ****。**

---

# **十五、为什么 Key 要设计成弱引用？**

你可能马上会问：

“既然弱引用会产生 key=null，那为什么不用强引用？”

假设 Key 也是强引用：

```text
Thread
 ↓
ThreadLocalMap
 ↓
Entry
 ↓
key ──强引用──→ ThreadLocal
```

即使你的代码：

```java
local = null;
```

ThreadLocalMap 仍然：

```text
Entry
 ↓
强引用
 ↓
ThreadLocal
```

那么只要线程长期存活：

ThreadLocal 对象本身也无法被回收。

设计成弱引用至少意味着：

```text
业务不再引用 ThreadLocal
↓
ThreadLocal对象本身可以被GC
↓
Entry变成 key=null
↓
ThreadLocalMap 后续操作时有机会识别并清理这个 stale Entry
```

所以：

**弱引用是在降低泄漏风险，但不能代替** `remove()` ****。**

---

# **十六、ThreadLocal 和 synchronized 有什么区别？**

这个也是很好的面试题。

假设有数据：

```text
线程A
线程B
线程C
```

`synchronized`：

```text
                一份共享数据
                     ↑
              synchronized 🔒
               /     |     \
              A      B      C

大家共享
↓
通过锁保证安全
```

ThreadLocal：

```text
Thread A → Data A
Thread B → Data B
Thread C → Data C

根本不共享
↓
自然减少竞争
```

所以：

**synchronized 是“共享数据，但是控制访问”。**  
**ThreadLocal 是“每个线程保存自己的数据，尽量避免共享”。**

ThreadLocal 不是锁，也不是用来解决所有线程安全问题的。

---

# **十七、一个 Java 后端实际场景**

比如登录后，拦截器拿到用户 ID：

```java
public class UserContext {

    private static final ThreadLocal<Long> USER_ID =
            new ThreadLocal<>();

    public static void set(Long id) {
        USER_ID.set(id);
    }

    public static Long get() {
        return USER_ID.get();
    }

    public static void remove() {
        USER_ID.remove();
    }
}
```

请求：

```text
HTTP请求
 ↓
Interceptor
 ↓
解析 Token
 ↓
获得 userId = 10086
 ↓
ThreadLocal.set(10086)
 ↓
Controller
 ↓
Service
 ↓
Mapper
```

Service 不需要每层：

```java
method(userId)
```

传参数。

直接：

```java
UserContext.get();
```

就能获得：

```text
当前请求线程
   ↓
自己的 ThreadLocalMap
   ↓
10086
```

请求完成：

```text
Interceptor.afterCompletion()
 ↓
UserContext.remove()
```

避免线程池复用导致数据残留。

---

# **十八、把 ThreadLocal 整体原理压缩成一张图**

```text
              ThreadLocal
                  │
             set(value)
                  ↓
        Thread.currentThread()
                  ↓
          当前 Thread 对象
                  ↓
          ThreadLocalMap
                  ↓
                Entry
          ┌───────┴───────┐
          ↓               ↓
         key             value
          ↓               ↓
   ThreadLocal对象       业务数据
      弱引用              强引用


不同线程：

Thread A
   ↓
ThreadLocalMap A
   ↓
local → User A


Thread B
   ↓
ThreadLocalMap B
   ↓
local → User B


因此：
线程之间数据隔离
```

风险：

```text
Thread长期存活
      ↓
ThreadLocalMap长期存在
      ↓
key可能被GC → null
      ↓
value仍被Entry强引用
      ↓
可能长期无法回收
      ↓
内存泄漏风险

+

线程池复用
      ↓
旧数据可能污染后续任务
```

解决：

```text
try
  ↓
ThreadLocal.set()
  ↓
使用

finally
  ↓
ThreadLocal.remove() ⭐⭐⭐⭐⭐
```

---

## Q：介绍一下 ThreadLocal 的作用、原理以及内存泄漏问题。

ThreadLocal 用于保存线程本地变量，使每个线程拥有自己独立的数据，从而实现线程之间的数据隔离，常用于保存用户上下文、TraceId 等信息。

它的核心原理是每个 Thread 内部维护一个 ThreadLocalMap。调用 ThreadLocal 的 `set()` 时，会获取当前线程的 ThreadLocalMap，并以 **ThreadLocal 对象本身作为 key，以我们 set 进去的数据作为 value** 保存。因此即使多个线程使用同一个 ThreadLocal，它们实际上操作的是各自线程内部的 ThreadLocalMap。

ThreadLocalMap 中 Entry 的 key 对 ThreadLocal 是弱引用，而 value 通常是强引用。当 ThreadLocal 没有其他强引用后，GC 可以回收 ThreadLocal，使 Entry 出现 `key=null`，但只要线程仍然存活，value 仍可能通过 `Thread → ThreadLocalMap → Entry → value` 的引用链无法及时回收，从而产生内存泄漏风险。在线程池中由于线程长期存活和复用，这个问题更加明显，还可能造成不同任务之间的数据污染。

因此使用 ThreadLocal 后应该在 `finally` 中调用 `remove()` 主动清理。**