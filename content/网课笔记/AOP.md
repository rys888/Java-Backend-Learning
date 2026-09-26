### 什么是 AOP？
面向切面编程
AOP 是在不改动原有业务代码的前提下，对方法做增强。
可以理解成：  
在某个方法执行前/后，自动插入一段公共逻辑。


### 在苍穹外卖中 AOP 起什么作用呢？
- 拦截 Mapper 的`insert` 方法  → 自动设置 `createTime`、`updateTime`、`createUser`、`updateUser`
- 拦截 `update` 方法  → 自动设置 `updateTime`、`updateUser`

这部分的伪代码大概如下：

```
@Aspect
@Component
public class AutoFillAspect {

    @Before("@annotation(autoFill)")
    public void autoFill(JoinPoint joinPoint, AutoFill autoFill) {
        Object entity = joinPoint.getArgs()[0]; // 拿到要插入/更新的对象

        if (autoFill.value() == OperationType.INSERT) {
            setField(entity, "createTime", LocalDateTime.now());
            setField(entity, "updateTime", LocalDateTime.now());
            setField(entity, "createUser", CurrentUserUtil.getUserId());
            setField(entity, "updateUser", CurrentUserUtil.getUserId());
        }

        if (autoFill.value() == OperationType.UPDATE) {
            setField(entity, "updateTime", LocalDateTime.now());
            setField(entity, "updateUser", CurrentUserUtil.getUserId());
        }
    }
}
```

然后在 Mapper 方法上加注解：

```
@AutoFill(OperationType.INSERT)
void insert(User user);

@AutoFill(OperationType.UPDATE)
void update(User user);
```

因为 insert 和 update 不可避免的需要添加 time 和 user 了，这样就不用在 service 层中反复写 setCreateTime 和 setCreateUser 了

## 具体的在苍穹外卖中如何实现 AOP 呢（主要代码分析）？

**自定义注解**
AutoFill.java
```
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AutoFill {

    OperationType value(); // INSERT / UPDATE
}
```
给 Mapper 方法打标记，告诉程序这个方法是新增和修改操作 
AOP 切面会拦截带有该注解的 Mapper 方法，在方法执行前自动填充公共字段（createTime、updateTime、createUser、updateUser）。

**枚举**
OperationType.java
```
package com.sky.annotation;

/**
 * 数据库操作类型枚举
 */
public enum OperationType {

    INSERT,

    UPDATE
}
```

**Mapper**
```
@AutoFill(OperationType.INSERT) //标记这是新增操作，触发AOP填充 @Insert("insert into dish values(#{id},#{name},#{categoryId},#{price},#{image},#{description},#{status},#{createTime},#{updateTime},#{createUser},#{updateUser})") 
void insert(Dish dish);
```


**切面**(AOP 核心)
AutoFillAspect.java
```
/**
 * 自定义切面，实现公共字段自动填充
 */
@Aspect
@Component
@Slf4j
public class AutoFillAspect {
    /**
     * 切入点
     */
    @Pointcut("execution(* com.sky.mapper.*.*(..)) && @annotation(com.sky.annotation.AutoFill)")
    public void autoFillPointCut(){

    }

    /**
     * 前置通知，在通知中进行公共字段赋值
     */
    @Before("autoFillPointCut()")
    public void autoFill(JoinPoint joinPoint) throws NoSuchMethodException {
        log.info("开始进行公共字段自动填充....");

        //获取当前被拦截的方法上的数据库操作类型
        MethodSignature signature= (MethodSignature) joinPoint.getSignature();
        AutoFill autoFill=signature.getMethod().getAnnotation(AutoFill.class);
        OperationType operationType=autoFill.value();

        //获取实体对象
        Object[] args= joinPoint.getArgs();
        if(args==null||args.length==0){
            return;
        }

        Object entity=args[0];
        
        //准备赋值数据
        LocalDateTime now=LocalDateTime.now();
        Long currentId= BaseContext.getCurrentId();
        
        
        //赋值
        if(operationType==OperationType.INSERT){
            //四个公共字段赋值
            try{
                Method setCreateTime=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_CREATE_TIME, LocalDateTime.class);
                Method setCreateUser=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_CREATE_USER,Long.class);
                Method setUpdateTime=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_UPDATE_TIME, LocalDateTime.class);
                Method setUpdateUser=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_UPDATE_USER, Long.class);

                setCreateTime.invoke(entity,now);
                setCreateUser.invoke(entity,currentId);
                setUpdateTime.invoke(entity,now);
                setUpdateUser.invoke(entity,currentId);
            } catch (Exception e){
                e.printStackTrace();
            }

        } else if (operationType==OperationType.UPDATE) {
            try{
                Method setUpdateTime=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_UPDATE_TIME, LocalDateTime.class);
                Method setUpdateUser=entity.getClass().getDeclaredMethod(AutoFillConstant.SET_UPDATE_USER, Long.class);
                setUpdateTime.invoke(entity,now);
                setUpdateUser.invoke(entity,currentId);
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    }
}
```


### 值得注意的点

切入点说明：
@Pointcut 定义切入点表达式：
1. `execution(* com.sky.mapper.*.*(..))`：匹配 `com.sky.mapper` 包下所有类、所有方法
2. `&& @annotation(com.sky.annotation.AutoFill)`：并且方法上带有 @AutoFill 自定义注解
合起来含义：只有 mapper 包下，并且标记了 @AutoFill 注解的方法，才会被 AOP 拦截
比如：
@AutoFill(OperationType.INSERT) 
void insert (Dish dish);
3. 而 autoFillPointCut() 是空方法，只是一个切入点签名，用来被通知引用，方法体不会执行



```
//准备赋值数据 
LocalDateTime now=LocalDateTime.now(); 
Long currentId= BaseContext.getCurrentId();
```
BaseContext.getCurrentId()：从 ThreadLocal 获取当前登录用户 id（员工 id）



判断是新增还是更新，用反射调用 setter 赋值
```
// 方法名字符串
String methodName = "setCreateTime";
// entity 可能是 Dish、Employee、Setmeal，不确定是哪个实体类
Method setCreateTime = entity.getClass().getDeclaredMethod(methodName, LocalDateTime.class);
// 执行这个set方法，等价于 entity.setCreateTime(now)
setCreateTime.invoke(entity, now);
```

第二行代码就是在反射：在运行时，拿到对象的字节码，根据方法名字符串去类里面查找对应的方法。
getDeclaredMethod(方法名,参数类型)
entity.getClass()：反射入口，拿到这个对象对应的 `Class` 字节码对象
    如果 entity 是 Dish 对象 → 拿到 Dish 的 Class
    如果 entity 是 Employee 对象 → 拿到 Employee 的 Class  
getDeclaredMethod(方法名, 参数类型)：去这个 Class 里面搜索，找一个名字叫 setCreateTime、参数是 LocalDateTime 的方法。

第三行是 invoke 反射调用方法：执行刚才找到的这个方法
invoke(实例对象，传给方法的参数)



# 完整执行流程回顾

1. Service 调用 `dishMapper.insert(dish)`
2. `insert` 方法上有 `@AutoFill(OperationType.INSERT)`
3. AOP 切面匹配切入点，执行 `@Before` 通知
4. JoinPoint 拿到方法、注解、dish 实体对象
5. 反射调用 dish 的 set 方法填充 4 个公共字段
6. 填充完成，执行 MyBatis Insert SQL