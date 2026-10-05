JDK 8 的 `ConcurrentHashMap` **两种思想都用了**：

**CAS → 乐观锁思想**  
**synchronized → 悲观锁思想**

### **乐观锁是什么？**

乐观锁的思想是：

**我觉得别人不会和我冲突，我先尝试修改；真冲突了再重试。**

比如 ConcurrentHashMap 发现桶为空：

```text
table[i] = null

线程A：想放 Node A
线程B：想放 Node B
```

通过 CAS：

```text
线程A：CAS(null → A) → 成功

线程B：CAS(null → B)
       ↓
发现已经不是 null
       ↓
失败，重新尝试
```

它不会提前把位置锁住。

所以：

**CAS 是典型的乐观并发控制方式：先尝试，冲突了再处理。**

### **悲观锁是什么？**

悲观锁的思想是：

**我认为别人很可能和我同时修改，所以我先把资源锁住，其他线程先等着。**

ConcurrentHashMap 桶不为空时：

```text
table[i]
   ↓
   A → B → C
   🔒
```

执行：

```java
synchronized (A) {
    // 修改当前桶
}
```

线程 A 拿到锁：

```text
线程A → 🔒 → 修改链表
线程B → 等待……
```

所以 `synchronized` 属于典型的**悲观锁机制**。

### **一句话区分**

```text
乐观锁：
“应该没人跟我抢，我先试试”
        ↓
       CAS


悲观锁：
“肯定有人跟我抢，我先锁起来”
        ↓
 synchronized / Lock
```

因此面试问：

**ConcurrentHashMap 用的是悲观锁还是乐观锁？**

回答：

**JDK 8 ConcurrentHashMap 两者都有使用。对于一些简单竞争场景，例如空桶插入，会通过 CAS 这种乐观并发方式完成；对于已经存在节点的桶，需要修改链表或红黑树时，会使用 synchronized 进行互斥，属于悲观锁机制。**

口诀就是：

**CAS：先试，失败重来——乐观。**  
**synchronized：先锁，再操作——悲观。**