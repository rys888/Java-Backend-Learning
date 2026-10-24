 Spring 主要通过声明式事务和编程式事务管理数据库事务。

 声明式事务最常用，通过在 Service 层方法上添加 `@Transactional` 注解，实现事务的自动开启、提交和回滚。
 
 底层基于 Spring AOP 动态代理。当外部调用事务方法时，会先经过 `TransactionInterceptor`，由 `PlatformTransactionManager` 管理事务。
 
 如果方法正常执行，则提交事务；如果抛出符合回滚规则的异常，则回滚事务。

另外，还可以通过 **`TransactionTemplate`** 实现编程式事务，适合需要灵活控制事务边界的场景。

实际开发中，我一般使用 `@Transactional(rollbackFor = Exception.class)`，并将事务放在 Service 层，保证多个数据库操作的一致性。