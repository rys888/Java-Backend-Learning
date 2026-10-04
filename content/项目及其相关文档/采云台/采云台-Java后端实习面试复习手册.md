# 采云台——Java 后端实习面试复习手册

> **事实边界**：本手册以 `backend/cai-yun-tai` 当前 Java、Mapper XML、SQL 迁移脚本和 Nginx 配置为准。`💡` 表示我知道的改进方案，**不能说成项目已经实现**。

## 目录

0. 简历真实性检查  
1. 一分钟项目介绍  
2. 项目整体架构  
3. M1：JWT + Redis 登录认证  
4. M4：角色权限与 AOP  
5. M2：部门预算并发控制  
6. M3：申领单核心链路  
7. Spring 事务  
8. Redis SET NX 防重复提交  
9. 申领单状态机  
10. Redis Cache-Aside  
11. Redis 三大缓存问题  
12. Redis 数据结构  
13. Redis KEYS 与 SCAN  
14. N+1 查询  
15. MySQL 与索引  
16. MyBatis  
17. Spring AOP 与自动填充  
18. 全局异常处理  
19. 申领车  
20. 如果面试官开始攻击我的项目  
21. 为什么不用 XXX  
22. Java 八股如何从项目延伸  
22.1 源码深挖追问题（扩充）  
23. TOP 30 高频题  
24. 面试前 30 分钟速记

---

# 0. 简历真实性检查

| 简历表述 | 结论 | 源码依据与面试边界 |
|---|---|---|
| JWT + Redis 白名单、Interceptor、ThreadLocal、注解 + AOP 三级权限 | ⚠️ 可以写，但必须知道局限 | 管理端 `token`、员工端 `authentication`，两套 HS256 密钥、两类拦截器、`login:token:{token}`、`BaseContext`、`@RequireRole`/`RoleAspect` 均真实存在。权限是**未标注即放行**，管理端有若干读接口未标注；密钥硬编码、密码无盐 MD5。 |
| MySQL 条件 UPDATE + InnoDB 行锁 + 影响行数避免预算超扣 | ✅ 可以放心写 | `BudgetMapper.deduct` 将余额条件放到 `WHERE`，Service 用受影响行数判定。不要夸大成“全链路预算幂等”：返还路径仍是先查订单再更新，存在并发重复返还窗口。 |
| `@Transactional` 保证预算预扣、主从单落库、车清理；服务端金额重算 + Redis SET NX | ⚠️ 可以写，但需改口径 | `submitOrder()` 的数据库四步在事务内；金额从**数据库购物车**的 `amount × number` 计算，未信任前端 `amount`。`SET NX` 在 Controller，key 为 `order:submit:{empId}`、TTL 5 秒，只是短时间防双击/限流，不是严格幂等，Redis 不会随 MySQL 回滚。 |
| Cache-Aside + 随机 TTL、空值短 TTL、主动失效 | ⚠️ 可以写，但必须说明缺口 | Goods/Combo Controller 手写缓存，30 分钟 + 0~299 秒抖动，空列表 60 秒；管理端写后删除 key。使用了 `KEYS`，无击穿锁、删除失败补偿；停售商品联动停售组合包时只清 goods 缓存，可能留下 combo 旧缓存。 |

**建议放在简历中的更精确版本**：

> 以 JWT + Redis 登录态实现管理端/员工端双端认证，并通过 Interceptor 写入 ThreadLocal、注解 + AOP 实现角色校验；以 MySQL 条件 UPDATE 和影响行数完成部门预算预扣；在事务内完成预算预扣、申领单主从表落库和申领车清理；对物资、组合包采用手写 Cache-Aside，并实现空值缓存、TTL 抖动与写后失效。

---

# 1. 一分钟项目介绍

## Q1：请你简单介绍一下采云台这个项目。

**参考回答：**

“采云台是一个企业内部办公物资申领与采购平台，前后端分离。员工在员工端浏览物资或组合申领包，加入申领车并提交申领；系统按部门月度预算预扣额度，采购专员或管理员再完成审批、采购、配送和核销。我的重点是后端的认证、预算并发和申领主链路：双端分别用 JWT 做身份凭证，再用 Redis 登录态支持主动登出；提交时金额由后端根据购物车重算，用 MySQL 条件 UPDATE 原子预扣预算，并用事务把预算、订单主从表和清车放在一起。物资和组合包还做了 Cache-Aside 缓存。它不是高并发生产系统，我也会主动说明当前状态流转和缓存一致性还有可优化点。”

源码状态：✅ 当前项目已实现；⚠️ 缺陷边界已如实说明。

---

# 2. 项目整体架构

## Q2：为什么采用 Controller / Service / Mapper 分层？一次请求如何走到数据库？

**参考回答：**

“Controller 负责 HTTP 参数、调用服务和返回 `Result`；Service 放业务编排、权限后的业务校验和事务；Mapper 只表达 SQL 与对象映射。以提交申领为例：浏览器经 Nginx 的 `/api/` 反代到 `/user/**`，员工端 JWT 拦截器验证 token、Redis 登录态和员工状态，写入 `BaseContext`；Controller 做 5 秒 SET NX；Service 查地址和购物车、计算金额、扣预算、插 orders 和 order_detail、清购物车；Mapper 最终执行 MyBatis SQL。这样 Controller 不会变成巨型业务类，事务也能覆盖多个数据库操作。”

```text
Browser → Nginx:8083 /api/ → Spring MVC
→ JwtTokenUserInterceptor → BaseContext(ThreadLocal)
→ User OrderController → OrderServiceImpl(@Transactional)
→ Mapper / MyBatis XML → MySQL(InnoDB)
```

源码状态：✅ 当前项目已实现。

### 追问 1：DTO、Entity、VO 分别是什么？

**答案：**“DTO 是输入，例如 `OrdersSubmitDTO`；Entity 对应持久化对象，例如 `Orders`、`Budget`；VO 是输出，例如 `OrderSubmitVO`、`OrderVO`。分开能避免把表字段和接口契约绑死，也不让客户端提交内部字段。”

### 追问 2：为什么业务逻辑和事务通常放 Service？

**答案：**“Service 是用例边界，可组合多个 Mapper。`submitOrder` 要扣预算、插主单、插明细、删购物车，放 Controller 会难测且事务边界不清。Spring 的事务代理也通常代理 Service 的 public 方法。”

## Q3：项目有哪些核心表？为什么 orders 和 order_detail 分表、requester_dept 要冗余？

**参考回答：**

“核心有 employee、department、budget、dish/`dish_flavor`、setmeal/`setmeal_dish`、shopping_cart、orders、order_detail、address_book。orders 存一张申领单的公共信息，order_detail 存多条物资快照，属于一对多，避免重复存订单号、地址、状态。`requester_dept` 在下单时从 employee 的 deptId 写入 orders，是有意冗余：后续按部门统计和预算返还不依赖员工现在仍属于原部门，减少联表和历史口径漂移。”

源码状态：✅ 当前项目已实现。

---

# 3. M1：JWT + Redis 登录认证

## Q4：管理端和员工端登录流程是什么？为什么双端认证？

**参考回答：**

“两个端都复用 employee 表和账号密码，但入口与权限边界不同。管理端 `/admin/employee/login` 调 `login()`，普通 EMPLOYEE 会被拒绝；员工端 `/user/user/login` 调 `staffLogin()`，所有启用员工都能登录。成功后都只把 `empId` 写入 JWT claim，分别使用 admin/user 的 SecretKey 和请求头，Redis 写 `login:token:{原始token}` 到 employeeId，TTL 都与 JWT 的 2 小时一致。这样同一个账号可以有两个端各自独立的登录态，也避免员工 token 被管理端拦截器当成管理 token 解析。”

源码状态：✅ 当前项目已实现。

### 追问 1：JWT 结构、签名和 claims 是什么？为什么只放 empId？

**答案：**“JWT 是 `Header.Payload.Signature` 三段 Base64URL 编码；这里 HS256 是**签名校验完整性**，不是加密，payload 不能放敏感信息。当前 claims 只有 `empId`，密码绝不能进 token；role 也没有放，因为每次请求会从 employee 表查当前角色和禁用状态，改角色或禁用能立即生效。”

### 追问 2：两套 SecretKey、两种请求头是什么？TTL 多久？

**答案：**“配置里管理端 header 是 `token`、员工端是 `authentication`；各自密钥分别为 admin/user secret，TTL 均是 7,200,000 ms，也就是 2 小时。隔离降低跨端 token 混用；但当前密钥直接写在 `application.yml`，生产应环境变量或密钥服务托管并轮换。”

源码状态：⚠️ 双端隔离已实现；密钥管理有缺陷。

## Q5：JWT 已能验签，为什么还要 Redis 白名单？退出时发生什么？

**参考回答：**

“纯 JWT 在过期前很难主动撤销。项目登录后把 `login:token:{token}` 写 Redis，value 是 employeeId、TTL 同 JWT；拦截器必须同时通过 JWT 验签和 Redis key 存在才放行。logout 只是 DEL 这个 key，所以未过期旧 token 下一次请求就 401。Redis key 先过期时，JWT 虽没过期也失效；JWT 先过期时解析失败，Redis 的残余 key 最多等 TTL 自然过期。Redis 宕机时当前实现读取异常后直接 401，属于 fail-closed，可用性会受影响。”

源码状态：✅ 当前项目已实现；⚠️ 没有 Redis 高可用/降级策略。

### 追问：JWT + Redis 和 Session 有什么区别？

**答案：**“Session 通常服务端保存完整会话、Cookie 仅带 sessionId；JWT 自带签名声明，适合无状态验签和跨服务传递。这个项目又加 Redis 登录态，因此并非纯无状态 JWT，而是用较少的 Redis 状态换取主动注销能力。它的代价是每次请求多一次 Redis 查询和 Redis 可用性依赖。”

## Q6：Interceptor 做了什么？为什么还查 employee？为什么 401？

**参考回答：**

“`preHandle` 先从对应 header 取 token，按对应密钥解析 JWT 取得 empId，检查 Redis 登录 key，然后 `employeeMapper.getById` 查账号是否存在、是否禁用；管理端还拒绝 EMPLOYEE。通过后写 `BaseContext.currentId/currentRole`，供 Service 与 AOP 用；失败就设置 HTTP 401。不能只信 JWT，因为 token 中没有实时角色，且账号可能已被禁用或角色已调整。`afterCompletion` 调 `BaseContext.clear()`，保证线程复用时不会串身份。”

源码状态：✅ 当前项目已实现。

## Q7：BaseContext 为什么用 ThreadLocal？不 remove 有什么问题？

**参考回答：**

“下游 Service、自动填充切面都需要当前人 id，逐层传参很冗长，所以项目在拦截器把 id、role 放 ThreadLocal。每个线程有自己的 ThreadLocalMap，因此同一时刻请求隔离；Tomcat 线程池会复用工作线程，请求结束不 remove，下个请求可能读到旧身份，也可能因 value 被长期线程持有造成泄漏。这里两个拦截器都在 `afterCompletion` 调 `BaseContext.clear()`。”

源码状态：✅ 当前项目已实现。

### 项目延伸题

**Q：ThreadLocal 为什么还会内存泄漏？**  
**答：**“ThreadLocalMap 的 key 是弱引用，ThreadLocal 对象被回收后 key 可能为 null，但 value 仍被线程强引用；在线程池中线程很长寿，value 可能滞留。最可靠做法是在 finally/afterCompletion 调 `remove()`，不能只依赖弱引用。”

**Q：ThreadLocalMap 如何处理冲突？**  
**答：**“它按 threadLocal hash 定位数组槽位，冲突时线性探测；扩容前会清理陈旧 entry。面试里重点仍是线程隔离与 remove。”

---

# 4. M4：角色权限与 AOP

## Q8：认证和授权有什么区别？为什么认证放 Interceptor、授权放 AOP？

**参考回答：**

“认证回答‘你是谁’，项目放 Interceptor：验 JWT、Redis 登录态、账号状态并写上下文。授权回答‘你能不能做’，项目用 `@RequireRole` + `RoleAspect`：ADMIN 可维护员工、预算、物资、部门，PURCHASER 与 ADMIN 可审批、配送、核销，EMPLOYEE 走员工端申领。HTTP 层所有请求都适合先认证；授权是方法级横切规则，注解加 AOP 比每个 Controller 手写 if 更集中。”

源码状态：✅ 当前项目已实现。

### 追问 1：自定义注解如何定义、切面如何取到它？

**答案：**“`@RequireRole` 用 `@Target({METHOD,TYPE})` 允许标方法或类，用 `@Retention(RUNTIME)` 让运行时反射可见，value 是允许角色数组。`RoleAspect` 用 `@Before` 命中方法/类注解，再从 `MethodSignature` 拿 Method，优先方法注解、否则类注解，读取 `BaseContext.getCurrentRole()` 比较。”

### 追问 2：Spring AOP、JDK Proxy、CGLIB？

**答案：**“Spring AOP 通常是运行时代理，调用先经过代理织入通知。目标有接口一般可用 JDK 动态代理，代理接口；没有接口可用 CGLIB 生成子类。CGLIB 不能代理 final 类/方法。这里关键是 `@Before` 在进入受保护 Controller 方法前做检查。”

## Q9：当前权限系统有什么不足？如何改成默认拒绝？

**参考回答：**

“最大风险是‘未标注即放行’，漏写注解就越权。当前管理员的部分读接口，比如 employee page/detail、order search/statistics/details，没有 `@RequireRole`；它们仍经过管理端登录，但采购专员可读。另一个实际问题是管理端 order details 调了带 `assertOwner` 的用户详情 Service，采购员查看他人详情会失败。改造时可按路径/控制器给默认角色，或维护权限白名单并在 AOP 中默认拒绝；再为管理端和员工端分别写明确的查询 Service，做接口权限测试。”

源码状态：⚠️ 当前实现存在缺陷。

### 追问：为什么不用 Spring Security？

**答案：**“这个实习项目接口少、角色固定为三类，已有 MVC Interceptor + 注解切面的教学成本低、代码直观。Spring Security 更适合复杂认证链、多种认证方式、细粒度授权和成熟安全能力；不是‘性能差’而没用。规模变大时我会迁移到它，并使用默认拒绝策略。”

---

# 5. M2：部门预算并发控制

## Q10：真实的预算扣减 SQL 是什么，为什么能防超扣？

```sql
UPDATE budget
SET used_amount = used_amount + #{amount}
WHERE dept_id = #{deptId}
  AND period = #{period}
  AND status = 1
  AND total_amount - used_amount >= #{amount};
```

**参考回答：**

“预算表以 `(dept_id, period)` 唯一，一行表示一个部门一个月的总额和已用额，金额是 `DECIMAL(12,2)` 对应 Java `BigDecimal`。我不先 SELECT 余额再 UPDATE，因为两个线程都可能读到同一余额。这里把余额判断和加已用额放进同一条 UPDATE，InnoDB 在更新目标记录时加行锁，影响行数 1 表示扣成功，0 表示预算不存在、停用或余额不足。关键不只是 UPDATE 原子，而是余额条件在 WHERE 里，在拿到锁后的当前版本上重新判断。”

源码状态：✅ 当前项目已实现。

### 追问：为什么不能 Float/Double，为什么唯一索引重要？

**答案：**“二进制浮点不能精确表达多数十进制小数，预算会产生精度误差；所以数据库 DECIMAL，Java BigDecimal。唯一索引保证同部门同周期只有一条事实记录，也让条件 UPDATE 的目标明确；Service 里的先查只是友好提示，真正约束仍应由唯一索引兜底。”

## Q11：并发时序——余额 100，T1 和 T2 同时各申请 80，会怎样？

```text
T1: UPDATE ... AND 100 - used >= 80
    ↓ 获取 budget 该行 X 锁，条件成立
    ↓ used: 0 → 80，影响 1 行，提交时释放锁

T2: 同一 UPDATE
    ↓ 等待同一行锁
    ↓ T1 提交后在当前版本重新判断：100 - 80 >= 80 为假
    ↓ 更新 0 行 → BudgetService 返回 false → 业务报“预算不足”
```

**参考回答：**

“最终只有一笔成功，所以不会超扣到 160。若没有 WHERE 中的余额条件，T2 等锁后仍会执行加 80，反而会超扣；因此不能只说‘UPDATE 天然安全’。”

源码状态：✅ 当前项目已实现。

### 追问：为什么不用 synchronized、ReentrantLock、Redis 锁或把预算放 Redis？

**答案：**“JVM 锁只能保护单实例，扩容后失效；Redis 锁增加续租、超时和异常释放复杂度，而预算事实最终仍在 MySQL。当前操作是一行条件更新，MySQL 已提供原子判断和持久化，最小方案更可靠。Redis 可以做缓存，不能替代预算事实来源。`SELECT ... FOR UPDATE` 也能做，但会把读、判断、写拆成多步并拉长锁时间；当前条件 UPDATE 更短。”

## Q12：驳回、撤销、退换如何返还预算？当前是否真正幂等？

**参考回答：**

“驳回、员工撤销、管理员取消会在事务内调 `release`：`used_amount = used_amount - amount AND used_amount >= amount`，并把订单 payStatus 写为 REFUND。退换只写状态 6 和 `isReturned=1`，明确不立即返还，留给线下确认。当前不是严格幂等：两条并发取消路径可能都先读到 PAID，然后都执行 release；余额足够时两次都成功，最后普通 UPDATE 才都写 REFUND。应把订单更新改为 `WHERE id=? AND pay_status=PAID AND status IN (...)`，先抢到状态迁移权的一方再返还，或引入唯一的 budget_log。”

```sql
-- 💡 当前未实现：用状态条件更新抢占返还权
UPDATE orders
SET status = ?, pay_status = 2, cancel_time = NOW()
WHERE id = ? AND pay_status = 1 AND status = 2;
```

源码状态：⚠️ 返还 SQL 有下限保护，但订单级幂等未完成；💡 budget_log 未实现。

---

# 6. M3：申领单核心链路

## Q13：用户点击提交以后，后端到底发生了什么？

**参考回答：**

“请求从员工端经 Nginx 到 `/user/order/submit`。员工拦截器验员工端 JWT、Redis 登录 key、employee 状态后，把 empId 和 role 放 BaseContext。Controller 以 `order:submit:{empId}` 做 5 秒 SET NX，挡住双击。进入 `submitOrder` 的事务后，先看 Redis 采购开关，按 id 查地址，按当前用户查购物车；从购物车金额和数量计算总额，再查 employee 取部门和当月 period。接着执行预算条件 UPDATE，失败就抛异常回滚。成功后生成 Redis 日序号订单号，插入 orders，MyBatis 回填 id，批量插 order_detail，最后删除当前人的购物车，返回订单 id、号、时间和金额。任何 RuntimeException 导致 MySQL 事务中预算、主单、明细、清车一起回滚。”

源码状态：✅ 主数据库链路已实现；⚠️ Redis 操作不参与该事务。

### 追问 1：为什么金额必须后端算？

**答案：**“前端请求可被篡改，不能相信它传的 total amount。当前项目不使用 DTO 里的金额，而是取数据库购物车 `amount × number` 求和。要如实补一句：购物车保存的是加入时价格，提交时没有回查物资/组合包当前价；如果要严格按现价结算，应在事务内查商品有效性和当前价格。”

### 追问 2：地址、主键回填、批量插入和清车？

**答案：**“当前只按 `addressBookId` 查地址并复制 consignee/phone/detail 到订单快照，**未校验地址属于当前员工，这是缺陷**。orders XML 设置 `useGeneratedKeys=true keyProperty=id`，插主单后 id 回填；明细再用 `<foreach>` 一条批量 INSERT。清车放最后，且和前面 SQL 在同一 MySQL 事务中。”

---

# 7. Spring 事务

## Q14：`@Transactional` 在 submitOrder 中保障什么？Redis 为什么不随它回滚？

**参考回答：**

“`submitOrder` 标在 Service public 方法上，事务边界覆盖预算 deduct、orders insert、order_detail batch insert 和购物车 delete。预算扣成功但任一后续 DB 操作抛 RuntimeException，Spring 事务代理会让同一数据源连接回滚，预算不会留下占用。默认只回滚 RuntimeException/Error；项目取消、驳回等声明 `rollbackFor=Exception.class` 来覆盖 checked exception。Redis 的 SET NX、订单号 INCR、缓存读写不在 MySQL 连接事务里，MySQL 回滚不会删除 Redis key，这就是跨资源一致性边界。”

源码状态：✅ 当前项目已实现。

### 追问：哪些情况会让 `@Transactional` 失效？

**答案：**“常见是 private/final 方法、同类内部 `this.xxx()` 绕过代理、方法不是 Spring Bean 管理、异常被吞掉，或 checked exception 没配置 rollbackFor。这里 submitOrder 是 public 并由 Controller 调 Service 代理，属于正常路径。”

---

# 8. Redis SET NX 防重复提交

## Q15：SET NX 是什么？当前方案能保证幂等吗？

**参考回答：**

“NX 是 only if not exists。员工提交前写 `order:submit:{empId}`，5 秒 TTL，第一次返回 true 才进 Service，第二次返回 false 报重复提交。TTL 必须有，否则一次请求会永久锁住用户；当前不主动删，所以即使业务失败也要等 5 秒才能重试。它只防短时间同一员工的重复请求，不是严格幂等：key 不含 requestId，5 秒后重试仍能建新单，Redis 宕机也失效。事务保证一次请求内的 MySQL 原子；条件 UPDATE 防预算超扣；真正业务幂等应由 client requestId + orders 唯一索引共同保证。”

```text
SET NX + TTL       → 短时防双击/重试
@Transactional     → 一次请求内多条 MySQL SQL 原子
条件 UPDATE         → 预算不超扣
requestId 唯一索引  → 严格业务幂等（💡当前未实现）
```

源码状态：⚠️ 当前实现存在边界；💡 requestId 未实现。

---

# 9. 申领单状态机

## Q16：状态机是什么？当前状态怎么走，为什么不能随便 UPDATE status？

```text
2 待审批 ──审批通过──> 3 采购中 ──发货──> 4 配送中 ──核销/确认收货──> 5 已完成
   │                         │
   ├─驳回（返还预算）──> 6 已取消
   ├─员工撤销（返还预算）> 6 已取消
   └─管理员取消（返还预算）> 6 已取消

5 已完成 ──发起退换（不立即返还）──> 6 已取消，is_returned=1
```

**参考回答：**

“状态机把允许的业务迁移固定下来，例如待审批才能审批或驳回，采购中才能发货，配送中才能完成。当前代码是先 SELECT 当前状态、Java 判断、再按 id 普通 UPDATE，功能上校验了前置状态，但并发下两个请求可能都读到旧状态后都更新，属于 TOCTOU 问题。生产化应改成状态条件更新，用 affected rows 判断是否抢到迁移权；这就是轻量乐观并发控制，不一定非要 version 字段。”

```sql
-- 💡 当前未实现
UPDATE orders SET status = #{nextStatus}
WHERE id = #{id} AND status = #{expectedStatus};
```

源码状态：⚠️ 业务状态校验已实现；原子状态迁移未实现。

---

# 10. Redis Cache-Aside

## Q17：项目如何实现 Cache-Aside？为什么更新 DB 后删缓存而不是直接更新？

**参考回答：**

“项目没有 `@Cacheable`，是在员工端 Goods/Combo Controller 手写 Cache-Aside。先查 Redis，命中直接返回；未命中查 MySQL，空列表缓存 60 秒，正常列表缓存约 30 到 35 分钟。管理端新增、修改、删除、启停后，先完成数据库 Service，再删 `goods:list:*` 或 `combo:list:*`，下一次读回源重建。先更新 DB 再删缓存较简单，直接更新缓存要维护多种 category/all key 和序列化对象，漏一个更易不一致。它是最终一致，不是强一致：删缓存失败、并发读写都可能短暂旧读。”

源码状态：✅ 当前项目已实现；⚠️ 没有删除失败补偿。

### 追问：什么适合缓存？

**答案：**“当前的物资目录和组合包是读多写少、可容忍短暂旧数据，适合。预算余额、订单状态、登录态外的强一致资金事实不适合只靠缓存；预算必须以 MySQL 为准。”

---

# 11. Redis 三大缓存问题

## Q18：三大缓存问题在本项目中的处理？

**参考回答：**

“穿透是大量访问不存在 categoryId，缓存和 DB 都没有；项目把空 List 缓 60 秒。雪崩是大量 key 同时过期；项目用 30 分钟加 0~299 秒随机 TTL 分散失效。击穿是一个热点 key 失效时大量请求同时回源；当前没有互斥锁、逻辑过期或 single-flight，因此**没有真正解决击穿**。可用 `SET NX` 互斥重建或逻辑过期异步重建，但这是优化方案，不是现有实现。”

源码状态：✅ 穿透/雪崩基础处理已实现；💡 击穿治理未实现。

---

# 12. Redis 数据结构

## Q19：为什么物资列表缓存为整个 List，而不是 Hash/List/ZSet？

**参考回答：**

“这里的访问模式是‘按 categoryId 一次拿完整物资列表及规格’，所以 key 是 categoryId，value 序列化整个 `List<GoodsVO>`，一次 GET 就够。不是因为 String 天然简单：如果要按物资 id 单独更新/随机查，Hash 更合适；按队列消费用 List；按评分排名用 ZSet；Set 用去重成员关系。当前 RedisTemplate 未显式配置 value serializer，实际是默认 JDK 序列化，这会增加体积和跨语言可读性问题。”

源码状态：✅ 当前项目已实现；⚠️ 序列化配置可改进。

---

# 13. Redis KEYS 与 SCAN

## Q20：当前为什么要批量删缓存？`KEYS` 有什么风险，怎么改？

**参考回答：**

“管理端写目录后不知道受影响的是哪一个 category/all key，所以当前用 `redisTemplate.keys('goods:list:*')`/combo 前缀找出再 DEL，保证缓存广义失效。问题是 KEYS 会遍历整个 keyspace，Redis 主命令执行路径会被长时间占用，大数据量会阻塞其他请求。当前本地小数据没明显暴露，但上线应改 SCAN 分批游标遍历后删除，或维护精确 key/版本号。Redis I/O 常以单线程事件循环处理命令，并非‘所有工作绝对单线程’，但阻塞命令仍危险。”

源码状态：⚠️ 当前实现使用 KEYS；💡 SCAN 未实现。

---

# 14. N+1 查询

## Q21：项目中真实的 N+1 在哪里，如何优化？

**参考回答：**

“`GoodsServiceImpl.listWithSpecs` 先 `goodsMapper.list(goods)` 查 N 条物资，再 for 循环每个 goods 调 `getByGoodsId` 查规格，总 SQL 是 1+N。缓存命中时它不会发生，容易掩盖问题；Redis 冷启动、缓存失效时仍会打出 N+1。优化是先查全部 goods，再 `SELECT * FROM dish_flavor WHERE dish_id IN (...)`，在 Java 里 `groupingBy(GoodsSpec::getGoodsId)` 组装 VO，总共两条 SQL。”

源码状态：⚠️ 当前有 N+1；💡 两条 SQL 优化未实现。

---

# 15. MySQL 与索引

## Q22：当前有哪些关键索引？orders 还能怎样优化？

**参考回答：**

“当前迁移确认 budget 有主键、`(dept_id, period)` 唯一索引和 period 索引；department code 唯一；employee 有 role、dept_id 索引；orders 有 requester_dept、approve_user 索引，修复脚本还加了 number 唯一索引。budget 联合唯一索引既维护业务不变量，也支持按部门周期定位预算。orders 分页常按 user_id/status、order_time 排序，但迁移脚本没有证明存在对应联合索引；可按真实 EXPLAIN 和查询模式考虑 `(user_id,status,order_time)` 或按管理端筛选另建索引，不能在面试说已经加了。”

源码状态：✅ 上述索引存在迁移证据；💡 orders 组合索引为优化建议。

### 追问：B+Tree、聚簇索引、最左前缀、覆盖索引？

**答案：**“InnoDB 主键索引是聚簇索引，叶子放整行；二级索引叶子存二级键和主键，取非覆盖列可能要回表。B+Tree 非叶节点只存索引键，扇出大、树高低、叶子有序且链表适合范围查询。联合索引遵循最左前缀；若查询列都在二级索引中可覆盖查询，避免回表。”

---

# 16. MyBatis

## Q23：Mapper 接口为什么没有实现类？`#{}` 和 `${}` 有何区别？

**参考回答：**

“MyBatis 启动时为 `@Mapper` 接口创建动态代理，调用方法会按 namespace + method id 找 XML 或注解 SQL，做参数绑定和结果映射。项目 XML 用 `#{}` 预编译参数，例如预算 amount、动态 `<if>/<where>/<set>`；`${}` 是字符串拼接，若放用户输入易 SQL 注入，只适合严格白名单后的标识符。`OrderMapper.insert` 用 `useGeneratedKeys` 回填 orders.id；`OrderDetailMapper.insertBatch` 用 `<foreach>` 一次插多条；Combo XML 的 ResultMap 组装组合包和 items。”

源码状态：✅ 当前项目已实现。

### 追问：PageHelper 原理？

**答案：**“Service 先 `PageHelper.startPage(page,pageSize)`，它借助 MyBatis 插件拦截后续查询，改写为带 LIMIT 的分页 SQL 并做 count；Mapper 返回 Page，代码读 total 和 result。要紧贴 startPage 后立刻执行目标查询，避免错误拦截其他 SQL。”

---

# 17. Spring AOP 与自动填充

## Q24：项目如何自动填充 createTime / updateTime？AOP 与 Interceptor 区别？

**参考回答：**

“`@AutoFill` 标在部分 Mapper 的 insert/update 方法，`AutoFillAspect` 切 Mapper 包内带注解的方法，`@Before` 取得 `MethodSignature` 和操作类型，再用反射调用实体 setter 填 create/update 时间和 BaseContext 当前人。JoinPoint 代表一次方法连接点，MethodSignature 用于取得具体方法。AOP 是方法执行层的横切，适合自动填充和角色规则；Interceptor 是 MVC 请求处理链，适合 token 认证、写请求上下文。”

源码状态：✅ 当前项目已实现；⚠️ 反射失败只 warn，且并非所有写 Mapper 都标了 AutoFill。

---

# 18. 全局异常处理

## Q25：为什么要全局异常处理？当前有什么不足？

**参考回答：**

“`@RestControllerAdvice` 集中处理 `BaseException` 和 SQL 唯一约束异常，统一返回 `Result.error`，避免每个 Controller 重复 try/catch，也让业务异常能用一致 code/message 表达。认证失败是拦截器直接设 HTTP 401，这是和业务失败不同的 HTTP 语义。当前不足是 Advice 没有兜底 RuntimeException、参数校验等，也没有为业务异常设置合适 HTTP status；SQL 异常通过字符串拆 message 也较脆弱。”

源码状态：⚠️ 当前实现存在缺口。

---

# 19. 申领车

## Q26：申领车如何合并同商品？并发有什么问题？

**参考回答：**

“shopping_cart 按当前 user、goods/combo、goodsSpec 查询，同一项存在就 Java 里 `number+1` 后按 id 覆盖更新；不存在则查商品或组合包填名称、图片、价格并插入。规格不同作为不同 cart 项。问题是它是‘先查再改’：两个请求都读 number=1，分别写 2，最终仍是 2 而不是 3；并发发现不存在还可能插两行。优化是唯一索引约束 `(user_id,dish_id,setmeal_id,dish_flavor)` 的可空列设计需谨慎，再用 `INSERT ... ON DUPLICATE KEY UPDATE number=number+1`，或专门原子增减 SQL。”

源码状态：⚠️ 当前实现存在丢失更新风险；💡 原子 upsert 未实现。

---

# 20. 如果面试官开始攻击我的项目

以下每题都按“承认 → 原因 → 风险 → 改进”回答。

## Q27：你把 JWT 密钥和数据库密码写配置里，不安全吗？

**推荐回答：**“是，当前开发配置里密钥明文，这是实习项目本地运行的便利取舍，不是生产方案。风险是代码泄漏即可伪造 token 或暴露凭据。生产会改为环境变量/密钥管理服务，密钥轮换并避免日志输出 token。”  
源码状态：⚠️ 当前缺陷。

## Q28：MD5 存密码也有问题吧？

**推荐回答：**“有。当前是无盐 MD5，只能算演示级校验，容易被彩虹表和高速爆破。登录失败次数用了 Redis 5 次/15 分钟限制，但不能替代密码哈希。生产会采用 BCrypt/Argon2 加盐并逐步迁移旧密码。”  
源码状态：⚠️ 当前缺陷。

## Q29：缓存删失败怎么办？物资停售为什么组合包还可能旧？

**推荐回答：**“当前是写 DB 后 KEYS 删除，删失败会旧读到 TTL；停售商品联动停售组合包时确实只删 goods 缓存，是遗漏。小项目先选简单最终一致，风险是短暂展示不可申领组合包。改为 Service 事务提交后精准删除 goods/combo 两类 key，并加重试、消息或版本号。”  
源码状态：⚠️ 当前缺陷。

## Q30：SET NX 为什么不是幂等？

**推荐回答：**“它只用 employeeId 作 key 且 5 秒过期，防的是双击窗口；5 秒后同一业务可再提交，失败后也被锁 5 秒。真正幂等需要客户端 requestId，服务端持久化 requestId 并加唯一索引，重复请求返回第一次结果。”  
源码状态：⚠️ 当前缺陷。

## Q31：预算返还不是已经 `used_amount >= amount` 了吗，为什么仍可能重复？

**推荐回答：**“这个条件只能防 used_amount 变负，不能把某笔订单的返还变成一次。两个事务都先读到 payStatus=PAID 时，都可能成功 release。应先用带 payStatus/status 条件的 orders UPDATE 原子抢占返还权，再释放预算，或写 budget_log 并以 orderId 做唯一约束。”  
源码状态：⚠️ 当前缺陷。

## Q32：状态流转并发怎么办？地址会越权吗？

**推荐回答：**“状态当前是先读后写，应改条件 UPDATE；地址下单只按 id 查，也没有检查 userId，确实可能使用他人地址。改造为 Mapper 查询 `WHERE id=? AND user_id=?`，状态操作返回 affected rows 为 0 则报状态已变化。”  
源码状态：⚠️ 当前缺陷。

## Q33：为什么说管理端权限有问题？

**推荐回答：**“写接口多数已标注，但设计是默认放行，遗漏注解的读接口采购员可访问；此外管理端订单详情复用员工 owner 校验，功能上又会拒绝看别人的单。应将默认策略改拒绝、显式配置每个接口角色，并拆管理端详情查询。”  
源码状态：⚠️ 当前缺陷。

## Q34：N+1、KEYS、购物车并发，这些不是低级问题吗？

**推荐回答：**“是我明确识别的项目边界。小数据下缓存和单用户操作让风险不明显，但不应把它当生产级实现。分别会批量规格查询、SCAN 或精准 key 失效、原子自增/upsert 加唯一约束来解决，并用压测和 SQL 日志验证。”  
源码状态：⚠️ 当前缺陷。

---

# 21. 为什么不用 XXX？

## Q35：为什么不用 Redis 分布式锁 / Redisson 扣预算？

**参考回答：**“预算是一行 MySQL 事实数据，当前条件 UPDATE 已把校验和修改原子化，Redis 锁不会替代最终写库，还会带来过期、续租和故障处理。当前规模没必要引入 Redisson；跨多行复杂资源竞争时再评估。”  
源码状态：✅ 技术选型解释；Redisson 未使用。

## Q36：为什么不用 MQ、微服务、ES、Redis 购物车、数据库触发器？

**参考回答：**“当前是单体实习项目，提交链路要求同步给出预算不足结果，MQ 会增加最终一致、重试和幂等成本；服务规模和团队也不足以支撑微服务治理。目录搜索量不大，不需要 ES。购物车按用户持久化、提交要参与订单事务，因此落 MySQL 更直接。预算等业务规则放 Service + SQL 更可测试可追踪，触发器会隐藏逻辑。不是它们性能不好，而是当前需求、维护成本和一致性不值得。”  
源码状态：✅ 当前未引入这些技术。

## Q37：为什么不用 Session、version 乐观锁、Spring Cache？

**参考回答：**“JWT 便于两端 header 传递，Redis 登录态补主动失效；Session 也可行但依赖服务端会话管理。订单状态当前没有 version，条件 `WHERE status=?` 已能实现轻量 CAS，version 是更通用的选择。缓存选择手写 Cache-Aside 是为了展示 key、TTL、空值和失效细节；Spring Cache 能减少模板代码，但当前确实没有使用。”  
源码状态：⚠️ version 未实现；Spring Cache 未使用。

---

# 22. Java 八股如何从项目延伸

| 项目技术 | 面试官可能延伸 | 项目化回答要点 |
|---|---|---|
| ThreadLocal | ThreadLocalMap、弱引用、泄漏 | Interceptor afterCompletion 必须 remove |
| JWT | Session/Cookie、签名与加密 | HS256 签名；claims 仅 empId |
| Redis | 数据结构、持久化、淘汰 | 登录 String、列表序列化、TTL 与缓存问题 |
| MySQL | B+Tree、MVCC、行锁 | 预算条件 UPDATE + InnoDB 行锁 |
| Transactional | AOP、代理、传播/回滚 | Service public、DB 和 Redis 边界 |
| AOP | JDK Proxy/CGLIB | RoleAspect 与 AutoFillAspect |
| MyBatis | 动态代理、一级二级缓存 | XML if/where/set/foreach、PageHelper |
| BigDecimal | 浮点精度 | budget DECIMAL(12,2) |
| Nginx | 反向代理、负载均衡 | 8082 admin、8083 user 反代 8084 |

**Q：InnoDB 行锁和 MVCC 的关系？**  
**答：**“普通一致性读常借 MVCC 读版本；预算扣减是 UPDATE，需要当前读并对目标记录加排他锁。T2 等 T1 后在最新数据上判断 WHERE，所以条件不成立更新 0 行。”

---

# 22.1 源码深挖追问题（扩充）

> 这一节不是为了堆八股，而是从当前代码再向下挖一层。答案中凡是“应当/可以”均为改进，不能误说成既有实现。

## Q68：登录失败次数限制是怎么做的？它能防住什么，防不住什么？

**参考回答：**

“`EmployeeServiceImpl.checkLogin` 以用户名构造 `login:fail:{username}`。每次用户名不存在或密码错误就 Redis INCR；第一次失败再设置 15 分钟 TTL，达到 5 次后直接拒绝，登录成功会 DEL 计数。它是分布式共享的失败计数，比单机内存计数更适合多实例。它能降低对同一用户名的撞库，但不能防大量不同用户名、IP 分布式攻击，也没有验证码、IP 限流或账户锁定审计。”

源码状态：✅ 当前项目已实现；💡 IP 限流/验证码未实现。

## Q69：为什么禁用账号后旧 JWT 立刻不能用？为什么仍保留 Redis token？

**参考回答：**

“每次受保护请求除验 JWT 和 Redis key 外，都会按 empId 查 employee，并检查 status；管理员禁用账号后，下次请求就 401，即使 Redis key 和 JWT 尚未到期。Redis token 并不会在禁用动作中批量删除，保留到自然过期没有认证权限；这是功能正确但不够节省的实现。若要主动清理，可维护 employeeId 到 token 集合或 token version。”

源码状态：✅ 禁用即时拒绝已实现；💡 批量清 token 未实现。

## Q70：为什么 `OrdersSubmitDTO` 有 amount，项目又不使用它？

**参考回答：**

“DTO 保留了原业务字段，但 `submitOrder` 后面显式用购物车的 amount 乘 number 覆盖到 orders.amount，没有信任客户端传的 total amount。这体现服务端金额计算原则。需要诚实补充：DTO 的冗余字段容易误导维护者，最好删除它或在注释中明确 deprecated；并且购物车价格是入车时快照，不是提交时商品现价。”

源码状态：⚠️ 防前端金额篡改已做到；DTO 冗余和现价校验未处理。

## Q71：下单时为什么要复制地址、名称、单价到订单和明细，而不是以后 join 实时表？

**参考回答：**

“订单属于业务快照。下单时 orders 复制地址、电话、收货人，detail 从购物车复制商品名称、图片、规格、单价和数量。以后员工改地址、管理员改商品名或价格，历史申领单仍能解释当时申请了什么、送往哪里、按什么金额扣预算。实时 join 适合当前目录，不适合历史单据。”

源码状态：✅ 当前项目已实现。

## Q72：订单号如何生成？Redis INCR 有什么优点和故障边界？

**参考回答：**

“下单以 `order:number:yyyyMMdd` 做 Redis INCR，首个序号设置 2 天 TTL，订单号形如 `POyyyyMMdd-000001`。INCR 原子，单 Redis 节点并发下不会重复；数据库还有 `orders.number` 唯一索引作为最终兜底。边界是 Redis 当天数据丢失/重启可能从 1 再来，DB 唯一索引会让 insert 失败，而当前没有捕获冲突后重新取号重试；严格方案可用数据库号段或重试机制。”

源码状态：⚠️ 原子递增与唯一索引已实现；故障重试未实现。

## Q73：采购开关为什么放 Redis？它有什么默认行为和风险？

**参考回答：**

“管理员把 `shop:status` 写 Redis，submitOrder 读到 0 就拒绝；它是低频配置、读路径轻量，适合 Redis。当前 key 没有 TTL，Redis 清库或宕机重启后读到 null，代码只在值为 0 时关闭，等价于默认允许提交；这可能不符合企业控制预期。稳妥做法是持久化到 DB 并缓存，缓存未命中回源，且明确默认策略。”

源码状态：⚠️ 当前实现存在默认放行边界；💡 DB 持久化未实现。

## Q74：部门新增为什么既先查 code 又依赖唯一索引？并发时会怎样？

**参考回答：**

“Service 先按 code 查询是为了给用户友好报错，但两个并发请求都可能查不到，不能作为最终保证；department 表的 `uk_department_code` 才是并发下唯一性约束。撞到唯一索引后 GlobalExceptionHandler 捕获 SQLIntegrityConstraintViolationException 并返回重复提示。更稳健的实现会不依赖字符串拆数据库异常消息，转为领域异常或统一错误码。”

源码状态：✅ 应用预查 + DB 唯一索引存在；⚠️ 异常文本解析脆弱。

## Q75：删除部门或分类为什么先查引用？还会有并发问题吗？

**参考回答：**

“部门删除前 count employee，分类删除前 count goods 和 combo，避免逻辑上留下员工或物资挂到不存在的基础数据。它们是应用层引用完整性检查，但在查和删之间并发新增关联记录仍可能穿透；迁移脚本没有建立外键证据。生产可用外键 RESTRICT，或在事务和合适锁范围内处理，并统一改为软删除。”

源码状态：⚠️ 当前有应用层保护；💡 外键/软删除未确认或未实现。

## Q76：组合申领包为什么使用 `ResultMap`？它是否避免了所有 N+1？

**参考回答：**

“ComboMapper 的 `getByIdWithItems` 用 setmeal 左连接 setmeal_dish，ResultMap 的 collection 将多行合成为一个 ComboVO 和多个 ComboItem，所以单个组合包详情不需要逐项查关联，避免这个场景的 N+1。但组合包列表缓存的是 Combo 基本信息，`/user/combo/goods/{id}` 仍单独查询商品项；不能泛化地说项目所有组合包查询都没有 N+1。”

源码状态：✅ 当前项目已实现。

## Q77：Goods 停售为什么会连带停用组合包？有哪些一致性缺口？

**参考回答：**

“GoodsService 在停售商品时，从 combo_dish 查关联 comboId，再循环把组合包状态更新为停用，防止一个包里包含不可申领商品仍可上架。该操作在 `@Transactional` 中，所以 MySQL 更新一起回滚。但缓存清理在 Controller 里且只删 goods 前缀，没清 combo 缓存；此外重新启用商品不会自动恢复组合包，这是偏保守的业务语义，当前需要管理员手动启用并校验包内商品。”

源码状态：⚠️ DB 联动已实现，缓存失效不完整。

## Q78：DTO 到 Entity 的 `BeanUtils.copyProperties` 有什么优点和风险？

**参考回答：**

“它减少同名字段逐个赋值，例如 OrdersSubmitDTO 到 Orders、GoodsDTO 到 Goods。风险是字段新增后可能被无意复制，写接口若 DTO 含敏感字段可能造成 mass assignment；类型不匹配或漏掉字段也不显眼。项目目前关键服务仍会显式覆盖 amount、status、userId、requesterDept 等服务端字段。更严格时可手工映射或 MapStruct，并让写 DTO 只暴露允许字段。”

源码状态：✅ 当前项目已使用；💡 MapStruct/更细 DTO 未实现。

## Q79：当前接口参数校验做得怎样？为什么 `@Valid` 很重要？

**参考回答：**

“源码没有发现 Controller 的 `@Valid/@Validated` 或 DTO 的 `@NotNull/@NotBlank`。例如提交 DTO 的 addressBookId 可以为 null，上传文件也没有空、大小、MIME 校验；异常可能变成 NPE 或数据库错误。Bean Validation 能在 Controller 边界把错误转成明确 400，再由 Advice 统一响应，但它不替代 Service 内的归属、状态、库存等业务校验。”

源码状态：⚠️ 当前项目未实现 Bean Validation。

## Q80：文件上传接口有哪些安全点？

**参考回答：**

“管理端上传使用 UUID 生成 OSS objectName，避免原文件名冲突，且有 ADMIN 注解。当前直接取原文件名后缀、读全部字节上传，没有检查空文件、大小、内容类型、魔数或允许扩展名；恶意文件可能占资源或被当作不安全内容分发。应限制 Content-Type/扩展名/大小，用流式上传，配置 OSS 私有读或安全下载策略。”

源码状态：⚠️ UUID 与权限已实现；文件安全校验未实现。

## Q81：为什么要同时关注 HTTP status 和项目的 `Result.code`？

**参考回答：**

“`Result` 用 code=1/0 表示业务成功失败，便于前端统一解析；认证失败拦截器直接返回 HTTP 401。两层语义不冲突：HTTP 描述协议状态，业务 code 描述领域结果。当前 Advice 对 BaseException 仍默认 HTTP 200 + Result.error，这在前端能用，但监控、网关和调用方不容易区分 4xx/5xx；生产可规范 400、403、409、500 的 HTTP 状态和稳定错误码。”

源码状态：⚠️ 当前协议语义不完整。

## Q82：日志为什么也算安全问题？项目中要避免记录什么？

**参考回答：**

“日志会被长期保存和多人访问。当前管理端登录直接打印 EmployeeLoginDTO，拦截器打印原始 JWT；如果 DTO 的 toString 含密码，或 token 落日志，泄漏风险很高。应该只记录 requestId、用户 id、接口、脱敏用户名和错误类型，密码/token/身份证/手机号都脱敏或不记；日志还要避免在异常里拼接原始客户端输入。”

源码状态：⚠️ 当前存在敏感日志风险。

## Q83：为什么 `@Transactional` 不能保证“所有下单副作用都原子”？

**参考回答：**

“它只协调当前 MySQL 数据源。下单前的 Redis SET NX 已写入，订单号 Redis INCR 也已经递增；即使 MySQL 回滚，这两个 Redis 副作用不会回滚。当前用 5 秒 TTL 让防重 key 自然恢复，订单号允许跳号；如果还要发消息、调用支付或 OSS，就要用 outbox、可靠消息或补偿，而不是误以为一个注解解决分布式事务。”

源码状态：✅ MySQL 原子性已实现；⚠️ 跨资源非原子是既有边界。

## Q84：预算修改会不会产生新问题？

**参考回答：**

“Budget update 允许动态改 totalAmount/status，但没有校验新总额不能小于已用额，也没有审计流水。若管理员把 total 调低到小于 used，之后所有扣减都会失败，列表会出现负的剩余额；是否允许要先定义业务规则。建议校验 `totalAmount >= usedAmount`，记录调整人、原因和前后金额，并对修改操作做权限与审计。”

源码状态：⚠️ 当前缺少额度下调校验和预算流水。

## Q85：订单详情和列表的查询有何性能差异？

**参考回答：**

“单笔 details 查 orders 再查该 order_detail，属于固定两次查询。员工历史订单分页和管理端 conditionSearch 都会遍历订单逐单查 detail 或拼 orderGoods，页面有 N 个订单时又是 1+N；前文主要讲了 goods-spec N+1，这里订单列表也有同类问题。可批量按 order_id IN 查询 detail，再按 orderId 分组组装。”

源码状态：⚠️ 当前订单分页存在 N+1 风险；💡 批量明细查询未实现。

## Q86：Nginx 在项目里做了什么？真实配置是否已经负载均衡？

**参考回答：**

“Nginx 为管理端 8082、员工端 8083 提供静态 SPA 和 `/api/` 反向代理，都转发到同一个 Spring Boot 8084；它设置了 Host、X-Real-IP、X-Forwarded-For。配置有 upstream `backend_server`，但里面只有一个 127.0.0.1:8084，所以这是单后端反代，不是实际多实例负载均衡。未来多个实例才会配置多个 upstream server、健康检查和会话/Redis策略。”

源码状态：✅ 当前项目已实现单实例反代；💡 多实例负载均衡未实现。

## Q87：为什么说数据库唯一索引比 Service 查询更可靠？

**参考回答：**

“任何应用层‘先查不存在再插入’都会有并发窗口；不同 JVM、不同事务都可能同时通过查询。唯一索引由数据库在写入点统一裁决，例如 department code、budget 部门周期、orders number。Service 预查可以改善提示，索引才是最终正确性边界；捕获冲突后再转业务错误。”

源码状态：✅ 该原则有多个当前索引例子。

## Q88：如果面试官问“你会给这个项目补哪些测试”，怎么答？

**参考回答：**

“先补核心回归：预算余额 100 并发两笔 80 只允许一笔；订单插明细失败时预算与主单回滚；logout 后 token 401；禁用账号后旧 token 401；EMPLOYEE 访问管理写接口被拒；缓存 miss/hit/失效；状态条件更新竞争。再补边界：地址归属、重复返还、购物车并发和 Redis 故障。当前 POM 有 spring-boot-starter-test，但我没有把这些自动化测试说成已实现。”

源码状态：💡 建议测试集，当前未见相应测试源码。

# 23. TOP 30 高频题

> 以下答案用于最后一天背诵，完整追问见前文。

## Q38 ★★★★★ 项目介绍？
“企业内部物资申领平台，员工提交后部门预算预扣，管理端审批采购配送核销。我重点做 JWT+Redis 双端认证、MySQL 条件 UPDATE 防预算超扣、事务化下单链路和目录 Cache-Aside。”

## Q39 ★★★★★ JWT 为什么配 Redis？
“JWT 能验签但难主动失效；我用 `login:token:{token}` 作为 Redis 登录态，TTL 同 2 小时 JWT，logout DEL key，拦截器两者都通过才放行。”

## Q40 ★★★★★ ThreadLocal 为什么 clear？
“拦截器写当前 empId/role，线程池复用，结束不 remove 可能串身份和滞留 value；两个拦截器 afterCompletion 都调用 clear。”

## Q41 ★★★★★ 条件 UPDATE 怎么防超扣？
“余额判断写 WHERE，`used_amount=used_amount+? AND total-used>=?`；InnoDB 锁行后再判断，affected rows=1 才成功，避免先查再改竞态。”

## Q42 ★★★★★ 两个 80 抢余额 100？
“T1 锁行更新到已用 80；T2 等锁，随后余额只剩 20，WHERE 不成立、更新 0 行，所以不超扣。”

## Q43 ★★★★★ 下单事务覆盖哪些？
“预算预扣、orders 主单、order_detail 批量明细、删购物车；其中失败 RuntimeException，MySQL 一起回滚。”

## Q44 ★★★★★ Redis SET NX 是幂等吗？
“不是。当前 `order:submit:{empId}` 只限制 5 秒，防双击；严格幂等需 requestId 持久化和唯一索引。”

## Q45 ★★★★★ Cache-Aside 流程？
“先 Redis，miss 查 DB 回填；管理端写 DB 成功后删目录缓存。当前是最终一致，删失败没有补偿。”

## Q46 ★★★★★ 缓存三大问题？
“空 List 60 秒防穿透；30 分钟加随机秒防雪崩；当前没有锁/逻辑过期，击穿未真正解决。”

## Q47 ★★★★★ 当前项目最大缺陷？
“状态先查后改、预算返还非订单级幂等、默认放行权限、KEYS 清缓存、N+1、购物车先查再改。我会说明具体风险和条件 UPDATE/唯一索引/SCAN 等改法。”

## Q48 ★★★★ 认证和授权？
“Interceptor 认证并写上下文；AOP 读取 `@RequireRole` 做授权。角色是 EMPLOYEE/PURCHASER/ADMIN。”

## Q49 ★★★★ JWT 是加密吗？
“不是；当前 HS256 是签名，payload 可被解码，只放 empId，不放密码。”

## Q50 ★★★★ 为什么查 employee 而非只信 JWT？
“实时看账号是否存在、禁用，且从 DB 取当前 role，不让旧 token 长时间带旧权限。”

## Q51 ★★★★ 为什么用 BigDecimal / DECIMAL？
“金额不能用二进制浮点，避免 0.1 类精度误差；项目 budget 是 DECIMAL(12,2)、Java 是 BigDecimal。”

## Q52 ★★★★ 为什么预算不放 Redis？
“预算是持久化强一致事实，MySQL 条件更新已满足原子性，Redis 做缓存/锁反而引入双写和恢复问题。”

## Q53 ★★★★ 状态机怎么改造？
“用 `UPDATE orders SET status=? WHERE id=? AND status=?`，affected rows 0 表示状态已变化，是 CAS 风格乐观控制。”

## Q54 ★★★★ Redis 与 MySQL 事务？
“`@Transactional` 只管同数据源 MySQL；SET NX、INCR、缓存不会随 DB rollback，所以要单独设计补偿/幂等。”

## Q55 ★★★★ KEYS 与 SCAN？
“KEYS 全量遍历会阻塞 Redis；当前小量可用但上线改 SCAN 分批，或维护精确 key。”

## Q56 ★★★★ N+1 在哪里？
“物资列表先查 goods，再逐项查 dish_flavor，1+N；缓存冷启动仍有。用 IN 查询加 groupingBy 改两条。”

## Q57 ★★★★ 申领车并发？
“当前先查 number 再覆盖写，会丢失更新；应 number=number+1 或唯一索引 + upsert。”

## Q58 ★★★★ 为什么 orders/detail 分表？
“订单公共字段与 N 条物资明细一对多，减少冗余并保留提交时快照。”

## Q59 ★★★★ requester_dept 为什么冗余？
“保存申请当时部门，统计与返还不受员工后续转部门影响。”

## Q60 ★★★★ MyBatis `#{}` 与 `${}`？
“前者预编译绑定防注入，后者文本拼接，需要白名单。”

## Q61 ★★★★ PageHelper 原理？
“MyBatis 插件拦截紧随 startPage 的查询，追加 limit/count，返回 Page total/result。”

## Q62 ★★★★ AOP 自动填充如何做？
“@AutoFill Mapper 方法触发 Before 切面，反射调用 setter 填审计字段。”

## Q63 ★★★★ 为什么不用 Spring Security？
“固定三角色、小项目用 Interceptor+AOP 更直观；复杂授权、多认证时迁移 Security。”

## Q64 ★★★ 为什么不用分布式锁？
“一行条件 UPDATE 已原子且事实在 MySQL；锁会增加失效续租复杂度。”

## Q65 ★★★ 地址有什么安全问题？
“submit 按 id 查地址但不验 user_id，应改 `id + user_id` 查询。”

## Q66 ★★★ 管理端权限有什么问题？
“未标注默认放行，部分读接口采购员可读；管理员订单详情还误复用 owner 校验。”

## Q67 ★★★ 数据库索引最重要的？
“budget `(dept_id,period)` 唯一既保证一月一预算又支持定位；orders number 有唯一索引。组合分页索引需 EXPLAIN 后补。”

---

# 24. 面试前 30 分钟速记

## 项目

企业物资申领：员工申领 → **预算预扣** → 审批 → 采购中 → 配送 → 完成。  
重点：**JWT+Redis / ThreadLocal / AOP / 条件 UPDATE / Transactional / Cache-Aside**。

## JWT + Redis

JWT：`Header.Payload.Signature`；HS256 **签名非加密**；claims 只 `empId`。  
双端：admin `token` + admin secret；user `authentication` + user secret；TTL **2h**。  
Redis：`login:token:{token}` → employeeId；TTL=JWT；logout DEL；补 JWT 无法主动撤销。  
Interceptor：JWT → Redis → employee 状态/role → BaseContext；失败 **401**。  
ThreadLocal：请求末尾 `afterCompletion clear/remove`，防线程复用串号。

## 权限

EMPLOYEE：员工端申领。  
PURCHASER：审批/配送/核销。  
ADMIN：基础数据、预算、员工管理。  
认证 Interceptor；授权 `@RequireRole + RoleAspect`。  
缺陷：**未标注即放行**；管理端部分读接口漏标。

## 预算并发

不要：`SELECT 余额 → Java 判断 → UPDATE`。  
要：

```sql
UPDATE budget SET used_amount = used_amount + ?
WHERE dept_id=? AND period=? AND status=1
  AND total_amount - used_amount >= ?;
```

InnoDB 行锁；判断+修改原子；**affected rows=1 成功，0 不足**。  
金额：MySQL `DECIMAL(12,2)` + Java `BigDecimal`。  
事实来源：**MySQL，不是 Redis**。  
返还当前有条件 SQL，但订单级重复返还仍有并发窗口。

## 下单 + 事务

Nginx → Interceptor → Controller SET NX 5s → Service。  
查地址 / 查购物车 / 后端按购物车算额 / 查部门 / 扣预算 / 插 orders / 批插 detail / 清车。  
`@Transactional`：预算、主单、明细、清车一起回滚。  
**Redis 不参与 MySQL 事务**。  
金额未信任前端；但当前购物车价格不是提交时重新查商品价。  
地址当前未校验归属。

## SET NX 与幂等

`order:submit:{empId}`，NX + TTL 5s：防双击。  
不是严格幂等：无 requestId，TTL 后仍能新建。  
严格：requestId + DB 唯一索引（**未实现**）。

## 状态机

2 待审批 → 3 采购中 → 4 配送中 → 5 完成。  
驳回 / 撤销 / 取消 / 退换 → 6；退换 `is_returned=1`，不立即返还。  
缺陷：先查状态再普通 UPDATE。  
改：`WHERE id=? AND status=?` + affected rows。

## 缓存

手写 Cache-Aside，**不是 Spring Cache**。  
goods/combo：hit 返回；miss 查 DB 回填。  
空列表 **60s** 防穿透；正常 **30min + 0~299s** 防雪崩。  
写：DB 成功后删缓存，最终一致。  
缺陷：KEYS、无删失败补偿、无击穿锁、商品停售未清 combo 缓存。

## 性能与缺陷

N+1：1 次 goods + N 次 spec；优化 IN + groupingBy（未实现）。  
购物车：先查再改会丢更新；优化 `number=number+1` / upsert（未实现）。  
安全：硬编码 JWT 密钥、无盐 MD5、日志可能打印 token/密码。  
回答缺陷四步：**承认 → 当前取舍 → 风险 → 改法**。
