# 阅读草稿错误与修正记录

生成讲解时，manager的注释表最初把开关判断起点写为L52，实际是L51；所以该小段草稿说明错位一行。生成后的原始代码行本身始终来自固定source，未被改变。交付前重新读取精确编号L48–65，修正全部说明并重生成。这里保留原错误映射，不能把它作为当前正确注释：

```text
51 | 功能说明。                         [错误：实际是总开关判断]
52 | 总开关关闭。                       [错误：实际是返回空管理器]
53 | 返回空列表管理器。                 [错误：实际是初始化列表]
54 | 初始化有序列表。                   [错误：实际是读取Airborne配置]
55 | 读Airborne配置。                   [错误：实际是enabled判断]
56 | 单项enabled为true。                [错误：实际是append Airborne]
57 | 首先添加Airborne。                 [错误：实际是读取JumpTakeoff配置]
58 | 读JumpTakeoff配置。                [错误：实际是enabled判断]
59 | 单项enabled为true。                [错误：实际是append JumpTakeoff]
60 | 然后添加JumpTakeoff。              [错误：实际是扫描开关判断]
61 | 扫描配置开启。                     [错误：实际是append StepUp]
62 | 添加StepUp。                       [错误：实际是读取Stair配置]
63 | 读Stair配置。                      [错误：实际是enabled判断]
64 | 单项enabled为true。                [错误：实际是append Stair]
65 | 最后添加Stair。                    [错误：实际是return管理器]
```

另一处apply_patch因上下文不匹配拒绝，未改变文件；随后使用完整精确上下文成功追加。一次公开GitHub tree URL读取受限；官方raw README成功。本次不重新复制源码，使用既有逐字节/Git blob验证材料。全部属于阅读/编辑错误，不是训练、资源准入或技能失败；没有生产操作。
