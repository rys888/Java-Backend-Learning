---
aliases:
  - "SQL基础"
title: "SQL基础"
---

[[NOSQL和SQL区别]]
[[三大范式]]
[[CHAR和VARCHAR有什么区别]]
[[INT(1)和INT(10)在mysql有什么不同]]
[[外键约束]]
[[mysql中的基本函数]]
[[DELETE、TRUNCATE 和 DROP 有什么区别？]]







SELECT * FROM Customers WHERE Country IN ('Germany','France');
SELECT column_name(s) FROM table_name WHERE EXISTS (SELECT column_name FROM another_table WHERE condition);


**找出：选了 02 号课，但是没有选 01 号课的学生，以及他 02 课程的分数。**

```
SELECT s.sid, s.sname, sc.score
FROM Student s
INNER JOIN Score sc ON s.sid = sc.sid AND sc.cid='02'
WHERE NOT EXISTS (
    SELECT 1 FROM Score sc1
    WHERE sc1.sid = s.sid AND sc1.cid='01'
);
```


给定一个学生表 student_score(stu_id, subject_id, score), 查询总分排名在 5-10 名的学生 i 问 d 及对应的总分

```
SELECT t1.stu_id, t1.total_score
FROM (
    SELECT stu_id, SUM(score) AS total_score
    FROM student_score
    GROUP BY stu_id
    ORDER BY total_score DESC
) t1
LIMIT 4,6;
```


查询班级名称为 'Class A' 的全部学生的选课情况

```
SELECT
    s.student_id,
    s.student_name,
    cs.course_name
FROM
    students s
LEFT JOIN
    course_selections cs ON s.student_id = cs.student_id
JOIN
    classes c ON s.class_id = c.class_id
WHERE
    c.class_name = 'Class A';
```

用 LEFT JOIN，因为题目要求的是所有学生，所以没有选课的同学也会返回
JOIN 两边必须都有匹配数据才保留