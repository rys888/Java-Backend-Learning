
[[#Q：]]

假设执行：

```sql
UPDATE user SET balance = 500 WHERE id = 1;
```

原来的 `balance = 1000`，`id` 是主键。

### **一、UPDATE 的具体执行过程**

**① Server 层解析 SQL**

MySQL 首先对 SQL 进行解析和优化，确定执行计划。

例如，这条 SQL 可以通过主键索引找到 `id = 1` 的记录。

**② InnoDB 通过索引查找数据**

InnoDB 通过聚簇索引找到 `id = 1` 对应的数据页。

- 如果数据页已经在 Buffer Pool 中，直接读取。
- 如果不在，就先从磁盘加载到 Buffer Pool。

**③ 对索引记录加排他锁（X 锁）**




⚠️：
**共享锁（S 锁）**：允许多个事务同时对同一条记录加共享锁进行读取，但不允许其他事务对该记录加排他锁进行修改。
**排他锁（X 锁）**：只允许当前事务持有该记录的排他锁，不允许其他事务再对该记录加共享锁或排他锁。
**共同点：** 两者都允许其他事务通过普通 `SELECT`（MVCC 快照读）读取数据，也都阻止其他事务修改被锁定的记录。
**核心区别：共享锁允许其他事务加锁（共享锁）读取，排他锁不允许其他事务加锁读取。**



**④ 记录 Undo Log**

修改数据之前，InnoDB 会生成相应的 Undo Log 信息。

假设：

```text
修改前：balance = 1000
修改后：balance = 500
```

Undo Log 可以用于：

- 事务回滚，恢复修改前的数据。
- MVCC，通过版本链读取历史数据。

**⑤ 修改 Buffer Pool 中的数据**

InnoDB 将 `balance` 从 1000 修改为 500。

此时修改通常先发生在 Buffer Pool 中，对应的数据页成为**脏页（Dirty Page）**。

并不需要立即将整个数据页写入磁盘。

**⑥ 生成 Redo Log**

InnoDB 会记录相关数据页的修改信息到 Redo Log。

这样即使 Buffer Pool 中的脏页还没刷盘，数据库突然崩溃，也可以通过 Redo Log 进行恢复。

注意：Redo Log 的生成会伴随前面的数据修改过程，并不是必须等数据全部修改完才开始生成。

**⑦ 写入 Binlog，并提交事务**

如果开启了 Binlog，事务提交时需要协调 Redo Log 和 Binlog。

MySQL 通常通过**两阶段提交**保证两种日志的一致性：

```text
Redo Log Prepare
        ↓
写入 Binlog
        ↓
Redo Log Commit
```

这里展示的是简化后的提交流程。

**⑧ 释放锁，后续将脏页刷入磁盘**

事务提交成功后，释放相关事务锁。

Buffer Pool 中的脏页可以在之后由 InnoDB 刷入磁盘。

---

### 二、流程

```text
执行 UPDATE
     ↓
Server 层解析、优化 SQL
     ↓
InnoDB 通过索引查找记录
     ↓
从 Buffer Pool 获取数据页
（没有则从磁盘读取）
     ↓
对目标索引记录加排他锁
     ↓
生成 Undo Log
     ↓
修改 Buffer Pool 中的数据
     ↓
生成 Redo Log
     ↓
事务提交
     │
     ├── Redo Log Prepare
     │
     ├── 写入 Binlog
     │
     └── Redo Log Commit
     ↓
释放事务锁
     ↓
后续将脏页刷入磁盘
```

这里的流程假设使用 InnoDB、开启 Binlog，并且事务成功提交；具体内部操作可能交织进行。

### Q：

MySQL 执行 UPDATE 时，首先由 Server 层解析和优化 SQL，确定执行计划。

然后 InnoDB 根据索引找到需要修改的记录，从 Buffer Pool 中获取对应的数据页，并对相关索引记录加排他锁。

修改数据时，会生成 Undo Log，用于事务回滚和 MVCC，同时修改 Buffer Pool 中的数据，并生成 Redo Log，用于崩溃恢复。

如果开启了 Binlog，事务提交时会通过两阶段提交机制协调 Redo Log 和 Binlog，保证两种日志的一致性。

最后事务提交成功，释放相关锁，而 Buffer Pool 中的脏页可以在之后异步刷入磁盘。

**最重要的是理解三个日志各自的作用：**

- **Undo Log：** 修改错了可以回滚，其他事务还能读取旧版本。
- **Redo Log：** 数据页还没刷盘，数据库崩溃后也能恢复。
- **Binlog：** 记录数据变更，用于主从复制和数据恢复。

这三个日志共同参与了 InnoDB 的事务处理过程。

