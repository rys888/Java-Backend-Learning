
Java 中的内存溢出（OutOfMemoryError，简称 OOM）是指 **JVM 无法为对象或其他运行时数据分配所需内存，并且无法通过垃圾回收等方式获得足够空间**。

OOM 不仅可能发生在堆中，还可能发生在**方法区（元空间）、虚拟机栈相关的线程创建过程、直接内存等区域**。

## 一、哪些内存区域可能发生 OOM？

|内存区域|是否可能 OOM|典型异常或表现|常见原因|
|---|---|---|---|
|**Java 堆**|✅| `Java heap space` |对象过多、内存泄漏、堆容量不足|
|**方法区（元空间）**|✅| `Metaspace` |加载大量类、ClassLoader 泄漏|
|**虚拟机栈**|✅| `unable to create native thread` 等|线程过多、本地内存不足|
|**本地方法栈**|✅|与本地栈资源有关的错误|本地栈空间或线程资源不足|
|**程序计数器**|❌|无|JVM 规范中唯一未规定 OOM 的运行时数据区域|
|**直接内存**|✅| `Cannot reserve ... bytes of direct buffer memory` |DirectByteBuffer 占用过多|

需要注意：直接内存不属于 JVM 规范定义的运行时数据区，但也是 Java 程序可能发生 OOM 的重要区域。

---

## 二、Java 堆内存溢出

这是最常见的 OOM。

### 1. 产生原因

Java 堆主要用于存储对象实例。

如果程序不断创建对象，并且这些对象始终被引用，GC 就无法回收它们。

例如：

```
public class HeapOOM {

    public static void main(String[] args) {
        List<byte[]> list = new ArrayList<>();

        while (true) {
            list.add(new byte[1024 * 1024]);
        }
    }
}
```

这里每次创建一个 1 MB 的数组，并放入 List 中。

由于 List 始终持有这些数组的引用，GC 无法回收它们。

最终可能出现：

```
java.lang.OutOfMemoryError: Java heap space
```

### 2. 如何排查？

可以配置：

```
-Xmx256m
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/logs/
```

发生 OOM 后生成 Heap Dump，再使用 MAT 分析对象占用情况和 GC Roots 引用链。

重点排查静态集合无限增长、缓存没有过期机制、一次性查询大量数据库记录等问题。

---

## 三、方法区（元空间）内存溢出 ⭐⭐⭐⭐⭐

方法区主要存储类元数据、方法信息、运行时常量池等。

在 HotSpot JVM 中，JDK 8 之后使用元空间（Metaspace）存储类元数据。

### 1. 产生原因

例如：

- 频繁动态生成类。
- 大量使用 CGLIB 等动态代理技术。
- 自定义 ClassLoader 不断加载类，却无法卸载。
- 元空间大小设置过小。

当元空间无法继续分配时，可能出现：

```
java.lang.OutOfMemoryError: Metaspace
```

### 2. 如何排查？

查看元空间配置：

```
-XX:MaxMetaspaceSize=256m
```

可以使用：

```
jcmd <pid> VM.metaspace
```

检查元空间使用情况。

如果元空间持续增长，应重点排查类加载器泄漏，而不是单纯增大元空间上限。

---

## 四、虚拟机栈和本地方法栈内存溢出

这里要区分两个异常：

**StackOverflowError 和 OutOfMemoryError。**

### 1. StackOverflowError：栈溢出

例如：

```
public class StackTest {

    public static void main(String[] args) {
        test();
    }

    public static void test() {
        test();
    }
}
```

由于无限递归，方法调用会不断创建新的栈帧。

```
虚拟机栈
┌──────────────┐
│ test() 栈帧  │
├──────────────┤
│ test() 栈帧  │
├──────────────┤
│ test() 栈帧  │
├──────────────┤
│ test() 栈帧  │
├──────────────┤
│     ...      │
└──────────────┘
```

最终出现：

```
java.lang.StackOverflowError
```

**注意：StackOverflowError 不属于 OOM，它是另一种错误。**

### 2. OutOfMemoryError：无法创建线程

例如：

```
public class ThreadOOM {

    public static void main(String[] args) {
        while (true) {
            new Thread(() -> {
                try {
                    Thread.sleep(Long.MAX_VALUE);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
    }
}
```

如果持续创建平台线程，每个线程都需要消耗一定的本地内存和操作系统线程资源。

当资源不足时，可能出现：

```
java.lang.OutOfMemoryError:
unable to create native thread
```

这类错误不一定意味着 Java 堆内存不足，也可能是操作系统线程数量限制、进程资源限制或本地内存不足。

**因此，虚拟机栈相关问题需要区分：递归过深通常导致 StackOverflowError；线程创建资源不足可能导致 OOM。**

---

## 五、直接内存溢出 ⭐⭐⭐⭐⭐

直接内存（Direct Memory）是 JVM 堆外的一种内存使用方式。

Java NIO 可以通过 `ByteBuffer.allocateDirect()` 申请直接缓冲区。

例如：

```
public class DirectMemoryOOM {

    public static void main(String[] args) {
        List<ByteBuffer> buffers = new ArrayList<>();

        while (true) {
            buffers.add(
                ByteBuffer.allocateDirect(1024 * 1024)
            );
        }
    }
}
```

这里不断申请 1 MB 的直接内存，并保留缓冲区引用。

当直接内存达到限制时，可能出现类似：

```
java.lang.OutOfMemoryError:
Cannot reserve 1048576 bytes of direct buffer memory
```

可以通过参数限制直接内存：

```
-XX:MaxDirectMemorySize=256m
```

---

## 六、程序计数器为什么不会 OOM？

程序计数器（Program Counter Register）是线程私有的。

它主要用于记录当前线程执行的字节码指令位置。

例如：

```
int a = 10;
int b = 20;
int c = a + b;
```

程序计数器可以帮助 JVM 跟踪当前线程执行到哪条字节码指令。

由于它只需要保存少量执行位置信息，JVM 规范没有规定程序计数器会发生 OOM。

因此，**程序计数器是 JVM 运行时数据区中唯一没有规定 OutOfMemoryError 的区域。**

---

## 七、面试怎么回答？⭐⭐⭐⭐⭐

 JVM 中可能发生 OOM 的区域主要包括 Java 堆、方法区、虚拟机栈和本地方法栈相关的内存资源，以及堆外的直接内存。
 
 **首先是 Java 堆**，如果对象创建过多、存在内存泄漏或者堆容量不足，可能出现 `Java heap space`。

**其次是方法区**，在 JDK 8 之后的 HotSpot 中主要由元空间实现。如果大量类被加载而无法卸载，可能出现 `Metaspace`。

**第三是虚拟机栈和本地方法栈相关的内存资源**，如果线程创建过多，导致本地内存或者操作系统线程资源不足，可能出现 `unable to create native thread`。

另外，Java NIO 使用的直接内存也可能发生 OOM，例如直接缓冲区分配过多。

需要注意，递归调用过深通常引发的是 `StackOverflowError`，而不是 OOM。

最后，程序计数器是 JVM 运行时数据区中唯一没有规定 OOM 的区域。

### 最后总结

```
JVM 内存溢出
│
├── Java 堆
│   └── OutOfMemoryError: Java heap space
│
├── 方法区（元空间）
│   └── OutOfMemoryError: Metaspace
│
├── 虚拟机栈 / 本地方法栈相关资源
│   ├── StackOverflowError（不是 OOM）
│   └── OutOfMemoryError: unable to create native thread
│
├── 直接内存
│   └── OutOfMemoryError: Direct buffer memory
│
└── 程序计数器
    └── JVM 规范未规定 OOM
```

**面试记忆：堆存对象、元空间存类、线程栈消耗线程资源、直接内存存堆外缓冲区；程序计数器不规定 OOM。**
