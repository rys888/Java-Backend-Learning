## Q：

Java 中主要有 BIO、NIO、AIO 三种 I/O 模型，区别就两件事：**线程等 I/O 的时候会不会被卡住**，以及 **I/O 做完之后怎么通知程序**。

- **BIO（Blocking I/O）**：同步阻塞，线程调 `read()` 时数据没到就一直等。
- **NIO（Non-blocking I/O）**：一般指同步非阻塞，靠 Channel、Buffer、Selector 做 I/O 多路复用，一个线程监听多个连接，哪个就绪就去读哪个。
- **AIO（Asynchronous I/O）**：异步非阻塞，发起读取后先干别的，读完由回调或者 Future 通知。

**BIO 是一直等数据，NIO 是等数据就绪然后自己读，AIO 是发起读取、完成后再通知。**

---

## 一、BIO：同步阻塞 I/O

BIO 是 Java 最传统的 I/O，典型代表是 `Socket`、`ServerSocket` 和 `InputStream`。

### 1. 工作过程

假设客户端给服务器发请求：

```text
客户端 A ────┐
            ▼
         服务器线程 A
            │
            ▼
         read() 读取数据
            │
            ▼
        没有数据到达
            │
            ▼
         线程阻塞等待
            │
            ▼
         数据到达
            │
            ▼
         继续执行
```

**BIO 的特点：线程调用 `read()` 时，如果数据还没准备好，线程就阻塞在这里，直到数据到达或者发生异常。**

传统 BIO 服务器一般是**一连接一线程**：

```text
客户端 A ─── 线程 A
客户端 B ─── 线程 B
客户端 C ─── 线程 C
客户端 D ─── 线程 D
```

所以有 10000 个客户端连接，就可能有大量线程，内存和线程调度开销都不小。

### 2. Java 示例

```java
ServerSocket serverSocket = new ServerSocket(8080);

while (true) {
    // 等待客户端连接，阻塞
    Socket socket = serverSocket.accept();

    // 为客户端创建处理线程
    new Thread(() -> {
        try {
            InputStream input = socket.getInputStream();

            // 等待客户端发送数据，可能阻塞
            int data = input.read();

            System.out.println(data);

            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }).start();
}
```

这段代码有两个阻塞点：`accept()` 等客户端建连接，`read()` 等客户端发数据。**优点是编程模型简单，缺点是传统的一连接一线程模型扛不住大量并发连接。**

---

## 二、NIO：同步非阻塞 I/O 

NIO 是 Java 1.4 引入的 I/O API，三个核心组件是 **Channel（通道）、Buffer（缓冲区）、Selector（选择器）**。

### 1. 为什么需要 Selector

Channel 可以设成非阻塞模式，**线程调 `read()` 时如果没数据可读，直接返回，不用一直等。**

但问题在于，不阻塞就得想办法知道数据什么时候来。如果自己不停循环检查，就是在空转烧 CPU。

所以 NIO 引入了 **Selector（多路复用器）**：一个 Selector 可以同时监听多个 Channel，某个 Channel 出现可读、可写事件时，再交给程序处理。

```text
客户端 A ─────┐
              │
客户端 B ─────┤
              │
客户端 C ─────┼────► Selector
              │          │
客户端 D ─────┤          ▼
              │      监听 I/O 事件
客户端 E ─────┘          │
                         ▼
                    某个连接可读
                         │
                         ▼
                     线程处理
```

这样一来，就不用给每个连接分配一个长期阻塞的线程了。

### 2. 三个核心组件

| 组件 | 作用 |
|---|---|
| Channel | 负责数据传输，类似传统 I/O 中的流 |
| Buffer | 用于存储读取或写入的数据 |
| Selector | 监听多个 Channel 的 I/O 就绪事件 |

一次完整的数据读取流程：

```text
SocketChannel
      │
      ▼
   Selector
      │
      ▼
  发现可读事件
      │
      ▼
Channel.read()
      │
      ▼
    Buffer
      │
      ▼
  处理业务数据
```

### 3. 为什么 NIO 是同步非阻塞

这里容易搞混，"非阻塞"和"同步"说的其实是两个层面。

**非阻塞**：线程调用非阻塞 Channel 的 `read()`，没数据可读就立即返回。

**同步**：Selector 通知程序的是"这个 Channel 已经可以读了"，而不是"数据已经读完了"。真正的读取还是要程序自己调：

```java
channel.read(buffer);
```

所以才叫同步非阻塞。

⚠️ 注意：`Selector.select()` 本身是会阻塞等待事件的，不能理解成 NIO 里所有方法都不会阻塞。

### 4. 优缺点

优点是**一个线程可以管理多个连接**，适合大量连接、网络 I/O 密集的场景。

缺点也很明显，原生 NIO 编程复杂，事件循环、缓冲区、半包粘包、连接状态都得自己处理。所以实际 Java 后端开发里一般用 Netty 这类框架，很少直接堆原生 NIO 代码。

---

## 三、AIO：异步非阻塞 I/O

AIO 是 Java 7 引入的异步 I/O API，典型代表是 `AsynchronousSocketChannel`、`AsynchronousServerSocketChannel` 和 `AsynchronousFileChannel`。

### 1. 工作过程

AIO 和 NIO 最大的区别是：**发起 I/O 操作后不需要等它完成，可以通过回调或者 Future 拿最终结果。**

```text
应用线程
   │
   ▼
发起异步 read()
   │
   ▼
立即继续执行其他任务
   │
   │
   │      底层执行 I/O 操作
   │              │
   │              ▼
   │          数据读取完成
   │              │
   ▼              ▼
其他任务       回调通知程序
```

### 2. Java 示例

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);

channel.read(buffer, buffer,
    new CompletionHandler<Integer, ByteBuffer>() {

        @Override
        public void completed(
                Integer result,
                ByteBuffer attachment) {

            System.out.println("读取完成：" + result);
        }

        @Override
        public void failed(
                Throwable exc,
                ByteBuffer attachment) {

            exc.printStackTrace();
        }
    }
);
```

调完 `read()` 方法就返回了，程序不用同步等着。底层读完之后系统来调 `completed()`，读失败则调 `failed()`。

⚠️ 注意：Java AIO 的底层实现跟操作系统有关，不一定全部依赖操作系统原生的异步 I/O，某些平台上可能是靠线程池模拟出的异步效果。

---

## 四、BIO、NIO、AIO 的核心区别 ⭐⭐⭐⭐⭐

| 对比 | BIO | NIO | AIO |
|---|---|---|---|
| I/O 模型 | 同步阻塞 | 同步非阻塞 | 异步非阻塞 |
| 数据未准备好时 | 线程阻塞等待 | 非阻塞读取可立即返回 | 发起操作后继续执行 |
| 数据读取方式 | 线程主动读取 | 线程主动读取 | 异步操作完成后通知 |
| 连接处理 | 传统方式一连接一线程 | Selector 管理多个连接 | 异步操作与完成通知 |
| 编程复杂度 | 较低 | 较高 | 较高 |
| Java 代表 API | Socket、InputStream | Channel、Buffer、Selector | AsynchronousSocketChannel |
| 典型应用 | 简单网络服务 | Netty、高并发网络服务器 | 异步网络或文件 I/O |

---

## 最后总结

三个关键词：

- **BIO：等待数据。**
- **NIO：等待数据就绪，然后自己读取。**
- **AIO：发起读取，完成后通知。**

面试里最常问的是 NIO 那套：**Channel、Buffer、Selector，以及 I/O 多路复用为什么能支撑大量并发连接。**
