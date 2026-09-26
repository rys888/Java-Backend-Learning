![[Pasted image 20260919133911.png|391]]



关于苍穹外卖中JWT 令牌知识总结

### Token 和 JWT 前置知识
- Token：Token 本质就是后端发给前端的一串字符串，作为登录通行证。前端登录成功拿到它，之后每次请求接口，在请求头带上这串字符串，后端识别：你已经登录了，允许访问。
Token 有很多的实现方式，比如 SessionId，JWT 等

- JWT 是一种特定结构的 Token 字符串，三段构成：
     Header：记录加密算法，比如 HS 256
     Payload：载荷（claims），存放业务数据，比如员工 id、过期时间等
     Signature ：签名，校验 Header 和 Payload 有没有被篡改，计算公式：
     Signature = HMAC-SHA256( Header + Payload + secretKey )
  其中 secretKey 是 yml 中配置的 itcast。


### 苍穹外卖员工登录完整流程，串起 JWT

1. 员工账号密码登录，校验成功
2. 后端准备 Payload：存入 employeeId，设置过期时间
3. 后端读取 yml 的 secretKey：`itcast`
4. 根据 Header、Payload、itcast 计算签名，拼接三段 → **生成 JWT 字符串**
5. 把这个 JWT 字符串返回前端，**这个字符串，在代码里就叫 token**
6. 前端保存 token，后续访问接口，请求头带上 `token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9......`
7. 后端 JWT 拦截器：
    1. 从请求头取出 token（JWT 字符串）
    2. 拆分三段，取出 Header、Payload、Signature
    3. 用**同样的密钥 itcast**，拿 Header+Payload 重新计算一遍签名
    4. 对比新算出来的签名 和 token 自带的签名：
        - ✅ 相等：没有被篡改。再判断是否过期。解析 Payload 拿到 employeeId，存入 BaseContext，放行。
        - ❌ 不相等：Payload 被人改过，直接拦截。



### 用代码方式解释

EmployeeController

```
@PostMapping("/login")
    public Result<EmployeeLoginVO> login(@RequestBody EmployeeLoginDTO employeeLoginDTO) {
        log.info("员工登录：{}", employeeLoginDTO);

        Employee employee = employeeService.login(employeeLoginDTO);

        //登录成功后，生成jwt令牌
        Map<String, Object> claims = new HashMap<>();
        claims.put(JwtClaimsConstant.EMP_ID, employee.getId());
        String token = JwtUtil.createJWT(
                jwtProperties.getAdminSecretKey(),
                jwtProperties.getAdminTtl(),
                claims);

        EmployeeLoginVO employeeLoginVO = EmployeeLoginVO.builder()
                .id(employee.getId())
                .userName(employee.getUsername())
                .name(employee.getName())
                .token(token)
                .build();

        return Result.success(employeeLoginVO);
    }
```

- claims：是 JWT 载荷（payload），也就是存在 token 里面的数据，数据结构是 hashmap（键值对 EMP_ID--employeeId），这里存了 employee 的 id
   ⚠️claims 中的数据并不是加密所以不要放手机号等敏感信息
- createJWT：是调用 JwtUtil 工具类预制的方法来生成 token，实现代码如下：
 
```
/**
 * 生成JWT字符串
 * @param secretKey 签名密钥（yml里的 itcast）
 * @param ttlMillis 过期时长，单位毫秒（7200000 = 2小时）
 * @param claims 载荷，存放业务数据，比如员工id
 * @return JWT字符串（就是我们代码里说的token）
 */
public static String createJWT(String secretKey, long ttlMillis, Map<String, Object> claims) {
    // 指定签名的时候使用的签名算法，也就是header那部分
    SignatureAlgorithm signatureAlgorithm = SignatureAlgorithm.HS256;

    // 生成JWT的过期时间
    long expMillis = System.currentTimeMillis() + ttlMillis;
    Date exp = new Date(expMillis);

    // 设置jwt的body
    JwtBuilder builder = Jwts.builder()
            // 放入自定义载荷（业务数据，比如employeeId）
            .setClaims(claims)
            // 设置签名算法 + 密钥secretKey
            .signWith(signatureAlgorithm, secretKey.getBytes(StandardCharsets.UTF_8))
            // 设置过期时间
            .setExpiration(exp);

    // 拼接成三段式JWT字符串返回
    return builder.compact();
}
```

其中 controller 层中的：
jwtProperties.getAdminSecretKey(),
jwtProperties.getAdminTtl(),
分别代表JWT 签名重要组成部分 secretKey和过期时间，这两个是在 yml 中配置的：

```
sky:  
  jwt:  
    # 设置jwt签名加密时使用的秘钥  
    admin-secret-key: itcast  
    # 设置jwt过期时间  
    admin-ttl: 7200000  
    # 设置前端传递过来的令牌名称  
    admin-token-name: token
```

在此强调itcast 的意义
我们需要知道：
- 首先 itcast 是是一串固定的密码（密钥），是整个后端项目共用的，所有管理员用户都共用这同一个密钥，不是某一个人的专属标识
- 生成 token 时候，需要签名+payload+header，而签名是使用 Header+Payload+itcast 做 HS256 加密生成的，Payload 就是 claims（employeeId），是 token 的具体数据
- 而在校验 token 的时候，拦截器拿到前端传的 token，拿 itcast （因为 itcast 不会变化）计算签名（itcast+payload+header）和 token 中的第三段（原来的签名），如果是签名一致合法；不一致不合法拒绝访问
- 通过后再校验过期时间，解析出 `empId` 存入 `BaseContext`，放行请求。请求结束后清理 `ThreadLocal`。