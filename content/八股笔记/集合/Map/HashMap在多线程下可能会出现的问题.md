
HashMap 本身不是线程安全的。多个线程并发修改时可能出现**数据覆盖或更新丢失、size 等状态不一致、并发扩容导致数据异常**等问题；JDK 7 中并发扩容还存在链表成环、导致死循环的经典问题。另外遍历过程中发生结构性修改，还可能触发 fail-fast，抛出 `ConcurrentModificationException`。因此并发场景下一般使用 `ConcurrentHashMap`，而不是直接共享 HashMap。

八股最值得记的三个关键词就是：

**更新丢失 + 并发扩容问题 + JDK 7 链表成环。**