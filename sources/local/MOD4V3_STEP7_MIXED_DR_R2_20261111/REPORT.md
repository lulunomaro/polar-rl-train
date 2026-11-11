# 第二轮实际运行记录

第一轮完整DR前进最佳10m为4/10、6/10；同源PhysX nominal前进0/20。选10m完整PPO恢复，本轮唯一修改为20%名义参数+80%原fullDR固定env样本，不改奖励/solver/DR端点；这是假设检验，未把混合视为已解决。先做64env固定父短探针确认分组写回，复用第一轮完整范围4096env与40min numerical0证据；后续在实际首update/检查点核4096采样与训练。


64env探针r1在rollout前因未选中collider仍被旧reset随机而失败；r2修复全shape名义恢复后完成320步，numerical0、20次闭链单envreset。独立probe本身仍用旧25%external/noise默认，不把它写成fullrange探针；主launcher四项fraction全1。主训练2026-11-11 10:24:13启动，PID1007162，完整恢复iter22265。实际STARTUP819nominal/3277fullDR，首update22266、完整11,048,951bytes检查点并核SHA，actorchanged、numerical0，2mm单envreset保留。


5min iter22326、实际302.253s、完整PT11048951bytes/SHA627c1d9f...已核对。MuJoCo名义2.0→2.13807（10/10）、2.2→2.40246（超速0/10），其余四项各10/10，无reset。不是同源PhysX fullDR成绩；当前主训numerical0，待轮末同时检查PhysX名义和fullDR。


10min iter22386、601.558s、完整PT11048951bytes/SHA dcbc1421...已核对。MuJoCo名义前进2.15860/2.41447，两项超速均0/10，后退/旋转/两高度各10/10、无reset。未据此判断同源PhysX；主训numerical仍0，完整DR与名义保护效果待末轮配对。


15min iter22444、900.249s，PT SHA3dd0aac8...下载核对。MuJoCo名义前进2.20120/2.45647，两项超速均0/10，其他四项各10/10，无reset。混合采样收益尚未由同源两分布评测证明；中途不改奖励/solver和DR端点。


20min iter22502/1200.697s，MuJoCo前进2.21825/2.48955；25min iter22560/1502.151s，2.25392/2.51248。四个前进task-check均超速0/10，其他四项各10/10，无reset。各完整PT已下载核SHA；训练numerical0。离线首轮10样本相关诊断未形成因果结论，首次混用XMLbank与runtime关节顺序的诊断标MAPPING_ERROR保留，已用实际runtime order纠正；不据此改DR或声称根因。


30min iter22617、1802.907s、MuJoCo前进2.20856/2.44011；35min iter22674、2100.740s、2.16310/2.39946，两项仍超速0/10；其余四项各10/10，无reset。各PT实体下载核SHA，主训numerical0，未热改support。


本轮完整完成2401.101s、8个检查点及同源配对。保留mixed2_020m作为本轮评测候选，理由见FINAL_REPORT与SELECTED_TRAINED_CANDIDATE；不自动晋升。


末权重MuJoCo前进2.15039/2.37177，均超速0/10，其余四项各10/10，无reset。配对实际2080env/85.377s，numerical0、闭链3次单envreset，包络/action槽误差0。第二轮混合采样带来有限收益，未完成名义能力恢复。相同2080env配对内：20m候选fullDR前进由直接父9/20升到11/20，正式六项39/60→41/60，二者正式reset0；名义前进MAE0.30816→0.25420，但仍0/20。40m末模型fullDR前进回到9/20、名义MAE0.32516，继续堆本配方的时间没有持续收益。保留20m诊断候选，25m总43/60但1reset另存备用；原已接受push020/主冻结不晋升替换，未启动第三轮。下一步固定权重在同源环境核对名义/DR前进偏差的执行、观测与稳态受力，再按定位结果修一项，不直接追加长训。


## 用户质疑后的回放环境复核

固定mixed2_020m完成0/5ms两引擎短回放：[环境与速度方向复核](replay_environment_check/REPORT.md)。MuJoCo仍超速、PhysX名义仍欠速；160env原混合训练类与paired评测包装的actor输入和输出差均0，未复现旧输入错误。延迟差和水平/机身速度定义解释不了现有偏差；完整DR失败样本两端都有，均值接近不能当每环境达标。现阶段把原因直接称“策略回归”过早，应先固定权重核对执行和物理参数。训练配方未改，未开启第三轮。
