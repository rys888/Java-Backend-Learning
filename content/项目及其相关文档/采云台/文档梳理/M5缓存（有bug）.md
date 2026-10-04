Redis 配置与序列化

```
@Configuration
public class RedisConfiguration {
    @Bean
    public RedisTemplate redisTemplate(RedisConnectionFactory redisConnectionFactory){
        RedisTemplate redisTemplate = new RedisTemplate();
        redisTemplate.setConnectionFactory(redisConnectionFactory);
        redisTemplate.setKeySerializer(new StringRedisSerializer());   // ★ 只设了 Key
        return redisTemplate;                                          //   Value 用默认
    }
}
```


## 链路 1：用户端物资列表

认证到时候在说

![[截屏2026-10-01 11.17.19.png|499]]

物资在缓存➡️直接拿
物资不在缓存➡️数据库查询➡️放入缓存（如果数据库为空设置 TTL 为 60 s，否则 30-35 分钟）
TTL 随机都懂防止缓存雪崩，这个点设计的很好


## 链路 2：用户端组合申领包列表

同理

![[截屏2026-10-01 11.21.35.png]]



## 链路 3：管理员写操作--清缓存（物资）

```
【入口 1】POST /admin/goods（新增）
   ↓ @RequireRole(ADMIN) → RoleAspect 校验
   ↓ goodsService.saveWithSpecs(dto)   @Transactional
   ↓ cleanCache(RedisKeyConstant.GOODS_LIST_PREFIX + "*")
        → redisTemplate.keys("goods:list:*")  【KEYS 命令，O(N) 阻塞】
        → redisTemplate.delete(keys)

【入口 2】DELETE /admin/goods?ids=（批量删除）
   ↓ goodsService.deleteBatch(ids)  @Transactional（含"在售不可删""被组合包引用不可删"校验）
   ↓ cleanCache("goods:list:*")
【入口 3】PUT /admin/goods（修改）
   ↓ goodsService.updateWithSpecs(dto)  @Transactional（删旧规格 + 插新规格）
   ↓ cleanCache("goods:list:*")
【入口 4】POST /admin/goods/status/{status}（启停）
   ↓ goodsService.startOrStop(status, id)  @Transactional
   │     ★ 如果 status == DISABLE(0)：
   │        comboDishMapper.getComboIdsByGoodsIds([id])   ← 查出包含该物资的组合包
   │        for (comboId : comboIds)
   │            comboMapper.update(Combo{id, status=DISABLE})   ← ★★ 级联停用组合包！
   ↓ cleanCache("goods:list:*")
   │     ⚠️⚠️⚠️ 只清了物资缓存，【没有清 combo:list:*】
   │        而这一步刚刚修改了 setmeal.status
   ↓ Result.success()

cleanCache 实现（第 157-160 行）：
   private void cleanCache(String pattern){
       Set keys = redisTemplate.keys(pattern);      ← Redis KEYS 命令
       redisTemplate.delete(keys);
   }

```

这里的问题应该是不应该级联不应该停用组合包，只针对物资；关于物资包的业务在 Combo 有关的 service 等中完成



## 链路 4：管理员写操作——清缓存（组合包）

```
【入口 1】POST /admin/combo（新增）        → comboService.saveWithItems(dto)  @Transactional
【入口 2】DELETE /admin/combo?ids=          → comboService.deleteBatch(ids)   @Transactional
【入口 3】PUT /admin/combo（修改）          → comboService.update(dto)         @Transactional
【入口 4】POST /admin/combo/status/{status} → comboService.startOrStop(status, id)
        ★ 启用时先校验包内物资是否都启用（ComboServiceImpl:151）
          有停用物资 → 抛 ComboEnableFailedException
   ↓ 四个入口都调：
   cleanComboCache()
       Set keys = redisTemplate.keys(RedisKeyConstant.COMBO_LIST_PREFIX + "*");  ← KEYS
       redisTemplate.delete(keys);
```



## 链路 5：采购开关

```
写：PUT /admin/shop/{status}  @RequireRole(ADMIN)
      → redisTemplate.opsForValue().set(RedisKeyConstant.SHOP_STATUS, status)
      ★ 泛型 RedisTemplate，Value 走 JDK 序列化存 Integer
      ★ 【无 TTL】

读：GET /admin/shop/status
    GET /user/shop/status（无拦截器，属于白名单路径）
      → Integer status = (Integer) redisTemplate.opsForValue().get(SHOP_STATUS);
      → log.info(...status != null && status == 1 ? "营业中" : "打烊中")   ← 已做 null 安全

消费：OrderServiceImpl.submitOrder:68
      Integer shopStatus = (Integer) redisTemplate.opsForValue().get(SHOP_STATUS);
      if (shopStatus != null && shopStatus == 0) throw ...(SHOP_CLOSED);
```

将采购状态写入缓存，以后每次提交申领都需要先获取 redis 里面的采购状态

![[截屏2026-10-01 12.06.14.png]]



## 链路 6：缓存与事物的关系（**所有写路径都"先事务、后清缓存"**）

```
PUT /admin/goods
   ├─ goodsService.updateWithSpecs(dto)   ← @Transactional 在这里【开始】
   │     goodsMapper.update(...)
   │     goodsFlavorMapper.deleteByGoodsId(...)
   │     goodsFlavorMapper.insertBatch(...)
   │  ← @Transactional 在这里【提交】
   └─ cleanCache("goods:list:*")          ← 在事务【之外】、提交【之后】

★ 这个顺序是【正确的】，见第四部分 4.1 的论证
```

如果发过来：

时序：

1. 线程 A：先删除 Redis 缓存（缓存变空），**然后开始执行数据库事务，还没提交！**
2. 同时线程 B 来查询数据：Redis 缓存是空 → 查询 MySQL，读到**旧数据**
3. 线程 B 把读到的旧数据，写入 Redis 缓存
4. 线程 A 才提交事务，数据库变成新数据

👉 结果：**数据库是新数据，Redis 缓存是旧数据，永久不一致！**
只要出现上面这个并发，缓存脏数据就一直存在，除非过期。
那为什么【先写数据库，事务提交成功后，再删除缓存】就安全？

时序：

1. 线程 A：开启事务，更新 MySQL，**事务还没提交**
2. 线程 B 查询：读到旧缓存，直接返回（没问题）
3. 线程 A：**事务提交成功**
4. 线程 A：删除 Redis 缓存

之后再来查询，缓存为空，去 DB 读最新数据写入缓存。
> 极端情况：事务刚提交，删缓存操作失败。
> 这时 DB 新、缓存旧，依然不一致。
> 解决方案：**缓存加过期时间兜底**（项目中 30 分钟）

## 对比两种策略
**先删缓存，再更新 DB**
并发读很容易直接造出脏缓存，**发生概率高**，基本不推荐。
**先更新 DB（事务提交），再删缓存（Cache Aside）**
只有【DB 提交成功，但是删缓存失败】才会不一致，**概率很低**，可以用过期时间兜底。


## 链路 7：缓存与 N+1 的关系（`listWithSpecs` 为什么没被感知为性能问题）

```
冷启动 / 缓存被清后第一次请求：
   GET /user/goods/list?categoryId=23
   → 未命中 → listWithSpecs → 1 + N 次 SQL（N = 该分类下物资数）
   → 写入缓存（TTL 30~35 分钟）
   
之后 30~35 分钟内的所有请求：
   → 命中 → 0 次 SQL

结论：N+1 只在"缓存重建"时发生。
     · 正常情况下每 30 分钟发生一次，压力可忽略；
     · 但如果管理员频繁改物资（每次写都清缓存），
       或者 Redis 被清空、缓存大面积过期，
       N+1 就会在短时间内被反复触发。
```