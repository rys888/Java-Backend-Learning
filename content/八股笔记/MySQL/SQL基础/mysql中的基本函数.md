MySQL 中的常用函数可以分为 **字符串函数、数值函数、日期时间函数、聚合函数、流程控制函数** 五大类。

对于 Java 后端实习面试，重点掌握每类函数的作用、基本用法，以及它们在实际 SQL 查询中的应用即可。

# **一、字符串函数

字符串函数主要用于处理字符串，例如拼接、截取、替换等。

|**函数**|**作用**|**示例**|
|---|---|---|
| `CONCAT()` |拼接字符串| `CONCAT('Hello', 'World')` |
| `LOWER()` |转换为小写| `LOWER('HELLO')` |
| `UPPER()` |转换为大写| `UPPER('hello')` |
| `LENGTH()` |获取字符串字节长度| `LENGTH('abc')` |
| `CHAR_LENGTH()` |获取字符串字符数量| `CHAR_LENGTH('你好')` |
| `SUBSTRING()` |截取字符串| `SUBSTRING('abcdef', 1, 3)` |
| `TRIM()` |去除字符串首尾空格| `TRIM(' hello ')` |
| `REPLACE()` |替换字符串内容| `REPLACE('Java8', '8', '17')` |
| `LPAD()` |左侧填充字符串| `LPAD('123', 5, '0')` |
| `RPAD()` |右侧填充字符串| `RPAD('123', 5, '0')` |

### **1. CONCAT：字符串拼接**

```sql
SELECT CONCAT('Hello', ' ', 'World');
```

结果：

```text
Hello World
```

实际应用：

```sql
SELECT CONCAT(first_name, last_name) AS full_name
FROM employee;
```

将员工的姓和名拼接起来。

### **2. SUBSTRING：截取字符串**

```sql
SELECT SUBSTRING('abcdef', 1, 3);
```

结果：

```text
abc
```

注意：**MySQL 字符串位置通常从 1 开始，而不是 Java 中的 0。**

### **3. LENGTH 和 CHAR_LENGTH 的区别**

```sql
SELECT LENGTH('你好');
```

在 UTF-8 的 `utf8mb4` 字符集下，结果为：

```text
6
```

因为每个汉字通常占 3 个字节。

而：

```sql
SELECT CHAR_LENGTH('你好');
```

结果为：

```text
2
```

因为字符串只有两个字符。

**面试重点：**** `LENGTH()` ** **返回字节数，**** `CHAR_LENGTH()` ** **返回字符数。**

---

# **二、数值函数 ⭐⭐⭐⭐**

数值函数主要用于数学计算、取整和随机数生成。

|**函数**|**作用**|**示例**|**结果**|
|---|---|---|---|
| `ABS()` |绝对值| `ABS(-10)` |10|
| `CEIL()` |向上取整| `CEIL(3.2)` |4|
| `FLOOR()` |向下取整| `FLOOR(3.8)` |3|
| `ROUND()` |四舍五入| `ROUND(3.14159, 2)` |3.14|
| `TRUNCATE()` |截断小数| `TRUNCATE(3.14159, 2)` |3.14|
| `MOD()` |取余| `MOD(10, 3)` |1|
| `RAND()` |生成随机数| `RAND()` |[0,1)|
| `POW()` |幂运算| `POW(2, 3)` |8|

### **1. ROUND：四舍五入**

```sql
SELECT ROUND(3.14159, 2);
```

结果：

```text
3.14
```

例如计算商品平均价格：

```sql
SELECT ROUND(AVG(price), 2)
FROM product;
```

表示保留两位小数。

### **2. CEIL 和 FLOOR**

```sql
SELECT CEIL(3.2);  -- 4

SELECT FLOOR(3.8); -- 3
```

实际业务中，可以用于计算分页总页数：

```sql
SELECT CEIL(COUNT(*) / 10)
FROM employee;
```

假设共有 23 条记录，每页 10 条，那么结果为 3 页。

---

# **三、日期时间函数 ⭐⭐⭐⭐⭐**

日期时间函数在 Java 后端开发中使用非常频繁，例如订单创建时间、预约时间、用户注册时间等。

|**函数**|**作用**|**示例**|
|---|---|---|
| `NOW()` |获取当前日期和时间| `NOW()` |
| `CURDATE()` |获取当前日期| `CURDATE()` |
| `CURTIME()` |获取当前时间| `CURTIME()` |
| `YEAR()` |提取年份| `YEAR('2026-10-11')` |
| `MONTH()` |提取月份| `MONTH('2026-10-11')` |
| `DAY()` |提取日期中的日| `DAY('2026-10-11')` |
| `DATE_FORMAT()` |格式化日期| `DATE_FORMAT(NOW(), '%Y-%m-%d')` |
| `DATEDIFF()` |计算两个日期相差的天数| `DATEDIFF('2026-10-11', '2026-10-01')` |
| `TIMESTAMPDIFF()` |计算指定单位的时间差| `TIMESTAMPDIFF(HOUR, start_time, end_time)` |
| `DATE_ADD()` |日期加上指定时间| `DATE_ADD(NOW(), INTERVAL 7 DAY)` |
| `DATE_SUB()` |日期减去指定时间| `DATE_SUB(NOW(), INTERVAL 7 DAY)` |

### **1. NOW：获取当前时间**

```sql
SELECT NOW();
```

返回当前日期和时间。

实际应用：

```sql
INSERT INTO orders (user_id, create_time)
VALUES (1001, NOW());
```

用于记录订单创建时间。

### **2. DATE_FORMAT：格式化日期**

```sql
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d');
```

结果类似：

```text
2026-10-11
```

常见格式：

|**格式**|**含义**|
|---|---|
| `%Y` |四位年份|
| `%m` |两位月份|
| `%d` |两位日期|
| `%H` |小时（24 小时制）|
| `%i` |分钟|
| `%s` |秒|

例如：

```sql
SELECT DATE_FORMAT(
    NOW(),
    '%Y-%m-%d %H:%i:%s'
);
```

### **3. DATEDIFF：计算日期差**

```sql
SELECT DATEDIFF(
    '2026-10-11',
    '2026-10-01'
);
```

结果：

```text
10
```

表示两个日期相差 10 天。

需要注意，`DATEDIFF()` 只比较日期部分，忽略具体时分秒。

### **4. DATE_ADD：日期加减**

```sql
SELECT DATE_ADD(
    NOW(),
    INTERVAL 7 DAY
);
```

表示获取当前时间 7 天后的时间。

例如查询最近 7 天的订单：

```sql
SELECT *
FROM orders
WHERE create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

这个写法在实际项目中非常常见。

---

# **四、聚合函数 ⭐⭐⭐⭐⭐**

聚合函数主要用于**对多条记录进行统计计算**。

这是 MySQL 面试和实际开发中最重要的一类函数。

|**函数**|**作用**|**示例**|
|---|---|---|
| `COUNT()` |统计数量| `COUNT(*)` |
| `SUM()` |求和| `SUM(amount)` |
| `AVG()` |求平均值| `AVG(score)` |
| `MAX()` |获取最大值| `MAX(price)` |
| `MIN()` |获取最小值| `MIN(price)` |

假设存在员工表：

|**id**|**name**|**department_id**|**salary**|
|---|---|---|---|
|1|张三|101|8000|
|2|李四|101|10000|
|3|王五|102|12000|

### **1. COUNT：统计数量**

```sql
SELECT COUNT(*)
FROM employee;
```

结果：

```text
3
```

这里需要注意：

```sql
COUNT(*)
```

统计所有行。

而：

```sql
COUNT(salary)
```

只统计 `salary` 不为 `NULL` 的行。

### **2. SUM：求和**

```sql
SELECT SUM(salary)
FROM employee;
```

结果：

```text
30000
```

### **3. AVG：平均值**

```sql
SELECT AVG(salary)
FROM employee;
```

结果：

```text
10000
```

注意，`AVG()` 会忽略 `NULL` 值。

### **4. GROUP BY：结合聚合函数分组统计**

例如查询每个部门的平均工资：

```sql
SELECT
    department_id,
    AVG(salary) AS avg_salary
FROM employee
GROUP BY department_id;
```

结果：

|**department_id**|**avg_salary**|
|---|---|
|101|9000|
|102|12000|

如果希望查询平均工资大于 10000 的部门：

```sql
SELECT
    department_id,
    AVG(salary) AS avg_salary
FROM employee
GROUP BY department_id
HAVING AVG(salary) > 10000;
```

这里涉及两个关键字：

- `WHERE`：对分组前的数据进行过滤。
- `HAVING`：对分组后的结果进行过滤。

**面试重点：WHERE 不能直接使用聚合函数筛选分组结果，而 HAVING 可以。**

---

# **五、流程控制函数 ⭐⭐⭐⭐**

流程控制函数主要用于条件判断。

|**函数**|**作用**|
|---|---|
| `IF()` |根据条件返回不同结果|
| `IFNULL()` |判断是否为 NULL|
| `NULLIF()` |两个值相等时返回 NULL|
| `CASE WHEN` |实现多条件判断|

### **1. IF：条件判断**

语法：

```sql
IF(条件, 条件成立返回值, 条件不成立返回值)
```

例如：

```sql
SELECT IF(90 >= 60, '及格', '不及格');
```

结果：

```text
及格
```

实际应用：

```sql
SELECT
    name,
    salary,
    IF(salary >= 10000, '高薪', '普通') AS salary_level
FROM employee;
```

### **2. IFNULL：处理 NULL**

语法：

```sql
IFNULL(字段, 默认值)
```

例如：

```sql
SELECT IFNULL(NULL, 0);
```

结果：

```text
0
```

实际应用：

```sql
SELECT IFNULL(SUM(amount), 0)
FROM orders
WHERE user_id = 1001;
```

如果用户没有订单，`SUM(amount)` 可能返回 `NULL`，通过 `IFNULL()` 可以转换为 0。

### **3. CASE WHEN：多条件判断**

例如，根据员工工资划分等级：

```sql
SELECT
    name,
    salary,
    CASE
        WHEN salary >= 15000 THEN '高级'
        WHEN salary >= 10000 THEN '中级'
        ELSE '初级'
    END AS salary_level
FROM employee;
```

其逻辑类似 Java 中的：

```java
if (salary >= 15000) {
    return "高级";
} else if (salary >= 10000) {
    return "中级";
} else {
    return "初级";
}
```

---

# **六、Java 后端开发中最值得掌握的函数**

对于 Java 后端实习面试，我建议你优先掌握以下函数：

|**类别**|**重点函数**|**常见业务场景**|
|---|---|---|
|字符串| `CONCAT()`、`SUBSTRING()`、`LENGTH()` |字符串处理|
|数值| `ROUND()`、`CEIL()`、`FLOOR()` |金额计算、分页|
|日期| `NOW()`、`DATE_FORMAT()`、`DATE_ADD()`、`DATEDIFF()` |订单、预约、时间统计|
|聚合| `COUNT()`、`SUM()`、`AVG()`、`MAX()`、`MIN()` |数据统计、报表|
|流程控制| `IF()`、`IFNULL()`、`CASE WHEN` |条件判断、空值处理|

其中，**聚合函数、日期时间函数和** ** `IFNULL()` ** **在实际业务开发中尤其常见。**

另外，还有两个容易在面试中被问到的知识点。

**① COUNT(*)、COUNT(1)、COUNT(字段) 有什么区别？**

- `COUNT(*)`：统计满足条件的所有行。
- `COUNT(1)`：统计满足条件的所有行。
- `COUNT(字段)`：只统计该字段不为 NULL 的行。

`COUNT(*)` 和 `COUNT(1)` 在 MySQL 中通常性能接近，没有必要为了优化而机械地替换。

**② SQL 函数会影响索引吗？**

例如：

```sql
SELECT *
FROM orders
WHERE YEAR(create_time) = 2026;
```

由于对索引列 `create_time` 使用了函数，普通的 `create_time` B+ 树索引通常无法直接用于该条件的范围查找。

更推荐：

```sql
SELECT *
FROM orders
WHERE create_time >= '2026-01-01'
  AND create_time < '2027-01-01';
```

这样更有利于利用 `create_time` 上的普通索引进行范围查询。

需要注意，MySQL 8.0 支持函数索引等机制，所以不能绝对地说“字段使用函数就一定不走索引”。

---

## **七、面试怎么回答？**

如果面试官问：

**“MySQL 中有哪些常用函数？”**

可以这样回答：

MySQL 中的常用函数主要分为五类。

第一类是字符串函数，例如 CONCAT、SUBSTRING、LENGTH，用于字符串拼接、截取和长度计算。

第二类是数值函数，例如 ROUND、CEIL、FLOOR，用于四舍五入和取整。

第三类是日期时间函数，例如 NOW、DATE_FORMAT、DATEDIFF 和 DATE_ADD，主要用于时间处理。

第四类是聚合函数，例如 COUNT、SUM、AVG、MAX、MIN，通常结合 GROUP BY 实现分组统计。

第五类是流程控制函数，例如 IF、IFNULL 和 CASE WHEN，用于条件判断和空值处理。

在实际开发中，我使用较多的是聚合函数和日期时间函数，例如统计订单数量、计算采购金额以及查询最近一段时间的业务数据。

**最后总结：MySQL 常用函数重点掌握字符串、数值、日期、聚合和流程控制五大类，其中聚合函数和日期函数是 Java 后端面试的重点。**