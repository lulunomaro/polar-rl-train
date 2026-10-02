# TASK_LIST - MOD4 滚动导轮修复包

## 已完成 (2026-09-13)
- [x] 交付 USD 前后哈希校验（`1d437847…` 未变）
- [x] 8 导轮独立刚体 + 被动转动关节的新 USD（`7b4d8535…`）
- [x] 从新 USD 重算 import_contract（31 bodies / 30 树关节 / 6 closures / 34 碰撞体 / 277 视觉 / 6 执行关节）
- [x] 离线闭链一致性复核：6/6 closure 残差 0.00000 m
- [x] `guide_contact` 正则覆盖 8 个刚体
- [x] 腿位置环刚度/积分旋钮（`RM_LEG_KP/KD/KI`）
- [x] 低姿态 KP 扫描 60→2500：包络 273.7→246.0 mm
- [x] 穿越探针：0.12 / 0.18 m/s 通过，顶板 0 接触，主轮 ~35 N
- [x] v3 训练链启动（64 环境 6000 步 smoke → tunnel → terrain → spin → fly → jump）

## 进行中
- [ ] smoke 判读：闭链 <2 mm、mimic <0.01 rad、无 NaN/OOM（当前 session max closure 0.4 mm / mimic 1.7 mrad）
- [ ] tunnel 阶段训练（tunnel_cross 41% 采样）
- [ ] 0.25 m/s 穿越行
- [ ] `RM_LEG_KI` 积分通路复核（现 KI=0，用 KP 等效）

## 待办
- [ ] 逐阶段版本门禁 + 逐路线评测（check_run_version.sh / read_phase_eval.py）
- [ ] tunnel gate：complete_rate ≥0.60、underpass_seen ≥0.80、roof_hit≈0（交付 2.30 m 终点）
- [ ] terrain 五路线各 ≥0.60（ramp_up / step_up / rough_cross 已加权）
- [ ] spin ≥0.60 且 spin_deg ≥360°；fly / jump 统计离地、腾空、落地、失败原因
- [ ] 统一策略：平衡路线采样 + rehearsal；禁止平均合并检查点
- [ ] 名义全绿后再开 DR（质量/质心/摩擦/执行器/编码器/延迟/电池电压/地形摩擦）并报最差样本
- [ ] 1024 环境吞吐与稳定性
- [ ] 交付：checkpoint 链、manifest/SHA256、名义 + 多种子 DR 评测 JSON、逐路线完成率与终止原因、
      最小洞净空、closure/mimic 最大误差、TensorBoard、结论
- [ ] 独立 ZIP + ZIP SHA256

## 硬约束
- 训练运行期间不修改 Python/USD/JSON/奖励配置（v3 链每阶段核冻结哈希，不一致 exit 4）
- 一次只跑一个训练任务；旧 checkpoint 只能作跨版本迁移基线