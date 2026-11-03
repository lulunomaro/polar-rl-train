# 阶段1 V2：已进入SDK环境构造，停在原reset调用链身份核验

## 实际结果

V2使用全新root、独立once markers及完整3675-file静态安装；真实Linux preflight已走同一个原helper bootstrap，两个完整模块的路径／来源／PIN核验通过。随后原parent通过原资源门，实际worker进入E3环境构造和原初始化路径。

本次未取得采样：在安装被动sensor observer的preflight中，`env._reset_idx`与固定的`RecoveryEnv._reset_idx`身份不匹配，执行在共同GO/READY/FINAL之前结束。

| 事实 | 回执 |
|---|---|
| controller／parent／worker | 1543093／1543101／1543111 |
| worker实际wait | RC0，但同时有WORKER_ERROR；RC0不是成功 |
| 外层实际parent wait | RC1，controller_errors为空 |
| 原parent结束 | wall16.3802秒、own child已实际wait、privateGPU EX及finite EX均释放 |
| 控制/模型/训练producer计数 | 缺FINAL，保持null；不生成技能分数 |
| Gate1／阶段2 | UNKNOWN／未放行 |

[完整闭合回执](<reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json>) · [紧凑事实](<reports/PHASE1_CAPTURE_V2_CLOSED_LIVE_BINDING_FAILURE_FACTS_V1.json>)。

V1的bootstrap遗漏已越过；此次是更后的SDK初始化／observer绑定路径，不是再次发生同一MissingModule，也不是物理技能退化。

## 已确认的源码缺口与尚缺的现场身份

原B preflight直接把`env._reset_idx`当作class RecoveryEnv descriptor核验。然而原完整D5/D6/D7 source会安装不带`__wrapped__`的四层`MethodType` reset wrapper，固定源码的E3外→内顺序为：

```text
ExplicitPDSDK reset wrapper
  → ChassisCOMSDK reset wrapper
  → GasDampingSDK reset wrapper
  → SpringPressureSDK reset wrapper
  → RecoveryEnv._reset_idx
```

每层都先调用闭包里的`original(ids)`，再调用对应adapter的原`reset(ids)`。这个source composition与现场identity mismatch相符；**现场错误只打印了expected名称，没有实际outer module/qualname/co_filename/closure，因此真实outer及完整链仍标UNKNOWN**。

NEW B2将保留原class descriptor固定PIN，并逐层验证原wrapper完整source/code、bound self、closure.original以及closure.adapter与同env实际实例属性／MRO；错层、重复、外env、未知wrapper继续失败。不会简单跳过qualname/module、动态重pin expected或改原D7以通过核验。补只读诊断字段和真实已发布函数的composition测试，不额外调用SDK getter、obs、step、reset或随机采样。

原V1/V2 root及封件保持；新传递包采用独立V3 source/root。H1、母本、原物理/DR和原技能接受不变，Stage2 native继续关闭。当前GPU已释放，等待正在推进的严格source修复；不是保持scene空转。此报告待阶段32追加归档。
