
ThreadLocal 使用不当可能导致**内存泄漏**，主要注意事项：
- 务必在不再使用时调用 `remove()` 方法，尤其在使用了线程池的环境中，因为线程复用会导致 ThreadLocal 中的值一直存在，无法被回收。
- 避免使用 ThreadLocal 存储大对象，因为其生命周期与线程绑定，可能长期占用内存。
- ThreadLocal 变量应定义为 `static`，避免创建多个实例（但要注意，static 的 ThreadLocal 本身不会被回收，但其值可能因线程存活而存在）。

在项目中防止 OOM 的做法：
- 在使用 ThreadLocal 的代码块结束后，主动调用 `ThreadLocal.remove()` 清理。
- 使用 try-finally 块确保移除操作一定执行。
- 对于 Web 应用，在拦截器或过滤器中统一处理，在请求结束后清除当前线程的 ThreadLocal。