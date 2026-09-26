# 从最初的 Controller 看懂 MyBatis-Plus

这篇只顺着 `hm-dianping` 刚开始实现的 `UserController`、`ShopController`、`BlogController` 来开展。看完你会知道：MP 是什么、你代码里哪些方法其实是它给的、它背后发了什么 SQL、以及什么时候必须自己写 SQL。

## 一、一些规则

MyBatis-Plus 是 MyBatis 的增强工具，不是替代品。它需要：
- Mapper 继承 BaseMapper ➡️ 可以使用 MP 提供的 `selectById`、`selectList`、`insert`、`updateById` 单表方法（第一套规则）
- 如果 Service 按照下面代码实现了（黑马点评就是选择这套） ➡️ 就可以对 BaseMapper 再封装一层，直接在 Service 层快捷调用 `getById`、`list`、`save`、`updateById`、`query()` 链式构造器（第二套规则）
- 如果 Service 不继承 IService、ServiceImpl ➡️ 走第一套规则：Service 注入 Mapper，手动调用 shopMapper.selectById()
- 两套规则方法名看起来很像，但属于两套不同 API，底层 Service 方法最终还是调用 Mapper 的方法

```java
// 1. Mapper 接口继承 BaseMapper，就自带单表增删改查
public interface ShopMapper extends BaseMapper<Shop> {
}

// 2. Service 接口继承 IService，实现类继承 ServiceImpl，这些方法就能在 Controller 里直接用
public interface IShopService extends IService<Shop> {
}
public class ShopServiceImpl extends ServiceImpl<ShopMapper, Shop> implements IShopService {
}
```

- 实体类注解`@TableName`、`@TableId`
 
```
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
@TableName("tb_shop")
public class Shop implements Serializable {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    // ...其他普通字段

    @TableField(exist = false)
    private Double distance;
}
```

@TableName("tb_name") 含义是：声明当前实体类对应的数据库表是 tb_shop
@TableId(value = "id", type = IdType.AUTO) 
- `value="id"`：主键字段数据库叫 id，实体属性也叫 id，value="id" 在这里其实可以省略。
- `type = IdType.AUTO`：数据库自增主键（重点！这个不能省）
@TableField(exist=false) 含义是：这个字段在数据库 tb_shop 表里面不存在！只是前端需要返回的临时字段（距离）

## 二、UserController：最简单的用法

```java
@GetMapping("/info/{id}")
public Result info(@PathVariable("id") Long userId){
    UserInfo info = userInfoService.getById(userId);   // ← 这一行是 MP 给的
    if (info == null) {
        return Result.ok();
    }
    ...
}
```

这里我开始很疑惑，怎么 Controller 层也能调用 getById()方法了，这个方法不是第二套规则范围里面的吗，啥情况?？

其实仍然是 Service 层在调用，写在 Controller 层，不代表是 Controller 自己的方法

```
@Resource  
private IUserInfoService userInfoService;
```

之前已经注入了 userInfoService （继承 IService），`getById()` 是 **MyBatis‑Plus IService 接口自带方法**

这样解释就合理了

`getById` 不是 `IUserInfoService` 里定义的，也不是 `UserInfoServiceImpl` 写的，它来自 `IService`。方法名和参数你都看得见，实际执行的 SQL 是：

```sql
SELECT user_id, ... FROM tb_user_info WHERE user_id = ?
```

表名 `tb_user_info` 来自实体上（User_info）的 `@TableName("tb_user_info")`，列名 `user_id` 来自 `@TableId(value = "user_id", ...)`。MP 在启动时读这些注解，把 `getById` 翻译成上面那条 SQL，再交给 MyBatis 执行。

这里有个容易忽略的点：**单表按主键查，查不到返回 `null`，不抛异常**，所以你能安心写 `if (info == null)`。

## 三、UserServiceImpl：按条件查和保存

```java
// 根据手机号查询用户
User user = query().eq("phone", phone).one();
```

`query()` 是 `ServiceImpl` 提供的方法，返回一个条件构造器，`eq` 继续往上加条件，最后的 `.one()` 才真正发 SQL：

```sql
SELECT id, phone, password, nick_name, icon, ... FROM tb_user WHERE phone = ? LIMIT 1
```

链式写法有个特点：不调 `.one()`、`.list()`、`.page()`、`.count()` 这些结尾方法，SQL 就不会执行。前面那一串只是在攒条件。

同一个文件里创建新用户：

```java
private User createUserWithPhone(String phone) {
    User user = new User();
    user.setPhone(phone);
    user.setNickName(SystemConstants.USER_NICK_NAME_PREFIX + RandomUtil.randomString(10));
    save(user);          // ← INSERT INTO tb_user (...) VALUES (...)
    return user;
}
```

这段代码写在 **UserServiceImpl** 里面，继承了 `ServiceImpl<UserMapper,User>`，所以直接写 `save(user)`，等价 `this.save(user)`。

这里的 `user` 是 `User` 实体类对象，MP 拿到 `User` 类，去读取这个类上面的注解 / 类名规则，找到对应的数据库表。

`save` 之后直接把 `user` 返回，调用方拿到的对象已经带上主键了。这靠的是 `User` 上的 `@TableId(value = "id", type = IdType.AUTO)`：告诉 MP 主键是数据库自增的，插入完把自增值回填到对象里。

**列名和属性名要分清。** `eq("phone", phone)` 里的 `"phone"` 是数据库列名，恰好和 Java 属性名一样，所以看不出问题。换成商铺类型就必须写列名：

```java
.eq("type_id", typeId)     // 正确：type_id 是列名
.eq("typeId", typeId)      // 错误：查不到数据，还不一定报错
```

## 四、ShopController：增删改查和分页

新增和更新各一行：

```java
shopService.save(shop);         // INSERT
return Result.ok(shop.getId()); // 主键回填

shopService.updateById(shop);   // UPDATE tb_shop SET ... WHERE id = ?
```

`updateById` 只更新对象里**非 null 的字段**。这点在更新商铺时很重要：没设值的字段不会进 `SET` 子句，也就不会被覆盖成 null。

分页是这里最值得看的一段：

```java
Page<Shop> page = shopService.query()
        .eq("type_id", typeId)
        .page(new Page<>(current, SystemConstants.DEFAULT_PAGE_SIZE));
return Result.ok(page.getRecords());
```

`Page` 来自 `com.baomidou.mybatisplus.extension.plugins.pagination.Page`，两个参数是页码和每页条数。它实际会发两条 SQL：

```sql
SELECT COUNT(*) FROM tb_shop WHERE (type_id = ?)
SELECT id, name, type_id, ... FROM tb_shop WHERE (type_id = ?) LIMIT ?
```

第一条 count 不是你写的，是分页插件自动加的。所以**分页插件必须注册**，否则 `new Page<>()` 只是个普通对象，MP 会把整张表查出来：

```java
// config/MybatisConfig.java
@Configuration
public class MybatisConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}
```

同一个 Controller 里还有个更巧的用法：

```java
Page<Shop> page = shopService.query()
        .like(StrUtil.isNotBlank(name), "name", name)
        .page(new Page<>(current, SystemConstants.MAX_PAGE_SIZE));
```

`like` 的第一个参数是个布尔开关。名字为空时这个条件整个不拼进 SQL，非空时才拼 `name LIKE '%关键字%'`。用 MyBatis 写就要在 XML 里加 `<if test="name != null and name != ''">`，MP 用一个参数替代了。

## 五、BlogController：进阶用法

```java
// 保存后立刻拿主键
blogService.save(blog);
return Result.ok(blog.getId());

// 点赞数加一
blogService.update()
        .setSql("liked = liked + 1").eq("id", id).update();
```

点赞这段值得单独说。为什么不用 `updateById`？因为那样得先把 blog 查出来、`liked + 1`、再写回去，两个人同时点赞就会互相覆盖。`setSql` 把表达式原样交给数据库，等价于：

```sql
UPDATE tb_blog SET liked = liked + 1 WHERE id = ?
```

## 六、这些方法为什么不用你写实现

把上面几段串起来，整条链路是这样的：

```
Controller 调用 shopService.page(...)
    ↓
IService 的默认实现（ServiceImpl 里已经写好）
    ↓
BaseMapper 的方法（MP 启动时按实体注解生成 SQL）
    ↓
MyBatis 执行 SQL
```

你需要提供的只有三样：

| 你写的 | 作用 |
|---|---|
| `@MapperScan("com.hmdp.mapper")`（在启动类上） | 把 Mapper 接口变成 Spring Bean |
| `@TableName` / `@TableId` / `@TableField` | 告诉 MP 类对应哪张表、哪个字段是主键 |
| `extends BaseMapper<T>` / `extends ServiceImpl<M, T>` | 继承那些现成的方法 |

另外 `type_id` 能自动映射到 `typeId`（下划线转驼峰），这是 MP 默认开着的，不用配。

## 七、什么时候必须自己写 SQL

MP 的自动化只覆盖单表。跨表联查得自己来，你项目里只有一个例子：

```java
// VoucherMapper.java
public interface VoucherMapper extends BaseMapper<Voucher> {
    List<Voucher> queryVoucherOfShop(@Param("shopId") Long shopId);
}
```

```xml
<!-- resources/mapper/VoucherMapper.xml -->
<mapper namespace="com.hmdp.mapper.VoucherMapper">
    <select id="queryVoucherOfShop" resultType="com.hmdp.entity.Voucher">
        SELECT v.`id`, v.`title`, ..., sv.`stock`, sv.begin_time, sv.end_time
        FROM tb_voucher v
        LEFT JOIN tb_seckill_voucher sv ON v.id = sv.voucher_id
        WHERE v.shop_id = #{shopId} AND v.status = 1
    </select>
</mapper>
```

这条 SQL 联查了两张表，MP 的自动 SQL 做不了。调用入口在 `VoucherServiceImpl`：

```java
List<Voucher> vouchers = getBaseMapper().queryVoucherOfShop(shopId);
```

`getBaseMapper()` 返回的就是 `VoucherMapper`。这样"MP 自动的方法"和"你手写的 SQL"能待在同一个 Mapper 里，互不影响。

## 八、和 MyBatis 的区别

| | MyBatis | MyBatis-Plus |
|---|---|---|
| 单表 CRUD | 每个方法都要写 SQL | 继承接口就有，零 SQL |
| 条件查询 | XML 里堆 `<if>` | `eq` / `like` 链式调用 |
| 分页 | 手写 `LIMIT` 或用 PageHelper | `new Page<>(current, size)` + 插件 |
| 主键回填 | 配 `useGeneratedKeys` | `@TableId(type = IdType.AUTO)` |
| 复杂 SQL | 本来就是干这个的 | 一样写 XML，不冲突 |

一句话：MyBatis 是发动机，每一步都要你决定；MP 是自动挡，单表操作替你挂挡，遇到联查这种复杂路况随时能切回手动。你项目里 `ShopServiceImpl` 是自动挡，`VoucherMapper.xml` 是手动挡，两者共存得很好。

## 九、速查表

| 你的需求 | 写法 | 等价 SQL |
|---|---|---|
| 按主键查一条 | `getById(id)` | `WHERE id = ?` |
| 按条件查一条 | `query().eq("phone", phone).one()` | `WHERE phone = ? LIMIT 1` |
| 按条件查多条 | `query().eq(...).list()` | `WHERE ...` |
| 分页 | `query().eq(...).page(new Page<>(c, s))` | `LIMIT` + `COUNT` |
| 新增 | `save(entity)` | `INSERT INTO` |
| 按主键改 | `updateById(entity)` | `UPDATE ... WHERE id = ?` |
| 字段自增 | `update().setSql("liked = liked + 1").eq("id", id).update()` | `SET liked = liked + 1` |
| 按主键删 | `removeById(id)` | `DELETE ... WHERE id = ?` |
| 联查 | 接口方法 + XML，用 `getBaseMapper()` 调 | 你说了算 |

