`DispatcherServlet` 是 Spring MVC 的核心组件，也叫前端控制器（Front Controller），主要作用是统一接收 HTTP 请求，并将请求分发给对应的 Controller 处理，最后将处理结果返回给客户端。

你可以把它理解为 Spring MVC 的请求调度中心。

## 一、DispatcherServlet 的工作流程

假设前端发送一个请求：

```
GET /user/1
```

Spring Boot 中存在对应的 Controller：

```
@RestController
@RequestMapping("/user")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getById(id);
    }
}
```

请求执行过程：

```
客户端发送 HTTP 请求
        ↓
Tomcat 接收请求
        ↓
DispatcherServlet（前端控制器）
        ↓
HandlerMapping（根据 URL 查找对应的 Handler）
        ↓
HandlerAdapter（调用对应的 Controller 方法）
        ↓
Controller → Service → Mapper → MySQL
        ↓
Controller 返回执行结果
        ↓
HandlerAdapter 处理返回值
        ↓
HttpMessageConverter（将 Java 对象序列化为 JSON）
        ↓
DispatcherServlet 将响应返回给客户端
```

简化的 REST API 请求流程。实际处理中，DispatcherServlet 还会协调拦截器、异常处理器等组件。

这里要注意，DispatcherServlet 本身不负责执行业务逻辑，而是协调 Spring MVC 的其他组件完成请求处理。

其中：

- HandlerMapping：根据请求 URL 等信息找到对应的处理器。
    
- HandlerAdapter：负责调用对应的 Controller 方法，包括参数解析等。
    
- HttpMessageConverter：在使用 `@ResponseBody` 或 `@RestController` 时，将 Java 对象转换为 JSON 等响应内容。
    

## 二、DispatcherServlet 和 Tomcat 有什么区别？

这是面试很容易追问的地方。

|Tomcat|DispatcherServlet|
|---|---|
|Servlet 容器|Spring MVC 前端控制器|
|接收和处理底层 HTTP 连接|负责 Spring MVC 请求分发|
|管理 Servlet 生命周期|作为 Servlet 运行在 Tomcat 中|
|将请求交给对应 Servlet|将请求交给对应 Controller|

因此，Spring Boot Web 应用的典型流程是：

客户端 → Tomcat → DispatcherServlet → Controller → Service → Mapper → MySQL

## 三、面试怎么回答？

> DispatcherServlet 是 Spring MVC 的核心组件，也叫前端控制器，主要负责统一接收和分发 HTTP 请求。
> 
> 当请求进入 Spring MVC 后，DispatcherServlet 首先通过 HandlerMapping 找到对应的 Controller 方法，再通过 HandlerAdapter 调用该方法。
> 
> Controller 执行业务逻辑后，DispatcherServlet 会协调完成返回值处理。对于 RESTful 接口，通常通过 HttpMessageConverter 将对象序列化为 JSON，最终返回给客户端。
> 
> 因此，DispatcherServlet 本质上是 Spring MVC 的请求调度中心，通过统一调度实现请求处理流程与业务逻辑的解耦。

一句话记忆：Tomcat 负责把 HTTP 请求交给 Servlet，DispatcherServlet 负责把请求分发给 Spring MVC 中对应的 Controller。