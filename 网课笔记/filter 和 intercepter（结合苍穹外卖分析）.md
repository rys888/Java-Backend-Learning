## 全局视角：

浏览器请求 → **Filter（过滤器，Servlet 层）** → DispatcherServlet → **Interceptor（拦截器，SpringMVC 层）** → Controller
返回：Controller → Interceptor → Filter → 浏览器

## Filter:
属于 Servlet 规范，由 Tomcat 容器创建管理，不属于 Spring！
因为不属于 Spring，所以不方便直接使用@Autowired 注入 SpringBean
以下代码演示了如何创建一个过滤器来拦截所有请求并打印日志：

```java
import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import java.io.IOException;

@WebFilter("/*") // 匹配所有请求（注意：Spring Boot 内置 Tomcat 还要在启动类加 @ServletComponentScan，否则这个注解会被忽略、过滤器不生效）
public class LoggingFilter implements Filter {
   @Override
   public void init(FilterConfig filterConfig) throws ServletException {
       System.out.println("过滤器初始化");
   }
   @Override
   public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
           throws IOException, ServletException {
       System.out.println("请求被拦截 - 处理前");
       chain.doFilter(request, response); // 放行请求，刚需，不然所有请求都断在这里
       System.out.println("响应被拦截 - 处理后");
   }
   @Override
   public void destroy() {
       System.out.println("过滤器销毁");
   }
}
```

Filter 的注解方式通过 @WebFilter 注解，`/*` 表示匹配所有请求。
Filter 匹配 `/*` 时，所有请求都会进来，包括 CSS、js 和静态页面等。

Interceptor 会不会被拦到，取决于请求路径有没有命中 addPathPatterns：命中就会进来，静态资源命中了也一样会进来。
之所以静态资源没有被拦住，是因为 preHandle 里手动放行了：

```java
if (!(handler instanceof HandlerMethod)) {
    // 不是 Controller 的方法（静态资源的 handler 是 ResourceHttpRequestHandler），直接放行
    return true;
}
```

也就是说：**不是"拦截器不拦静态资源"，而是"代码里判断后把非 Controller 的请求放行了"**。

## Interceptor

- 属于 SpringMVC 框架，执行位于 DispatcherServlet 之后，Controller 之前。
- 会拦截命中 addPathPatterns 的请求，静态资源不是自动不拦，而是靠上面那行判断放行
- 支持@Autowired 注入 Bean

在苍穹外卖中使用 Interceptor 进行登录校验操作，因为它属于 Spring 组件，可以直接注入 JwtProperties 这类配置 Bean。
（注意：JwtUtil 是纯静态工具类，方法全是 static，不在 Spring 容器里，注入不了也不需要注入，直接 `JwtUtil.parseJWT(...)` 用类名调即可。）

## 苍穹外卖中的 Interceptor（结合 JWT）

| 文件                                                         | 角色                                      |
| ---------------------------------------------------------- | --------------------------------------- |
| `sky-server/.../interceptor/JwtTokenAdminInterceptor.java` | 管理端拦截器，拦 `/admin/**`                    |
| `sky-server/.../interceptor/JwtTokenUserInterceptor.java`  | 用户端拦截器，拦 `/user/**`                     |
| `sky-server/.../config/WebMvcConfiguration.java`           | **注册**两个拦截器 + 配置放行名单                    |
| `sky-common/.../utils/JwtUtil.java`                        | 签发 / 解析 JWT                             |
| `sky-common/.../properties/JwtProperties.java`             | 读 `sky.jwt.*` 配置（两套密钥/过期时间/请求头名）        |
| `sky-common/.../constant/JwtClaimsConstant.java`           | 载荷 key 常量：`empId`、`userId`              |
| `sky-common/.../context/BaseContext.java`                  | `ThreadLocal<Long>`，在拦截器里存、在 Service 里取 |
| `sky-server/.../controller/admin/EmployeeController.java`  | 管理端登录，签发 token                          |
| `sky-server/.../controller/user/UserController.java`       | 用户端微信登录，签发 token                        |
| `sky-server/src/main/resources/application.yml`            | `sky.jwt` 两套配置                          |

**JwtTokenAdminInterceptor.java**

```java
/**  
 * jwt令牌校验的拦截器 */
@Component  
@Slf4j  
public class JwtTokenAdminInterceptor implements HandlerInterceptor {  
  
    @Autowired  
    private JwtProperties jwtProperties;  

    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {  
        //判断当前拦截到的是Controller的方法还是其他资源  
        if (!(handler instanceof HandlerMethod)) {  
            //当前拦截到的不是动态方法，直接放行  
            return true;  
        }  
  
        //1、从请求头中获取令牌  
        String token = request.getHeader(jwtProperties.getAdminTokenName());  
  
        //2、校验令牌  
        try {  
            log.info("jwt校验:{}", token);  
            Claims claims = JwtUtil.parseJWT(jwtProperties.getAdminSecretKey(), token);  
            Long empId = Long.valueOf(claims.get(JwtClaimsConstant.EMP_ID).toString());  
            log.info("当前员工id：", empId);  
            BaseContext.setCurrentId(empId);  
            //3、通过，放行  
            return true;  
        } catch (Exception ex) {  
            //4、不通过，响应401状态码  
            response.setStatus(401);  
            return false;  
        }  
    }  
}
```

这是 JWT 令牌校验的拦截器（上面是管理端拦截器，拦 `/admin/**`）：
- 拿到 token --> 校验 token 中的载荷（claims，其中包含存储的信息，这里是员工 id）--> 校验通过：拿到 empId --> 放入 BaseContext
- 是自定义 SpringMVC 拦截器，专门用来校验管理员端**请求的 JWT 令牌**。在请求进入 Controller 之前执行，校验 token 合法性，解析出管理员 id 存入 `BaseContext`；校验失败直接拦截请求返回 401。

**JwtUtil.parseJWT()** 方法的调用是校验的核心，是定义在**JwtUtil.java** 中的：

```java
public static Claims parseJWT(String secretKey, String token) {  
    // 得到DefaultJwtParser  
    Claims claims = Jwts.parser()  
            // 设置签名的秘钥  
            .setSigningKey(secretKey.getBytes(StandardCharsets.UTF_8))  
            // 设置需要解析的jwt  
            .parseClaimsJws(token).getBody();  
    return claims;
}
```

- `Jwts.parser()`：获取 JWT 解析器
- `.setSigningKey()`：告诉解析器，验证签名要用哪个密钥
- `.parseClaimsJws(token)`：
    - 拆分 token 三段
    - 使用 secretKey 校验签名
    - 校验 exp 过期时间
        ✅ 全部通过：返回 Jws 对象，调用 `.getBody()` 拿到载荷 Claims
        ❌ 任意失败：直接抛出异常（`SignatureException` / `ExpiredJwtException` 等）
- 拦截器外层的 `try-catch` 捕获这个异常，返回 401

**WebMvcConfiguration.java（关键代码截取）**

```java
@Configuration  
@Slf4j  
public class WebMvcConfiguration extends WebMvcConfigurationSupport {  
  
    @Autowired  
    private JwtTokenAdminInterceptor jwtTokenAdminInterceptor;  
    @Autowired  
    private JwtTokenUserInterceptor jwtTokenUserInterceptor;  
  
	@Override
	protected void addInterceptors(InterceptorRegistry registry) {
    	log.info("开始注册自定义拦截器...");
    	// 1、管理员端拦截器：jwtTokenAdminInterceptor
    	registry.addInterceptor(jwtTokenAdminInterceptor)
            	.addPathPatterns("/admin/**")// 拦截匹配 /admin/** 的所有路径
            	.excludePathPatterns("/admin/employee/login"); // 排除登录接口，不拦截

    	// 2、用户端拦截器：jwtTokenUserInterceptor
    	registry.addInterceptor(jwtTokenUserInterceptor)
            	.addPathPatterns("/user/**")// 拦截匹配 /user/** 的所有路径
            	.excludePathPatterns("/user/user/login")// 排除用户登录接口
            	.excludePathPatterns("/user/shop/status");// 排除店铺状态查询接口
}
```

单纯是上述的管理端和用户端拦截器的注册

**JwtUtil.java**

``` 
public class JwtUtil {  
    /**  
     * 生成jwt     
     * 使用Hs256算法, 私匙使用固定秘钥     
     *     
     * @param secretKey jwt秘钥  
     * @param ttlMillis jwt过期时间(毫秒)  
     * @param claims    设置的信息  
     * @return  
     */  
    public static String createJWT(String secretKey, long ttlMillis, Map<String, Object> claims) {  
        // 指定签名的时候使用的签名算法，也就是header那部分  
        SignatureAlgorithm signatureAlgorithm = SignatureAlgorithm.HS256;  
  
        // 生成JWT的时间  
        long expMillis = System.currentTimeMillis() + ttlMillis;  
        Date exp = new Date(expMillis);  
  
        // 设置jwt的body  
        JwtBuilder builder = Jwts.builder()  
                // 如果有私有声明，一定要先设置这个自己创建的私有的声明，这个是给builder的claim赋值，一旦写在标准的声明赋值之后，就是覆盖了那些标准的声明的  
                .setClaims(claims)  
                // 设置签名使用的签名算法和签名使用的秘钥  
                .signWith(signatureAlgorithm, secretKey.getBytes(StandardCharsets.UTF_8))  
                // 设置过期时间  
                .setExpiration(exp);  
  
        return builder.compact();  
    }  
  
    /**  
     * Token解密     
     *     
     * @param secretKey jwt秘钥 此秘钥一定要保留好在服务端, 不能暴露出去, 否则sign就可以被伪造, 如果对接多个客户端建议改造成多个  
     * @param token     加密后的token  
     * @return  
     */  
    public static Claims parseJWT(String secretKey, String token) {  
        // 得到DefaultJwtParser  
        Claims claims = Jwts.parser()  
                // 设置签名的秘钥  
                .setSigningKey(secretKey.getBytes(StandardCharsets.UTF_8))  
                // 设置需要解析的jwt  
                .parseClaimsJws(token).getBody();  
        return claims;  
    }  
  
}
```

JwtUtil 是一个 **JWT 工具类**，封装了 JWT 令牌的生成、解析、校验方法，专门用来创建 token 和解析 token 中的用户信息，在 JWT 拦截器中调用。

## 什么时候该用 Filter 而不是 Interceptor？

Filter 更底层、更通用：跨域处理、字符编码、请求体包装（比如 XSS 过滤、Body 重复读）、全局访问日志——这些要在"进入 Spring MVC 之前"做，就用 Filter。而"要拿到 Controller 方法/注解信息"的（比如 `@AutoFill`、登录校验要知道 handler）就用 Interceptor 或 AOP。
 

## Intercepter 与 JWT 拦截器校验

1）第一次请求：登录（POST /admin/employee/login）

1. 前端提交账号密码，访问登录接口
2. 请求进入 Tomcat，经过 Filter，到达 DispatcherServlet
3. 匹配拦截器配置：`excludePathPatterns("/admin/employee/login")` → **跳过 JwtTokenAdminInterceptor**
4. 进入 EmployeeController 的 login 方法
5. Controller 校验账号密码是否正确
6. 如果账号密码正确：调用 `JwtUtil.generateToken()`，**生成 JWT 令牌**
7. 把 JWT 字符串返回给前端
8. 前端拿到 token，保存在浏览器本地存储（localStorage）

这一步：**只生成 JWT，没有 JWT 校验**。还没 token，自然不需要校验。

2）第二次请求：登录之后，访问业务接口（例如 /admin/dish/list）

前端发请求，请求头带上 `token: JWT字符串`，**这个时候拦截器才会触发 JWT 校验**

1. 浏览器发起请求：`GET /admin/dish/list`，header 携带 token
2. 请求经过 Filter，到达 DispatcherServlet
3. 匹配拦截器规则：`/admin/**`，**进入 JwtTokenAdminInterceptor 的 preHandle ()**
4. preHandle 里面：
    
    - 获取请求头的 token
    - 调用 `JwtUtil.parseJWT(密钥, token)`
    - jjwt 底层校验签名、过期时间
    - 校验成功：取出 empId 放入 BaseContext，return true 放行，进入 DishController
    - 校验失败：catch 捕获异常，设置 401 状态码 return false，请求终止，不会进到 Controller
    
5. Controller 执行业务，可从 BaseContext 拿到当前登录员工 id（用于公共字段自动填充 createUser/updateUser）
6. 请求结束，执行拦截器 `afterCompletion()`，清理 BaseContext 中的 ThreadLocal