MyBatis 中 `#{}` 和 `${}` 的区别是 Java 后端面试的高频考点。

**核心区别：**** `#{}`  **使用预编译参数绑定，而**  `${}`  **直接进行字符串替换。**

## **一、#{ } 和 ${ } 的区别 ⭐⭐⭐⭐⭐**

|**对比**| `#{}` | `${}` |
|---|---|---|
|实现原理|通过 `PreparedStatement` 进行参数绑定|直接将参数值拼接到 SQL 中|
|SQL 处理|转换为 `?` 占位符|直接替换为参数内容|
|SQL 注入|能有效防止参数值导致的 SQL 注入|存在 SQL 注入风险|
|字符串处理|自动作为参数值处理|不会自动添加引号|
|使用场景|普通 SQL 参数传递|动态表名、列名、排序字段等|
|推荐程度|**优先使用**|仅在必要时使用|

---

## **二、#{ }：预编译参数绑定**

假设我们要根据用户名查询用户。

MyBatis Mapper：

```java
@Select("SELECT * FROM user WHERE username = #{username}")
User selectByUsername(String username);
```

传入：

```java
username = "Eason";
```

MyBatis 会将 SQL 处理为：

```sql
SELECT * FROM user WHERE username = ?
```

然后通过 `PreparedStatement` 绑定参数：

```java
preparedStatement.setString(1, "Eason");
```

最终数据库执行的是带有参数值的查询。

### **为什么能够防止 SQL 注入？**

假设用户输入：

```text
' OR '1'='1
```

如果使用 `#{}`：

```sql
SELECT * FROM user WHERE username = ?
```

MyBatis 会把整段输入作为一个普通字符串参数。

数据库不会将其中的 `OR` 当成 SQL 逻辑运算符执行。

**因为 SQL 结构和参数值是分开处理的。**

---

## **三、${ }：字符串直接替换**

例如：

```java
@Select("SELECT * FROM user WHERE username = '${username}'")
User selectByUsername(String username);
```

传入：

```java
username = "Eason";
```

MyBatis 会直接替换字符串，得到：

```sql
SELECT * FROM user WHERE username = 'Eason'
```

看起来和 `#{}` 的查询结果一样，但底层处理方式完全不同。

### **为什么存在 SQL 注入风险？**

假设用户输入：

```text
' OR '1'='1
```

SQL 就会变成：

```sql
SELECT * FROM user WHERE username = '' OR '1'='1'
```

由于：

```sql
'1'='1'
```

始终成立，可能导致查询返回大量不应该返回的数据。

**这就是 SQL 注入：用户输入被直接拼接进 SQL，改变了原本的 SQL 语义。**

---

## **四、为什么有了 #{}，还需要 ${}？⭐⭐⭐⭐⭐**

因为有些 SQL 位置不能使用 `?` 占位符。

例如：**动态排序字段**。

假设我们希望根据用户指定的字段排序：

```sql
SELECT * FROM user ORDER BY create_time
```

如果使用：

```java
@Select("SELECT * FROM user ORDER BY #{column}")
List<User> selectUsers(String column);
```

MyBatis 会将 SQL 处理为：

```sql
SELECT * FROM user ORDER BY ?
```

这里的 `?` 代表一个参数值，而不是 SQL 中的列名。

因此无法实现预期的动态列排序。

这时候就需要：

```java
@Select("SELECT * FROM user ORDER BY ${column}")
List<User> selectUsers(String column);
```

传入：

```java
column = "create_time";
```

最终 SQL：

```sql
SELECT * FROM user ORDER BY create_time
```

这样才能按照指定列排序。

**但是这里存在安全风险！**

如果 `column` 来自用户输入，不能直接拼接。

正确做法是使用白名单校验：

```java
public List<User> selectUsers(String column) {

    Set<String> allowedColumns =
            Set.of("id", "username", "create_time");

    if (!allowedColumns.contains(column)) {
        throw new IllegalArgumentException("非法排序字段");
    }

    return userMapper.selectUsers(column);
}
```

这样就能限制动态 SQL 只能使用允许的字段。

注意：上面 `Set.of()` 是 Java 9 引入的；如果项目使用 Java 8，可以改用 `HashSet` 等方式构建白名单。

---

## **五、面试怎么回答？⭐⭐⭐⭐⭐**

如果面试官问：

**“MyBatis 中**  `#{}`  **和**  `${}`  **有什么区别？”**

可以这样回答：

MyBatis 中 `#{}` 和 `${}` 的主要区别在于参数处理方式。

`#{}` 使用预编译参数绑定，MyBatis 会将参数转换为 SQL 中的 `?` 占位符，再通过 `PreparedStatement` 设置参数值，因此能够有效防止 SQL 注入。

而 `${}` 是直接进行字符串替换，会将参数内容拼接到 SQL 中，因此存在 SQL 注入风险。

实际开发中，普通查询条件一般使用 `#{}`，而动态表名、列名、排序字段等无法使用占位符的位置，才考虑使用 `${}`，并且必须通过白名单等方式校验参数。

### **最后总结**

 `#{}`  **是参数绑定，**** `${}` **是字符串拼接。**

记住两个例子即可：

```sql
-- 推荐：查询条件
SELECT * FROM user WHERE id = #{id}

-- 特殊场景：动态排序字段（必须白名单校验）
SELECT * FROM user ORDER BY ${column}
```

**实际开发中，能用**  `#{}`  **就不要用**  `${}` ****。**