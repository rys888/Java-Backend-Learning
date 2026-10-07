# 05 · Redis + Lua 高并发预约

> **只讲代码在做什么。** 本篇覆盖 `submit` 的前半段：**校验 → 生成 id → 写账本 → 抢名额**。投递消息在 06 篇。
>
> **全篇用一个例子从头走到尾**：一门 **5 个名额**的批次，**6 个学生同时点**。每个代码块后面都会写「例子里的对应值」——你可以在脑子里跟着这几个数字把代码跑一遍。

**涉及文件**

```
resources/reservation.lua
utils/ReservationQuotaExecutor.java     utils/RedisIdWorker.java
utils/RedisConstants.java
service/impl/ReservationServiceImpl.java（submit 前半段）
service/impl/ReservationRequestServiceImpl.java（createPreAccepted / casStatusWithFailReason）
controller/ReservationController.java   dto/ReservationSubmitDTO.java
enums/ReservationResultCode.java        enums/ReservationRequestStatus.java
entity/ReservationBatch.java
```

---
---

# 零、先把例子摆出来

## 0.1 数据

> 实验室、设备、分类的名字与状态都取自 `phase2_laboratory_equipment.sql` 里的**真实种子数据**；`userId` 是编的（真实环境里 `tb_user.id` 由自增决定，种子管理员靠 `phone` 唯一键定位），但形状是真的。

| 对象 | 字段 | 值 |
|---|---|---|
| 实验室 | `id` / `name` / `status` | 2 / 分析测试实验室 / `OPEN` |
| 设备 | `id` / `name` | **3** / 高效液相色谱仪 |
| | `laboratory_id` / `category_id` | 2 / 2（化学分析） |
| | `status` / `booking_enabled` | `AVAILABLE` / `1` |
| 批次 | `id` | **7** |
| | `equipment_id` | 3 |
| | `total_quota` / `remaining_quota` | **5** / **5** |
| | `status` | `PUBLISHED` |
| | `booking_start_time` / `booking_end_time` | 2026-10-07 09:00 / 18:00 |
| | `start_time` / `end_time`（使用时段） | 2026-10-08 14:00 / 16:00 |
| 学生 | `userId` | **101, 102, 103, 104, 105, 106** |

6 个人都在 **2026-10-07 09:00:00** 这一刻点了「预约」。

## 0.2 这一刻 Redis 里长什么样

批次 `publish` 的时候已经建好了 quota key（见 04 篇），users key 还不存在：

```
127.0.0.1:6379> GET reservation:batch:quota:7
"5"

127.0.0.1:6379> EXISTS reservation:batch:users:7
(integer) 0
```

**记住这两个 key 的样子**，后面全程都在改它们两个。

---
---

# 一、先看结果：6 个人点下去，Redis 里发生了什么

Lua 脚本在 Redis 里是**原子执行**的，所以 6 个请求必然排成一队。下面这张表是本篇的「答案」，后面几节拆开讲每一步是怎么发生的。

| 顺序 | 请求 | 在 Lua 的哪一行停下 | 返回 | quota 之后 | users 之后 |
|---|---|---|---|---|---|
| 1 | 学生 101 | 走完全程 | **0** `SUCCESS` | `"4"` | `{101}` |
| 2 | 学生 102 | 走完全程 | **0** | `"3"` | `{101,102}` |
| 3 | 学生 103 | 走完全程 | **0** | `"2"` | `{101…103}` |
| 4 | 学生 104 | 走完全程 | **0** | `"1"` | `{101…104}` |
| 5 | 学生 105 | 走完全程 | **0** | `"0"` | `{101…105}` |
| 6 | 学生 106 | `GET quota` 拿到 `"0"` → `<= 0` | **2** `SOLD_OUT` | `"0"`（**没动**） | `{101…105}`（没动） |

**结果**：101～105 拿到 `200`，106 拿到 `400 名额已约满`。

**第 6 个请求停下的位置很关键**：它在 `GET` 之后就 `return 2` 了，**根本没执行 `DECR`**。所以「抢失败」这一侧**不需要归还名额**——它压根没扣。后面 §6.5 会用到这个事实。

## 1.1 三个变体（同一个例子，换个时间点）

**变体 A：学生 101 手快点了两次**

第二个请求会拿到一个**新的 `reservationId`**（`RedisIdWorker` 每次递增），所以它是一笔新请求，但 `userId` 还是 101：

| 顺序 | 请求 | 停下 | 返回 |
|---|---|---|---|
| 1 | 101 第 1 次 | 走完全程 | **0** |
| 2 | 101 第 2 次 | `SISMEMBER users 101` = 1 | **3** `DUPLICATE` |

**变体 B：学生 107 在 08:59 点**（窗口还没开）

**根本走不到 Lua** —— `submit` 里第 ⑥ 项前置检查 `now.isBefore(bookingStartTime)` 就先抛 `400 预约尚未开始`。

**变体 C：学生 107 在 09:00:00.000 被 Java 放行，09:00:00.001 管理员关闭了批次**

Java 那侧已经判完了（通过），Lua 执行时 quota key 已被 `close` 删掉：

| 停下 | 返回 | 含义 |
|---|---|---|
| `EXISTS quota:7` = 0 | **1** `BATCH_NOT_OPEN` | 批次已关闭 |

**变体 C 说明了为什么 Java 和 Lua 要做两遍判定**（§6.1 会展开）。

---
---

# 二、两个 key

```java
// utils/RedisConstants.java
public static final String RESERVATION_BATCH_QUOTA_KEY  = "reservation:batch:quota:";
public static final String RESERVATION_BATCH_USERS_KEY  = "reservation:batch:users:";
public static final Long   RESERVATION_BATCH_QUOTA_TTL_BUFFER_HOURS = 24L;
```

| Key | 类型 | 值 | TTL |
|---|---|---|---|
| `reservation:batch:quota:{batchId}` | **String** | 剩余名额（整数文本） | `publish` 时设 = `endTime + 24h - now` |
| `reservation:batch:users:{batchId}` | **Set** | 抢到名额的 userId | 每次抢成功时 `EXPIRE` 重设 = `endTime + 24h - now` |

**一个用 String（要 `DECR`/`INCR`），一个用 Set（要 `SISMEMBER`/`SADD`）。**

**例子里的对应值**：

| Key | TTL 秒数 |
|---|---|
| `reservation:batch:quota:7` | `endTime(1791446400) + 24h − now(1791334800)` = **198000 秒 = 55 小时** |
| `reservation:batch:users:7` | 每次抢成功时被 `EXPIRE` 设成同样的 198000（但基准 `now` 是那一刻的 `now`，会有几毫秒/几秒的差） |

> 55 小时 = 从 10-07 09:00 到 10-08 16:00 的 31 小时，再加 24 小时缓冲。**批次使用时段结束后还有 24 小时，名额 key 才过期**——留这个缓冲是为了让「取消」还能把名额还回去。

---
---

# 三、`reservation.lua` 逐行

`src/main/resources/reservation.lua`，27 行。**每一段后面都用例子里的某个请求代入。**

## 3.1 参数约定 —— 拿学生 102 的那次请求代入

| 位置 | 是什么 | 例子里（学生 102，09:00:00） |
|---|---|---|
| `KEYS[1]` | quota key | `"reservation:batch:quota:7"` |
| `KEYS[2]` | users key | `"reservation:batch:users:7"` |
| `ARGV[1]` | `userId` | `"102"` |
| `ARGV[2]` | `now`（epoch 秒） | `"1791334800"` |
| `ARGV[3]` | `bookingStartTime` | `"1791334800"` |
| `ARGV[4]` | `bookingEndTime` | `"1791367200"` |
| `ARGV[5]` | users key 的 TTL 秒数 | `"198000"` |

**Redis 传进来的都是字符串**（注意上面每个值都带引号），所以 Lua 里要用 `tonumber()` 转换。

## 3.2 第 1-3 行：名额 key 存在吗

```lua
if redis.call('EXISTS', KEYS[1]) == 0 then
    return 1
end
```

quota key 不存在 → 返回 **1 = `BATCH_NOT_OPEN`**。

**什么时候会不存在**：`publish` 用 `setIfAbsent` 建这个 key；`close` / `cancel` 会删它；它自己也有 TTL。所以 key 不在 = 要么批次没发布过，要么已经关了/取消了，要么 TTL 到期了。

**例子里的对应**：变体 C —— 管理员在 Java 判完之后、Lua 执行之前关了批次，`EXISTS reservation:batch:quota:7` 返回 0，学生 107 拿到 `1`。

## 3.3 第 5-13 行：预约窗口

```lua
local now = tonumber(ARGV[2])
local bookingStartTime = tonumber(ARGV[3])
local bookingEndTime = tonumber(ARGV[4])
if now < bookingStartTime then
    return 4
end
if now > bookingEndTime then
    return 5
end
```

- `now < bookingStartTime` → **4 = `BOOKING_NOT_STARTED`**
- `now > bookingEndTime` → **5 = `BOOKING_EXPIRED`**

**例子里的对应**（`now = 1791334800`，正好等于 `bookingStartTime`）：

| 比较 | 结果 | 是否拦下 |
|---|---|---|
| `1791334800 < 1791334800` | false | 不拦 → 继续往下 |
| `1791334800 > 1791367200` | false | 不拦 → 继续往下 |

**`now` 是从 Java 传进来的**（`submit:101` 那次 `LocalDateTime.now()`），**不是脚本内部取的**。所以判定基准是**请求开始的那一刻**，不是 Lua 执行的那一刻。

## 3.4 第 15-18 行：名额

```lua
local quota = redis.call('GET', KEYS[1])
if not quota or tonumber(quota) <= 0 then
    return 2
end
```

- `GET` 拿到 `nil`（key 刚被删）或值 `<= 0` → **2 = `SOLD_OUT`**

**例子里的对应**：这就是**学生 106 停下的地方**。前面 5 个人已经把 `quota` 扣到 `"0"`，他 `GET` 到 `"0"`，`tonumber("0") <= 0` 成立 → `return 2`。

**注意它没有执行 `DECR`** —— 这是他后面不需要「归还名额」的原因。

## 3.5 第 20-22 行：去重

```lua
if redis.call('SISMEMBER', KEYS[2], ARGV[1]) == 1 then
    return 3
end
```

`userId` 已经在 users Set 里 → **3 = `DUPLICATE`**。

**例子里的对应**：变体 A —— 学生 101 的第二次点击，`SISMEMBER reservation:batch:users:7 101` 返回 1 → `return 3`。

## 3.6 第 24-27 行：扣减 + 打标记

```lua
redis.call('DECR', KEYS[1])
redis.call('SADD', KEYS[2], ARGV[1])
redis.call('EXPIRE', KEYS[2], ARGV[5])
return 0
```

三条命令：**名额 −1、userId 加进 Set、重设 Set 的 TTL**。然后返回 **0 = `SUCCESS`**。

**例子里的对应**：学生 102 走的就是这一支。执行完：

```
quota:7  "5" → "3"        （前面 101 扣过一次，他这次扣完是 3）
users:7  {101} → {101,102}
users:7 的 TTL 被重设为 198000 秒
```

**`KEYS[1]`（quota）这里没有再 `EXPIRE`** —— 它的 TTL 在 `publish` 时设好了，之后一直不动。**只有 users 的 TTL 会被每次抢成功往后推**。

## 3.7 判定顺序

```
EXISTS quota?      no  → 1 BATCH_NOT_OPEN
now < bookStart?   yes → 4 BOOKING_NOT_STARTED
now > bookEnd?     yes → 5 BOOKING_EXPIRED
quota <= 0?        yes → 2 SOLD_OUT          ← 学生 106 停在这里
SISMEMBER users?   yes → 3 DUPLICATE         ← 学生 101 第 2 次停在这里
否则：DECR + SADD + EXPIRE → 0 SUCCESS       ← 学生 101~105 走完
```

**「已约过」的判断排在第 5 步**：一个已经约过的用户，如果此时窗口也过了，返回的是 5（`BOOKING_EXPIRED`），不是 3。**顺序决定返回哪个码。**

---
---

# 四、六个返回码

`enums/ReservationResultCode.java`

```java
SUCCESS            (0, null)
BATCH_NOT_OPEN     (1, "批次未开放预约")
SOLD_OUT           (2, "名额已约满")
DUPLICATE          (3, "你已预约过该批次")
BOOKING_NOT_STARTED(4, "预约尚未开始")
BOOKING_EXPIRED    (5, "预约已截止")

public static ReservationResultCode fromCode(int code) {
    for (ReservationResultCode resultCode : values()) {
        if (resultCode.code == code) return resultCode;
    }
    throw new IllegalArgumentException("未知预约结果码：" + code);
}
```

`fromCode` 走的是**枚举 `values()` 遍历**，找不到就抛 `IllegalArgumentException`。

**例子里的对应**：

| 例子 | Lua 返回 | `fromCode` 得到 | 最终 HTTP |
|---|---|---|---|
| 学生 101~105 | 0 | `SUCCESS` | `200` |
| 学生 106 | 2 | `SOLD_OUT` | `400 名额已约满` |
| 学生 101 第 2 次 | 3 | `DUPLICATE` | `400 你已预约过该批次` |
| 变体 B：学生 107 @08:59 | — | Java 侧就拦了 | `400 预约尚未开始` |
| 变体 C：批次被关 | 1 | `BATCH_NOT_OPEN` | `400 批次未开放预约` |

---
---

# 五、Java 侧怎么调这个脚本

`utils/ReservationQuotaExecutor.java`

## 5.1 加载脚本（静态块）

```java
private static final DefaultRedisScript<Long> RESERVATION_SCRIPT;

static {
    RESERVATION_SCRIPT = new DefaultRedisScript<>();
    RESERVATION_SCRIPT.setLocation(new ClassPathResource("reservation.lua"));
    RESERVATION_SCRIPT.setResultType(Long.class);
}
```

`DefaultRedisScript<Long>` 声明返回值类型是 `Long`。类加载时读一次 `reservation.lua`，之后复用。

## 5.2 `tryAcquire`

```java
public ReservationResultCode tryAcquire(ReservationBatch batch, Long userId, LocalDateTime now) {
    String quotaKey = RESERVATION_BATCH_QUOTA_KEY + batch.getId();
    String usersKey = RESERVATION_BATCH_USERS_KEY + batch.getId();
    long ttlSeconds = Duration.between(
            now,
            batch.getEndTime().plusHours(RESERVATION_BATCH_QUOTA_TTL_BUFFER_HOURS)).getSeconds();

    Long rawCode = stringRedisTemplate.execute(
            RESERVATION_SCRIPT,
            Arrays.asList(quotaKey, usersKey),          // KEYS[1], KEYS[2]
            userId.toString(),                          // ARGV[1]
            Long.toString(toEpochSecond(now)),          // ARGV[2]
            Long.toString(toEpochSecond(batch.getBookingStartTime())),   // ARGV[3]
            Long.toString(toEpochSecond(batch.getBookingEndTime())),     // ARGV[4]
            Long.toString(ttlSeconds));                 // ARGV[5]
```

**`Arrays.asList(quotaKey, usersKey)` 的顺序就是 `KEYS[1]`、`KEYS[2]`**；后面变长参数按顺序是 `ARGV[1..5]`。

**例子里的对应** —— 学生 102 那次调用，拼出来的两条 key 和五个参数就是 §3.1 那张表。等价的 `redis-cli` 写法：

```
EVAL "$(cat reservation.lua)" 2 \
     reservation:batch:quota:7 reservation:batch:users:7 \
     102 1791334800 1791334800 1791367200 198000
      ↑   ↑          ↑          ↑          ↑
    user  now    bookStart  bookEnd    ttlSeconds
```

`toEpochSecond`（同一文件末尾）：

```java
private long toEpochSecond(LocalDateTime time) {
    return time.atZone(ZoneId.systemDefault()).toEpochSecond();
}
```

**注意时区**：这里用的是 `ZoneId.systemDefault()`，而 `RedisIdWorker` 用的是 `ZoneOffset.UTC`。**同一个 09:00，这两处会算出相差 8 小时的两个数**（具体见 §7）。

## 5.3 返回值转换

```java
    if (rawCode == null || rawCode < Integer.MIN_VALUE || rawCode > Integer.MAX_VALUE) {
        log.error("预约 Lua 返回异常：{}", rawCode);
        throw new BadRequestException("预约失败，请稍后重试");
    }
    try {
        return ReservationResultCode.fromCode(rawCode.intValue());
    } catch (IllegalArgumentException e) {
        log.error("预约 Lua 返回未知码：{}", rawCode);
        throw new BadRequestException("预约失败，请稍后重试");
    }
}
```

**两道检查**：`rawCode` 为 null / 超出 int 范围 → 抛异常；落在 int 范围内但 `fromCode` 不认识（比如 Lua 里手滑 `return 9`）→ 也抛异常。两种情况都返回 `400 预约失败，请稍后重试`。

**例子里的对应**：学生 106 那次 `rawCode = 2` → `fromCode(2)` → `SOLD_OUT`。

方法注释：

```java
/**
 * 调用方已确认窗口开放：now ≤ bookingEndTime ≤ startTime < endTime，因此 Set 的 TTL 恒为正。
 */
```

---
---

# 六、`submit` 前半段 —— 跟着学生 102 走一遍

`ReservationServiceImpl.java:79-138`

## 6.1 七项前置检查

```java
if (batchId == null) throw new BadRequestException("预约批次不存在");                    // ① 400
UserDTO user = UserHolder.getUser();
if (user == null) throw new ForbiddenException("请先登录");                             // ② 403

ReservationBatch batch = reservationBatchService.getById(batchId);
if (batch == null) throw new BadRequestException("预约批次不存在");                      // ③ 400
if (batch.getStatus() != ReservationBatchStatus.PUBLISHED)
    throw new BadRequestException("批次当前不可预约");                                   // ④ 400

Equipment equipment = equipmentService.getById(batch.getEquipmentId());
if (equipment == null
        || equipment.getStatus() != EquipmentStatus.AVAILABLE
        || !Boolean.TRUE.equals(equipment.getBookingEnabled()))
    throw new BadRequestException("设备当前不可预约");                                   // ⑤ 400

LocalDateTime now = LocalDateTime.now();
if (now.isBefore(batch.getBookingStartTime()))
    throw new BadRequestException("预约尚未开始");                                       // ⑥ 400
if (now.isAfter(batch.getBookingEndTime()))
    throw new BadRequestException("预约已截止");                                         // ⑦ 400
```

**学生 102 逐条过一遍**（请求体 `{"batchId": 7}`）：

| 检查 | 实际比较 | 结果 |
|---|---|---|
| ① | `batchId = 7` 非 null | 通过 |
| ② | `UserHolder.getUser()` 里有 102 | 通过 |
| ③ | `getById(7)` 查到了批次 | 通过（1 次查库） |
| ④ | `PUBLISHED == PUBLISHED` | 通过 |
| ⑤ | `getById(3)` 查到设备，`AVAILABLE` 且 `booking_enabled = true` | 通过（第 2 次查库） |
| ⑥ | `09:00:00 < 09:00:00` → false | 通过 |
| ⑦ | `09:00:00 > 18:00:00` → false | 通过 |

**两次查库**：`batch` 和 `equipment`。

**⑥⑦ 和第 101 行的 `now` 是同一个变量**——`now` 只取一次，后面拼 Lua 参数也用它（就是 `ARGV[2] = 1791334800`）。

**④⑥⑦ 和 Lua 里的 1/4/5 是三对重复判定**：

| Java 侧 | Lua 侧 | 为什么要判两遍 |
|---|---|---|
| ④ `status != PUBLISHED` | 1 `EXISTS quota` | Java 查的是 MySQL 快照；判完到 Lua 执行之间，管理员可能关了批次（**变体 C**） |
| ⑥ `now < bookingStartTime` | 4 `now < bookStart` | 理论上同一秒不会变，但保持一致 |
| ⑦ `now > bookingEndTime` | 5 `now > bookEnd` | 同上 |

**变体 B 是 Java 拦下的**（⑥ 抛 400，Lua 根本没被调用）；**变体 C 是 Lua 拦下的**（Java 放行后状态才变）。**两层各自拦住不同的窗口，不是冗余。**

## 6.2 生成 id + 写账本

```java
long reservationId = redisIdWorker.nextId("reservation");                    // ⑧

try {
    reservationRequestService.createPreAccepted(reservationId, user.getId(), batchId);   // ⑨
} catch (RuntimeException e) {
    log.error("预约请求账本创建失败：reservationId={}，userId={}，batchId={}",
            reservationId, user.getId(), batchId, e);
    throw new ServiceUnavailableException("预约失败，请重试");                // 503
}
```

**⑧ 算出来的值**（展开见 §7）：`reservationId = 645827360351847424`。

**⑨ `createPreAccepted` 只做一件事：往 `tb_reservation_request` 插一行。** 学生 102 那次插进去的行：

| `request_id` | `user_id` | `batch_id` | `status` | `fail_reason` |
|---|---|---|---|---|
| `645827360351847424` | 102 | 7 | `PRE_ACCEPTED` | NULL |

**这一行是在抢名额之前写的。** 也就是说：**先往账本写一条「我要预约」，再去 Redis 抢名额。**

失败抛 `ServiceUnavailableException` → `WebExceptionAdvice` 映射成 **HTTP 503**。

## 6.3 抢名额

```java
ReservationResultCode resultCode = reservationQuotaExecutor.tryAcquire(batch, user.getId(), now);   // ⑩
```

学生 102 拿到 `SUCCESS`；学生 106 拿到 `SOLD_OUT`。

## 6.4 抢失败：补偿账本（用学生 106 的例子）

```java
if (resultCode != ReservationResultCode.SUCCESS) {
    log.warn("预约名额抢占被拒：batchId={}, userId={}, resultCode={}",
            batchId, user.getId(), resultCode);
    try {
        boolean compensated = reservationRequestService.casStatusWithFailReason(
                reservationId,
                ReservationRequestStatus.COMPENSATED,      // 目标状态
                resultCode.name(),                          // failReason = 枚举名，如 "SOLD_OUT"
                ReservationRequestStatus.PRE_ACCEPTED);     // 期望状态
        if (!compensated) {
            log.error("预约名额抢占被拒后账本补偿失败：reservationId={}，resultCode={}",
                    reservationId, resultCode);
        }
    } catch (RuntimeException e) {
        log.error("预约名额抢占被拒后账本补偿异常：reservationId={}，resultCode={}",
                reservationId, resultCode, e);
    }
    throw new BadRequestException(resultCode.getMessage());   // 用枚举里的 message
}
```

**学生 106 走这一支**：他 §6.2 插的那行账本，被这条 SQL 改掉：

```sql
UPDATE tb_reservation_request
   SET status = 'COMPENSATED', fail_reason = 'SOLD_OUT'
 WHERE request_id = 645827...（106 那次的 id）
   AND status = 'PRE_ACCEPTED'
```

改完那一行变成：

| `request_id` | `user_id` | `batch_id` | `status` | `fail_reason` |
|---|---|---|---|---|
| `645827...`（106 的） | 106 | 7 | **`COMPENSATED`** | **`SOLD_OUT`** |

然后抛 `BadRequestException("名额已约满")` → `400`。

三点：

- **`fail_reason` 存的是枚举名字符串**（`"SOLD_OUT"`），不是中文 message（中文 message 只用来回给前端）。
- **补偿失败了只打 error 日志**，然后照样抛 400。账本停在 `PRE_ACCEPTED`，会被对账扫到（08 篇）。
- **这里不需要归还 Redis 名额**——因为 Lua 返回非 0 时**根本没有 `DECR`**（§3.4 讲过学生 106 停在 `GET` 之后）。**这就是「失败路径不用补偿 Redis」的全部理由。**

## 6.5 抢成功

```java
    publishReservationMessage(reservationId, user.getId(), batchId, now);   // ⑪ 06 篇
    return reservationId;                                                    // ⑫ 返回给前端
```

**接口返回的是 `reservationId`**（`ReservationController:29` → `Result.ok(reservationService.submit(request.getBatchId()))`），不是预约单 id。前端拿到它去查「我的预约」。

请求体只有一个字段（`dto/ReservationSubmitDTO.java`）：

```json
{"batchId": 7}
```

**学生 102 走完整条路之后，三个地方的状态**：

| 位置 | 状态 |
|---|---|
| Redis | `quota:7 = "3"`，`users:7 = {101,102}` |
| MySQL `tb_reservation_request` | 1 行，`⑨` 写进去是 `PRE_ACCEPTED`；`⑪` 投递拿到 broker ACK 后 CAS 成 `PUBLISHED`（06 篇） |
| MySQL `tb_reservation` | **还没有行** —— 落库要等消费者，也在 06 篇 |
| HTTP | `200` + `645827360351847424` |

**注意「HTTP 已经返回 200，但预约单还不存在」** —— 这是异步落库的正常状态，用户此时去查「我的预约」可能查不到，几秒后才有。

---
---

# 七、`RedisIdWorker.nextId` —— 那个 id 是怎么来的

`utils/RedisIdWorker.java`

```java
private static final long BEGIN_TIMESTAMP = 1640995200L;   // 2022-01-01 00:00:00 UTC
private static final int  COUNT_BITS = 32;

public long nextId(String keyPrefix) {
    LocalDateTime now = LocalDateTime.now();                 // 例子：2026-10-07T09:00:00
    long nowSecond = now.toEpochSecond(ZoneOffset.UTC);      // ① 用 UTC → 1791363600
    long timestamp = nowSecond - BEGIN_TIMESTAMP;            // ② → 150368400

    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));   // ③ → "2026:10:07"
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);   // ④ → 1024

    return timestamp << COUNT_BITS | count;                  // ⑤ → 645827360351847424
}
```

**把学生 102 的数字代进去：**

| 步 | 表达式 | 值 |
|---|---|---|
| ① | `LocalDateTime(2026-10-07T09:00:00).toEpochSecond(ZoneOffset.UTC)` | `1791363600` |
| ② | `1791363600 − 1640995200` | `150368400` |
| ③ | 当天日期 | `"2026:10:07"` |
| ④ | `INCR icr:reservation:2026:10:07` | `1024`（假设当天第 1024 个请求） |
| ⑤ | `150368400 << 32 \| 1024` | **`645827360351847424`** |

**⑤ 是位运算拼接**：`150368400`（32 位以内）左移 32 位，低位填当天序号 `1024`：

```
高位 32 bit = 150368400   （距 2022-01-01 的秒数）
低位 32 bit = 1024        （当天第几个）
```

**这不是雪花算法**：没有机器号、没有毫秒级、没有同毫秒内的时钟回拨处理。它是「**秒级时间戳 + 按天自增计数**」。

**③④ 按天分 key**，所以每天从 1 重新计数，`icr:reservation:2026:10:08` 是另一个计数器。

**⚠️ 一个时区上的不一致**：同一个 09:00，两个人算出了不同的数：

| 谁 | 用的时区 | 算出的 epoch 秒 |
|---|---|---|
| `RedisIdWorker:nowSecond` | `ZoneOffset.UTC` | **1791363600** |
| `ReservationQuotaExecutor.toEpochSecond` → `ARGV[2]` | `ZoneId.systemDefault()`（+08:00） | **1791334800** |

**差 `28800` 秒 = 8 小时**，正好是时区偏移。两者**不互相比较**（一个用来拼 id，一个用来在 Lua 里比窗口），所以现在没出问题；但同一个请求里两个时间基准不同，是一个需要知道的点。

**`reservationId` 同时被当作 `requestId` 用**——`createPreAccepted(reservationId, ...)` 的第一个参数就是它，`tb_reservation_request` 的主键也是这个值。见 07 篇。

---
---

# 八、速查

## 8.1 学生 105 成功那条路

```
POST /reservation  {"batchId": 7}        userId=105
  │
  ├─ ① batchId != null                      ✓
  ├─ ② 已登录                               ✓
  ├─ ③ batch 7 存在                          ✓ (查库1)
  ├─ ④ status == PUBLISHED                  ✓
  ├─ ⑤ equipment 3 AVAILABLE & enabled      ✓ (查库2)
  ├─ ⑥ now(09:00) >= bookingStart(09:00)    ✓
  ├─ ⑦ now(09:00) <= bookingEnd(18:00)      ✓
  │
  ├─ ⑧ reservationId = 645827360351847424   ← 1791363600-1640995200 << 32 | 1024
  ├─ ⑨ INSERT tb_reservation_request (PRE_ACCEPTED)     失败 → 503
  │
  ├─ ⑩ EVAL reservation.lua 2 quota:7 users:7 105 1791334800 1791334800 1791367200 198000
  │        EXISTS=1 → 窗口通过 → GET="1">0 → SISMEMBER=0
  │        → DECR (1→0) + SADD {…105} + EXPIRE 198000
  │        → 返回 0 SUCCESS
  │
  └─ ⑪ publishReservationMessage(...)   ← 06 篇
     return 645827360351847424          → 200
```

## 8.2 学生 106 失败那条路（和上面只差第 ⑩ 步）

```
  ├─ ⑩ EVAL ... 106 1791334800 ...
  │        EXISTS=1 → 窗口通过 → GET="0" → tonumber("0") <= 0 → return 2
  │        （没有 DECR，Redis 一个字节都没动）
  │
  ├─ CAS UPDATE tb_reservation_request
  │     SET status='COMPENSATED', fail_reason='SOLD_OUT'
  │   WHERE request_id=<106那次的id> AND status='PRE_ACCEPTED'
  │
  └─ throw BadRequestException("名额已约满")   → 400
```

## 8.3 Lua 返回码 → 枚举 → HTTP

| 码 | 枚举 | message | 结果 |
|---|---|---|---|
| 0 | `SUCCESS` | — | 继续投递（06 篇） |
| 1 | `BATCH_NOT_OPEN` | 批次未开放预约 | 400 |
| 2 | `SOLD_OUT` | 名额已约满 | 400 |
| 3 | `DUPLICATE` | 你已预约过该批次 | 400 |
| 4 | `BOOKING_NOT_STARTED` | 预约尚未开始 | 400 |
| 5 | `BOOKING_EXPIRED` | 预约已截止 | 400 |

**`fail_reason` 存的是枚举名**（`SOLD_OUT` 等），不是中文。

**「谁拿到哪个码」**：0 → 101~105；2 → 106；3 → 101 的第二次；4/5 → Java 侧先拦住了，实际很少走到 Lua（只有 Java 判完后时间跨过边界才会）；1 → 批次在使用前被 `close`/`cancel`。

## 8.4 key 与常量

| | 值 |
|---|---|
| quota key | `reservation:batch:quota:{batchId}`，String |
| users key | `reservation:batch:users:{batchId}`，Set |
| TTL | `endTime + 24h − now`（例子：198000 秒 = 55 小时） |
| TTL 谁设 | quota 在 `publish` 设一次；users 每次抢成功 `EXPIRE` 重设 |

| | 值 |
|---|---|
| `BEGIN_TIMESTAMP` | `1640995200`（2022-01-01 UTC） |
| 移位 | `<< 32` |
| 计数 key | `icr:reservation:yyyy:MM:dd`（每天从 1 重数） |
| 时区 | `ZoneOffset.UTC`（而 Lua 的 `now` 用 `systemDefault()`，两者差 8 小时） |
