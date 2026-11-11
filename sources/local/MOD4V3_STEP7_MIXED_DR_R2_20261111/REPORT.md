# 第二轮实际运行记录

第一轮完整DR前进最佳10m为4/10、6/10；同源PhysX nominal前进0/20。选10m完整PPO恢复，本轮唯一修改为20%名义参数+80%原fullDR固定env样本，不改奖励/solver/DR端点；这是假设检验，未把混合视为已解决。先做64env固定父短探针确认分组写回，复用第一轮完整范围4096env与40min numerical0证据；后续在实际首update/检查点核4096采样与训练。


64env探针r1在rollout前因未选中collider仍被旧reset随机而失败；r2修复全shape名义恢复后完成320步，numerical0、20次闭链单envreset。独立probe本身仍用旧25%external/noise默认，不把它写成fullrange探针；主launcher四项fraction全1。主训练2026-11-11 10:24:13启动，PID1007162，完整恢复iter22265。实际STARTUP819nominal/3277fullDR，首update22266、完整11,048,951bytes检查点并核SHA，actorchanged、numerical0，2mm单envreset保留。
