# H5 statistics static pre-review

**主gate/完整分母/Wilson路径通过；发现2个中断分支摘要问题，已先报父。**

## 应修的报告问题（不改候选/参数，不停止或消费H5）
1. `analyze_h5_minihop_l20_v1.py:81`无条件粗体打印`accepted/len(expected)`。
   当有软件错/未启动时也会显示x/64；JSON已置fraction/Wilson为None，但Markdown仍有完整分母错觉。
   建议仅full时输出x/64；否则写“有效物理result通过x/n，软件错m、未启动u；完整计划率不适用”。
2. 同脚本:72的`actual_controls/actual_physics_steps`只累计有效result rows。
   有软件错误时，已消耗prefix可能遗漏，字段名不可解释为全部真实耗量。
   建议改名有效物理result计数；软件prefix单列known/unknown，只有已保存数值才累加，缺失不补满配置步数。

## 其余静态核对
- :25–28核冻结case集合、唯一执行case和unstarted差集；未启动不变成机器人失败。
- :32–34把非零returncode归software并跳过，不加入robot_failed。
- :36要求结果config精确等于frozen base；flat因此与原v4:97的scene条件一致。
- :43–49使用原浮点值直接比较clearance>=.08、guide/hard==0、endstable>=2、complete；无round。
- :63/69只有无software、无unstarted、物理result数等于计划数才生成完整成功率/Wilson。
- incomplete但有效物理result按机器人未过保留，不伪装complete。
- :11–15是z=1.959963984540054的两侧Wilson score，:70明确仅声明DR范围描述，不是硬件/95%可靠度证明。
- :39–40保持nominalFalse、D0–D7键/D1enabled100Hz；:54/73单列原D0 nominal-mixture分支，不排除或当nominalTrue。
- :59–61只复制producer_streamed_once raw metadata，没有打开/重hash raw。
- v4旧kind字符串含TRAIN，但统计脚本不以kind筛选/选参，输出kind明确FROZEN_H5；无以新结果选择profile逻辑。
- 原100Hz、operational air/末恢复语义、power与270/RM/Cjump/board限制保持；机械正功率不是母线电功率。

只读本统计脚本、冻结PROTOCOL及v4原grade表达式。未运行/import统计脚本，未读任何H5结果/raw/DR收据或新holdout数据。
未跑unit/physics/Git/资产hash/41sourcehash/新agent；仅新建此review与小receipt，候选/协议/阈值未动。
