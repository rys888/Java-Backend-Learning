# 自定义 RedisTemplate 配置类

**自定义 RedisTemplate 配置类**，解决 Spring 默认 RedisTemplate 的序列化坑。

> 默认的 RedisTemplate，key 和 value 用 JDK 序列化，存到 Redis 里会出现一堆 `\xac\xed` 这种乱码，而且对象存进去很难看懂。所以我们重写配置，改成 **String 序列化 key，JSON 序列化 value**。

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory){
        // 1. 创建RedisTemplate对象
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        // 2. 设置连接工厂（负责底层和Redis建立连接，底层是Lettuce/Jedis）
        template.setConnectionFactory(connectionFactory);

        // 3. 创建JSON序列化器：把Java对象转成JSON字符串存入Redis；读取时把JSON转回Java对象
        GenericJackson2JsonRedisSerializer jsonRedisSerializer = new GenericJackson2JsonRedisSerializer();

        // ========== 设置key序列化器 ==========
        // 普通String类型key，使用字符串序列化
        template.setKeySerializer(RedisSerializer.string());
        // Hash结构的field（hashKey）也用字符串序列化
        template.setHashKeySerializer(RedisSerializer.string());

        // ========== 设置value序列化器 ==========
        // 普通value用JSON序列化：比如存Dish对象，自动转JSON
        template.setValueSerializer(jsonRedisSerializer);
        // Hash结构的value也用JSON序列化
        template.setHashValueSerializer(jsonRedisSerializer);

        return template;
    }
}
```

## 核心概念拆解

1. **@Configuration**：标记这是配置类，项目启动时会加载
2. **@Bean**：把这个方法返回的 `RedisTemplate` 交给 Spring 容器管理，之后 `@Autowired` 直接注入使用
3. **RedisConnectionFactory**：连接工厂，底层封装 Redis 客户端（Lettuce 默认），自动读取 yml 里面 redis 地址、端口密码
4. **序列化器作用**
    - `RedisSerializer.string()`：key 存普通字符串，Redis 客户端查看不会乱码
    - `GenericJackson2JsonRedisSerializer`：Java 对象 ↔ JSON。存 Dish、Setmeal 实体类时，自动序列化为 JSON 字符串；读取时自动反序列成 Java 对象。


## 代码解析与示例

```java
GenericJackson2JsonRedisSerializer jsonRedisSerializer = new GenericJackson2JsonRedisSerializer();
```

创建一个 **JSON 序列化工具**：
- 写：Java 对象 → JSON 字符串（存入 Redis）
- 读：Redis 里的 JSON 字符串 → 自动转回 Java 对象

```java
template.setKeySerializer(RedisSerializer.string());
template.setHashKeySerializer(RedisSerializer.string());
```

- `setKeySerializer`：普通 `key`（比如 `dish_1`），用**字符串序列化**
  比如你代码写 key="dish_1"，存入 Redis 的 key 就是原样字符串 `dish_1`，不会出现乱码。
- `setHashKeySerializer`：针对 Redis Hash 结构，`hash的field`（Hash 里面的小 key）也用字符串。
> 例：`hset user name "张三"`，`user` 是大 key，`name` 就是 hashKey。

```java
template.setValueSerializer(jsonRedisSerializer);
template.setHashValueSerializer(jsonRedisSerializer);
```

- `setValueSerializer`：普通 key 对应的 value，用 JSON 序列化。
  存入 `Dish对象`，自动转成一段 JSON 放到 Redis；读取时自动把 JSON 转回 Dish 对象。
- `setHashValueSerializer`：Hash 结构里面 field 对应的 value，同样用 JSON 序列化。

那么不配置这 4 行，会发生什么？
Spring 默认 RedisTemplate 使用 **JDK 序列化**：
- 存 key：`dish_1`，Redis 里看到的是一堆二进制乱码 `\xac\xed\x00\x05t\x00\x06dish_1`
- 存 Dish 对象，Redis 里全是不可读的二进制。
- 只能 Java 程序读取，别的客户端（Redis 可视化工具、小程序）看不懂。

配置完之后：
- Redis 里的 key：`dish_1`（干净字符串）
- Redis 里的 value：`{"id":1,"name":"鱼香肉丝","categoryId":10}`（标准 JSON，肉眼可读）

## 4 个序列化器对应 Redis 两种数据类型

**普通 String 类型** `redisTemplate.opsForValue().set("dish_1", dishObj)`
   - `setKeySerializer`：控制 key
   - `setValueSerializer`：控制 value

**Hash 类型** `redisTemplate.opsForHash().put("hashKey","field",obj)`
   - `setHashKeySerializer`：控制 hash 里面的 field（小 key）
   - `setHashValueSerializer`：控制 hash 里面 field 对应的 value


## 为什么要写这个配置？

SpringBoot 原生自动装配的 `RedisTemplate` 默认：
- `RedisTemplate<Object,Object>`
- 默认序列化：**JDK 序列化**
- 缺点：
  1. Redis 客户端看 key/value 是二进制乱码，可读性极差
  2. JDK 序列化只能 Java 语言读取，跨语言不友好
  3. 序列化后的字节体积大，占用 Redis 内存

我们自定义之后：
- Key 统一字符串，干净清晰（比如 `dish_1`）
- Value 自动 JSON，可视化，适合存菜品、套餐缓存。

## 四个序列化器简单区分
|方法|作用|
| ---- | ---- |
|setKeySerializer|普通 key（String 类型 key）|
|setValueSerializer|普通 key 对应的 value（可以是对象）|
|setHashKeySerializer|Hash 类型的 field 字段|
|setHashValueSerializer|Hash 类型 field 对应的 value|

⚠️：GenericJackson 2 JsonRedisSerializer 会在 JSON 里额外保存 `@class` 字段，用来识别要反序列化成哪个 Java 类
比如：
{
	"@class":"com.heima.redis.pojo.User",
	"name":"虎哥",
	"age":23
}
@class.....占用内存空间 ➡️
所以一般不使用 JSON 序列化器来处理 value，而是统一使用 String 序列化器，要求只能
存储 String 类型的 key 和 value，手动完成对象序列化和反序列化（因为没有@class.....)

![截屏2026-09-22 21.54.29](../%E9%99%84%E4%BB%B6/%E6%95%B0%E6%8D%AE%E5%BA%93%E4%B8%8E%E7%BC%93%E5%AD%98/%E6%88%AA%E5%B1%8F2026-09-22%2021.54.29.png)

实际上这个过程中，Spring 已经给我们提供了一个叫 StringRedisTemplate 的类，它的 key 和 value 的序列化方式已经默认是 String 方式，省去了我们自定义 RedisTemplate 的过程（白雪！）。

如果是传入的字符串类型，就很方便了
如果是传入的对象类型的数据，就需要我们手动完成序列化和反序列化
示例：

```
private static final ObjectMapper mapper=new ObjectMapper();

@Test
void testSaveUser() throws JsonProcessingException{
	User user=new user("虎哥",21);
	String json=mapper.writeValueAsString(user);//序列化(java➡️json)
	stringRedisTemplate.opsForValue().set("user.200",json);
	.....
	User user1=mapper.readValue(jsonUser,User.class);//反序列化（json➡️java）
}
```

补充：`ObjectMapper` 是 Jackson 包里面的核心类，作用：**Java 对象 ↔ JSON 字符串互相转换**
