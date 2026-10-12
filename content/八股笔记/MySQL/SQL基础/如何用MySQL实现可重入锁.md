
在 MySQL 中，可以通过 **数据库锁表 + 唯一索引 + 持有者标识 + 重入次数** 实现一个可重入锁。

不过需要先明确：**MySQL 本身已经提供了命名锁** `GET_LOCK()` ****，它支持可重入；如果面试官要求手动设计可重入锁，则可以使用 MySQL 表来实现。**

下面分别解释。

## **一、什么是可重入锁？**

可重入锁（Reentrant Lock）指的是：

**同一个线程已经获得某把锁后，可以再次获得这把锁，而不会被自己阻塞。**

例如 Java 中的 `ReentrantLock`：

```java
ReentrantLock lock = new ReentrantLock();

lock.lock(); // 第一次获取锁
lock.lock(); // 第二次获取锁，允许重入

try {
    System.out.println("执行业务");
} finally {
    lock.unlock();
    lock.unlock();
}
```

其核心原理是：

```text
线程 A 第一次获取锁
        ↓
锁持有者 = A
重入次数 = 1
        ↓
线程 A 再次获取锁
        ↓
发现锁持有者还是 A
        ↓
允许重入
重入次数 = 2
        ↓
第一次释放锁
重入次数 = 1
        ↓
第二次释放锁
重入次数 = 0
        ↓
真正释放锁
```

所以，实现可重入锁需要解决三个问题：

1. 如何保证只有一个持有者获得锁？
2. 如何识别当前请求是否来自同一个持有者？
3. 如何记录重入次数，并在次数归零时释放锁？

## 使用 MySQL 表手动实现可重入锁 ⭐⭐⭐⭐⭐

如果面试官问的是：

**“如何基于 MySQL 自己设计一个可重入的分布式锁？”**

那么更值得掌握的是这种方案。

## **1. 设计锁表**

创建一张分布式锁表：

```sql
CREATE TABLE distributed_lock (
    lock_key VARCHAR(100) PRIMARY KEY,
    owner_id VARCHAR(100) NOT NULL,
    reentrant_count INT NOT NULL,
    expire_time DATETIME(6) NOT NULL
) ENGINE = InnoDB;
```

字段含义：

|**字段**|**作用**|
|---|---|
| `lock_key` |锁名称，唯一标识一把锁|
| `owner_id` |锁持有者标识|
| `reentrant_count` |重入次数|
| `expire_time` |锁过期时间|

其中最重要的是：

```sql
lock_key VARCHAR(100) PRIMARY KEY
```

利用 MySQL 主键的唯一性，保证同一把锁最多只有一条记录。

例如：

|**lock_key**|**owner_id**|**reentrant_count**|**expire_time**|
|---|---|---|---|
|order:1001|JVM 1:Thread 10:UUID|2|2026-10-11 18:30:00|

表示：

- `order:1001` 这把锁已经被持有。
- 持有者是 `JVM1:Thread10:UUID`。
- 当前重入了两次。

这里的 `owner_id` 应当在一次锁持有生命周期内保持不变，并且对不同持有者足够唯一。

---

## **2. 第一次获取锁**

假设线程 A 想获取：

```text
order:1001
```

执行：

```sql
INSERT INTO distributed_lock (
    lock_key,
    owner_id,
    reentrant_count,
    expire_time
)
VALUES (
    'order:1001',
    'owner-A',
    1,
    DATE_ADD(NOW(6), INTERVAL 30 SECOND)
);
```

如果插入成功：

```text
锁不存在
    ↓
INSERT 成功
    ↓
线程 A 获取锁
    ↓
重入次数 = 1
```

如果线程 B 同时执行：

```sql
INSERT INTO distributed_lock (
    lock_key,
    owner_id,
    reentrant_count,
    expire_time
)
VALUES (
    'order:1001',
    'owner-B',
    1,
    DATE_ADD(NOW(6), INTERVAL 30 SECOND)
);
```

由于 `lock_key` 是主键，线程 B 会因为主键冲突而无法成功插入。

这样就利用 **MySQL 唯一索引保证了锁的互斥性**。

---

## **3. 同一个线程再次获取锁**

现在假设线程 A 已经持有锁。

它再次请求：

```text
order:1001
```

由于主键已经存在，不能再次插入。

但是我们可以判断锁持有者是不是自己。

执行：

```sql
UPDATE distributed_lock
SET
    reentrant_count = reentrant_count + 1,
    expire_time = DATE_ADD(NOW(6), INTERVAL 30 SECOND)
WHERE lock_key = 'order:1001'
  AND owner_id = 'owner-A'
  AND expire_time > NOW(6);
```

如果更新成功：

```text
锁已经存在
    ↓
判断 owner_id
    ↓
发现持有者是自己
    ↓
允许再次获取锁
    ↓
reentrant_count + 1
```

例如：

```text
第一次获取：

owner_id = owner-A
reentrant_count = 1

第二次获取：

owner_id = owner-A
reentrant_count = 2

第三次获取：

owner_id = owner-A
reentrant_count = 3
```

这就是可重入锁的核心实现。

**本质上就是通过** ** `owner_id` ** **判断是否为同一个持有者，通过** ** `reentrant_count` ** **记录重入次数。**

---

## **4. 不同线程获取锁**

假设线程 B 尝试获取线程 A 持有的锁：

```sql
UPDATE distributed_lock
SET reentrant_count = reentrant_count + 1
WHERE lock_key = 'order:1001'
  AND owner_id = 'owner-B'
  AND expire_time > NOW(6);
```

因为数据库中保存的是：

```text
owner_id = owner-A
```

所以：

```text
UPDATE 影响行数 = 0
```

线程 B 无法获取锁。

此时可以选择：

- 立即返回获取失败。
- 等待一段时间后重试。
- 设置最大等待时间，超时后返回失败。

需要注意，**不能仅凭一次 UPDATE 影响行数为 0，就判断锁永久不可获取**，因为锁可能随后被释放。

---

# **四、如何释放可重入锁？**

释放锁时需要判断当前重入次数。

### **情况一：重入次数大于 1**

执行：

```sql
UPDATE distributed_lock
SET reentrant_count = reentrant_count - 1
WHERE lock_key = 'order:1001'
  AND owner_id = 'owner-A'
  AND reentrant_count > 1
  AND expire_time > NOW(6);
```

例如：

```text
原来：
reentrant_count = 3

释放一次：
reentrant_count = 2
```

此时锁仍然由线程 A 持有。

### **情况二：重入次数等于 1**

执行：

```sql
DELETE FROM distributed_lock
WHERE lock_key = 'order:1001'
  AND owner_id = 'owner-A'
  AND reentrant_count = 1
  AND expire_time > NOW(6);
```

此时锁记录被删除。

其他线程就可以重新竞争这把锁。

这里有一个重要细节：

**释放锁时的 UPDATE 和 DELETE 必须根据数据库实际影响行数判断结果。**

如果 UPDATE 影响 0 行，才尝试 DELETE；如果两者都没有成功，说明当前持有者可能已经失去锁，不能直接认为释放成功。

上述两个操作通过条件更新避免了普通并发下的重入计数丢失问题。

---

# **五、还需要解决一个问题：锁过期怎么办？**

假设线程 A 获取锁后，程序突然崩溃：

```text
线程 A 获取锁
       ↓
数据库插入锁记录
       ↓
程序崩溃
       ↓
没有执行释放锁
       ↓
其他线程一直无法获取锁
```

所以我们设计了：

```sql
expire_time
```

表示锁的过期时间。

但需要注意：

**仅仅增加**  `expire_time`  **字段，并不能自动释放过期锁。**

我们还需要实现过期锁回收或原子抢占逻辑。

例如，可以使用单条条件更新尝试抢占过期锁：

```sql
UPDATE distributed_lock
SET
    owner_id = 'owner-B',
    reentrant_count = 1,
    expire_time = DATE_ADD(NOW(6), INTERVAL 30 SECOND)
WHERE lock_key = 'order:1001'
  AND expire_time <= NOW(6);
```

如果更新成功，说明线程 B 抢占了已经过期的锁。

这里利用 MySQL 的条件更新保证抢占操作的原子性。

但这只是基础实现，还存在一个重要问题。

### **过期锁可能导致并发执行**

假设：

```text
线程 A 获取锁，过期时间 30 秒
            ↓
线程 A 执行业务超过 30 秒
            ↓
锁过期
            ↓
线程 B 抢占锁
            ↓
线程 A 和线程 B 同时执行业务
```

此时，即使数据库锁记录只有一个持有者，也不能保证业务代码绝对互斥。

生产环境通常还需要考虑：

- 锁续期机制。
- 过期后的旧持有者不能继续修改受保护资源。
- Fencing Token（递增令牌）等防止旧持有者写入的机制。
- 获取锁、重入、释放操作应及时提交，不能把锁表事务长时间保持开启。

尤其要注意：**续期只能降低锁意外过期的概率，不能单独解决旧持有者继续执行的问题。**

---
## **七、面试怎么回答？⭐⭐⭐⭐⭐**

如果面试官问：

**“如何使用 MySQL 实现一个可重入锁？”**

可以这样回答：

MySQL 实现可重入锁可以基于 MySQL 表手动实现。

首先设计一张锁表，包含 lock_key、owner_id、reentrant_count 和 expire_time 四个核心字段。

获取锁时，通过 lock_key 的唯一索引保证互斥性。如果锁不存在，就插入记录，并将重入次数设置为 1。

如果锁已经存在，则判断 owner_id 是否与当前持有者一致。如果一致，就通过条件 UPDATE 将 reentrant_count 加 1，实现锁的重入。

释放锁时，将重入次数减 1，只有当重入次数降为 0 时，才真正删除锁记录。

此外，还需要考虑锁过期、程序崩溃、锁续期以及旧持有者继续执行等问题。

不过实际生产开发中，如果需要跨 JVM 的可重入分布式锁，通常还会考虑 Redis + Redisson 等成熟方案。

### **最后总结**

**MySQL 手动实现可重入锁的核心是三个字段：**

```text
lock_key
   ↓
唯一索引保证互斥

owner_id
   ↓
判断是不是同一个持有者

reentrant_count
   ↓
记录重入次数，归零释放锁
```

其中最值得记住的是：

**普通互斥锁只需要判断锁是否被占用，而可重入锁还需要判断锁是否被自己占用，并维护重入次数。**

这也是 Java `ReentrantLock` 和 Redisson 可重入锁在设计思想上的共同点。