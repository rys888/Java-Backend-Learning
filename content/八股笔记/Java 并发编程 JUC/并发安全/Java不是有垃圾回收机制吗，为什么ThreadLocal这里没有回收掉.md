
[[#Q：]]

Java 确实有垃圾回收机制，但 **GC 只能回收不可达的对象，而不是回收所有不再使用的对象。**

ThreadLocal 可能发生内存泄漏，正是因为：**ThreadLocal 对象已经被 GC 回收了，但它对应的 Value 仍然被 ThreadLocalMap 强引用着，导致 Value 无法被回收。**

## **一、先理解 ThreadLocal 的存储结构**

每个 Thread 对象内部都有一个 `ThreadLocalMap`，用于存储线程自己的局部变量。

```java
ThreadLocal<User> threadLocal = new ThreadLocal<>();

threadLocal.set(new User());
```

底层关系可以理解为：

```text
Thread（线程）
   │
   │ 强引用
   ▼
ThreadLocalMap
   │
   ▼
Entry
   │
   ├── Key：ThreadLocal 对象（弱引用）
   │
   └── Value：User 对象（强引用）
```

**重点：ThreadLocalMap 中的 Key 是弱引用，而 Value 是强引用。**

为什么 Key 要设计成弱引用？

因为如果外部不再使用某个 ThreadLocal，弱引用不会阻止 GC 回收这个 ThreadLocal 对象。

但问题也因此出现了。

---

## **二、为什么 GC 没有回收 Value？**

假设执行：

```java
public void test() {
    ThreadLocal<User> local = new ThreadLocal<>();

    local.set(new User());
}
```

当 `test()` 方法执行结束后，局部变量 `local` 不再使用。

如果没有其他强引用指向这个 ThreadLocal，那么 GC 可以回收它。

但是，此时可能出现：

```text
                  GC Roots
                      │
                      ▼
                 Thread 线程
                      │
                   强引用
                      ▼
                ThreadLocalMap
                      │
                   强引用
                      ▼
                    Entry
                   /     \
                  /       \
              弱引用     强引用
                │           │
                ▼           ▼
          ThreadLocal      User
             (Key)        (Value)
                │           │
                ▼           │
            被 GC 回收      │
                            ▼
                       无法被回收
```

最终变成：

```text
Thread
   │
   ▼
ThreadLocalMap
   │
   ▼
Entry
   │
   ├── Key = null
   │
   └── Value = User 对象
```

**虽然 Key 已经被 GC 回收，但是 Value 仍然存在一条从 GC Roots 出发的强引用链。**

所以，GC 不能直接回收 Value。

这就是 ThreadLocal 内存泄漏问题的根本原因。

注意，`Key = null` 不代表 Value 一定会永久泄漏，而是说它可能在一段时间内无法被回收。

---

## **三、为什么线程池更容易出现这个问题？**

这是面试中经常追问的地方。

普通线程执行结束后，如果 Thread 对象本身也不再被引用，那么它持有的 ThreadLocalMap 及其中的 Value 就可以一起被回收。

但线程池不一样。

**线程池会复用线程，线程可能长期存活。**

例如：

```java
private static final ThreadLocal<User> USER_CONTEXT =
        new ThreadLocal<>();

public void process() {
    USER_CONTEXT.set(new User());

    // 执行业务逻辑
}
```

假设这个方法在线程池中执行：

```text
线程池
   │
   ▼
工作线程 Thread-1
   │
   ▼
ThreadLocalMap
   │
   ▼
User 对象
```

业务方法执行结束后，线程并没有销毁，而是回到线程池等待下一个任务。

如果没有调用 `remove()`，之前设置的 User 对象可能一直保存在这个线程的 ThreadLocalMap 中。

这里还有一个需要区分的情况：

**如果 ThreadLocal 本身是** ** `static final` ****，Key 通常不会被回收，但 Value 仍然可能因为没有清理而长期占用内存。**

因此，ThreadLocal 的问题不仅仅是弱引用 Key 变成 null，还包括线程复用导致的旧数据残留。

---

## **四、ThreadLocalMap 不会自动清理吗？**

会，但不是立即清理。

ThreadLocalMap 在执行 `get()`、`set()`、`remove()` 等操作时，可能顺带清理部分 Key 已经失效的 Entry。

但这种清理具有一定的触发条件，**并不是每次 GC 后都会立即清理所有失效 Entry**。

如果线程长期存活，而且后续没有触发相关清理操作，那么 Value 就可能长期占用内存。

所以，不能完全依赖 ThreadLocalMap 的自动清理机制。

---

## **五、怎么解决？**

最推荐的方式是使用 `try-finally`，确保业务执行结束后调用 `remove()`。

```java
private static final ThreadLocal<User> USER_CONTEXT =
        new ThreadLocal<>();

public void process() {
    try {
        USER_CONTEXT.set(new User());

        // 执行业务逻辑
        doSomething();

    } finally {
        USER_CONTEXT.remove();
    }
}
```

这样即使业务代码抛出异常，也能够清理当前线程的 ThreadLocal 数据。

在 Spring Boot 项目中，ThreadLocal 经常用于保存当前请求的用户信息。

例如：

```java
public class UserContext {

    private static final ThreadLocal<Long> USER_ID =
            new ThreadLocal<>();

    public static void set(Long userId) {
        USER_ID.set(userId);
    }

    public static Long get() {
        return USER_ID.get();
    }

    public static void remove() {
        USER_ID.remove();
    }
}
```

如果在拦截器中设置用户信息，就应该在请求结束时清理，避免线程池复用时发生用户信息串扰。

---

## Q：

Java 虽然有 GC，但 GC 只能回收不可达对象。

ThreadLocal 的数据实际上存储在线程内部的 ThreadLocalMap 中，其中 Key 是对 ThreadLocal 对象的弱引用，而 Value 是强引用。

当外部没有强引用指向 ThreadLocal 时，GC 可以回收 Key 对应的 ThreadLocal 对象，但 Value 仍然被 ThreadLocalMap 中的 Entry 强引用，因此无法直接回收。

特别是在线程池中，线程会被长期复用，ThreadLocalMap 也会随线程长期存在。如果没有及时清理，就可能造成内存泄漏。

虽然 ThreadLocalMap 会在部分操作中清理失效 Entry，但不能保证及时清理。

因此，实际开发中应该在 `finally` 中调用 `ThreadLocal.remove()`，避免内存泄漏和线程复用导致的数据串扰。

记住 Key 弱引用，value 强引用