
管理端：

![[截屏2026-10-01 00.20.10.png]]

员工端：

![[截屏2026-10-01 00.21.24.png]]


Orders 类中的状态机：

```
1 PENDING_PAYMENT  待提交（原"待付款"，新流程基本闲置，无任何代码路径会写入 1）
2 TO_BE_CONFIRMED  待审批   ← submitOrder 落库即此状态
3 CONFIRMED        采购中   ← confirm / 管理员核销前置
4 DELIVERY_IN_PROGRESS 配送中 ← delivery
5 COMPLETED        已完成   ← complete / confirmReceipt
6 CANCELLED        已取消   ← userCancelById / rejection / cancel / returnOrder  【三态合一】
```

## 链路1：提交申领单

POST/user/order/submit
提交 OrderSubmitDTO 相关参数

JWT 部分的内容在 M 1 部分会进行详细阐述

Controller 层调用 submit

![[截屏2026-09-30 23.46.16.png]]


[[M2部门预算模块#链路 4：预算预扣（核心，也是我觉得可以修改的地方）]]

一模一样


## 链路2：员工撤销/管理员驳回/管理员取消

[[M2部门预算模块#链路5：预算返回]]


## 链路3：审核通过/发货/核销/确认收货

管理员审核通过
confirm
![[截屏2026-10-01 09.38.06.png|386]]

管理员发货：
delivery
![[截屏2026-10-01 09.39.33.png|370]]


管理员核销
complete
![[截屏2026-10-01 09.42.18.png]]

员工确认收货：
confirmReceipt
![[截屏2026-10-01 09.35.58.png|371]]


这个地方是有问题的，后续修改方向是管理员核销是在任意阶段都可以操作（我自己认为的），同时 `complete` 和 `confirmReceipt` 的**并发问题也和 M 3-1 是同一个**——两个请求同时调（一个员工确认、一个管理员核销）都会通过 `status == 4` 校验、都写 `delivery_time`，**后者覆盖前者的时间戳**。



## 链路 4：员工端分页查询(不同状态申领查询没有实现)

user/OrderController.page 
➡️
![[截屏2026-10-01 09.56.49.png]]

setUserId(...)强制只查询和自己有关的申领单


## 链路 5：管理端条件搜索

![[截屏2026-10-01 10.12.04.png]]

xml 实现条件查询，注意和用户端作区分，这里是通过 DTO 里面的 number，phone 等参数来查询，用户端是用户 id 来查询

![[截屏2026-10-01 10.13.11.png]]



## 链路 6：订单统计

![[截屏2026-10-01 10.18.33.png]]

GET/admin/order/statistics

![[截屏2026-10-01 10.19.15.png|542]]


## 链路 7：催办

GET/user/order/reminder/{id}

![[截屏2026-10-01 10.34.06.png]]

通过 redis 限流，读 TTL 返回剩余 N 秒