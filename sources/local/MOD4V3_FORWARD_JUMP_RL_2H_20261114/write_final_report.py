"""Write the final human-readable result from frozen independent evidence."""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import shutil
import torch

T=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--outputs',required=True)
args=parser.parse_args()
output=Path(args.outputs)
summary=json.loads((T/'evidence/RESULTS_SUMMARY.json').read_bytes())
assert not summary['pending']
best=summary['selected']
budget=summary['budget']
result=json.loads((T/'evidence'/best['job']/'RESULT.json').read_bytes())
passed=[row for row in result['episodes'] if row['success'] and not row['terminated']]
stats={}
for key,scale in (('air_s',1.),('rim_peak',100.),('air_pitch',180/3.141592653589793),('air_roll',180/3.141592653589793)):
    values=[row[key]*scale for row in passed]
    stats[key]=dict(min=min(values) if values else None,max=max(values) if values else None,
        mean=sum(values)/len(values) if values else None)
model=output/'selected_forward_jump_full_ppo.pt'
state=torch.load(model,map_location='cpu',weights_only=False)
assert hashlib.sha256(model.read_bytes()).hexdigest()==best['sha256']
assert len(state['optimizer_state_dict']['state'])==17
tz=timezone(timedelta(hours=8))
start=datetime.fromtimestamp(budget['original_start_epoch'],tz).strftime('%Y-%m-%d %H:%M:%S')
deadline=datetime.fromtimestamp(budget['deadline_epoch'],tz).strftime('%Y-%m-%d %H:%M:%S')
parent='03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd'
outcome=('仅部分 fullDR 样本完整通过，标称完整动作尚未通过' if best['nominal_success_survived']==0 and best['total_success'] else
         ('已有标称完整通过样本，仍需按实际通过率判断稳定性' if best['nominal_success_survived'] else '尚未通过完整跳跃验收'))
lines=[
'# 前进中跳跃：两小时训练窗结果','',
f'结果：**{outcome}**。选中 `{best["checkpoint"]}`，第 {best["iteration"]} 次迭代。',
f'完整检查点 SHA256：`{best["sha256"]}`。','',
'## 固定评测','',
f'选中模型的输入版本为 {best["revision"]}，随机种子 10066，确定性学习策略独立运行。评测未创建优化器，也未执行示范控制器。R3 使用阶段指令和进度，R4 另加下降时的落地准备标志；各版本原始结果分别保留，物理验收判据相同。',
'完整通过要求：前进压腿、实际蹬伸、真正腾空、空中实际收腿、腾空时俯仰不超过 10 度/横滚不超过 5 度、轮缘离地峰值至少 12 cm、腾空至少 0.16 s，并在落地后稳定前进至少 0.5 s。若随后在本回合发生终止，单独列为晚期失败，不计通过。','',
'收腿深度的既定判据是两侧主动腿关节差的平均值小于 0.9 rad；蹬伸需先大于 1.25 rad。原始通过、未通过和完成后又失败的记录均保留。','',
'| 指标 | 标称参数（51 回合） | fullDR（205 回合） |',
'|---|---:|---:|',
f'| 压腿 | {best["nominal_crouched"]} | {best["fullDR_crouched"]} |',
f'| 蹬伸 | {best["nominal_extended"]} | {best["fullDR_extended"]} |',
f'| 真正起跳 | {best["nominal_takeoff"]} | {best["fullDR_takeoff"]} |',
f'| 空中收腿 | {best["nominal_retracted"]} | {best["fullDR_retracted"]} |',
f'| 腾空姿态限值通过 | {best["nominal_air_balance_passed"]} | {best["fullDR_air_balance_passed"]} |',
f'| 落地 | {best["nominal_landed"]} | {best["fullDR_landed"]} |',
f'| 完整通过并存活到回合结束 | **{best["nominal_success_survived"]}/51** | **{best["fullDR_success_survived"]}/205** |',
f'| 完成后又终止 | {best["nominal_late_failure_after_success"]} | {best["fullDR_late_failure_after_success"]} |','',
f'合计 {best["total_success"]}/256。选模先比较完整通过数，再比较标称通过数、实际收腿数、起跳数；奖励高低不用于代替验收。所有原始 completed 事件与失败回合保留。','',
'## 训练与预算','',
f'北京时间 {start} 开始，原定截止 {deadline}。实际训练窗 {budget["actual_window_seconds"]:.3f} s，最后一次迭代完成及保存的尾差如实计入。',
f'四个连续 owner 阶段合计 {budget["total_owner_phase_elapsed_seconds"]:.3f} s（{budget["total_owner_phase_elapsed_seconds"]/60:.2f} 分钟）；准备、准入与切换在该两小时窗内占 {budget["preparation_and_admission_inside_window_seconds"]:.3f} s。没有另加两小时，也没有独立 BC 预训练优化器。R4 从本次已验收最好的 80 分钟完整状态接续；R3 之后的更新和权重全部保留并计入实际预算。',
f'实际 PPO 更新 {budget["total_PPO_updates"]} 次，采集 {budget["environment_steps"]:,} 个环境步。GPU0 同时最多一个优化器，GPU1 仅采集示范和冻结评测。',
'actor、critic、STD、Adam 实际更新的首次证据均已保存。完整 PT 包含 actor/critic/STD/Adam/RNG、DR 状态、任务与训练合同；每五分钟保存完整检查点。','',
'## 父模型与方法','',
f'按用户最终明确选择，根父模型为仓库五分钟检查点，第 26163 次迭代，SHA256 `{parent}`。后续阶段只从本次试验的完整保存状态接续，未换用其它父模型。',
'训练方法是原生 PPO 加训练专用动作示范损失。36 条原生完整成功示范共 10800 帧；示范种子 20066 与固定评测种子 10066 分开。指导损失按五阶段均衡采样，在同一次 PPO 反向传播中计算；训练与验收时，实际关节动作均由学习策略输出。',
'策略接收阶段指令和阶段进度，R4 还接收由世界系竖直速度得到的下降/落地准备状态；并非已经学会从单一不变输入自主安排整套时序。actor35/critic78/action6 维度保持；控制模式槽的含义已经版本化，现有部署输入生产端尚未接入此科目。','',
'## 物理与保留范围','',
'使用已批准 MOD4v3 HW300N60 R3 资产并核验哈希。2.5 ms 物理、100 Hz 腿、400 Hz 轮、50 Hz 策略、TGS32/4、原电机包络和动作顺序保持。闭链 10 mm、mimic 0.01 rad 按单环境重置；原接触、倾角和非有限保护保留。没有机身姿态锁定、人工起跳力或跳跃动作覆盖。',
'fullDR 参数范围及固定 80% fullDR/20% 标称混合保留；本次起始分布改为直立可行姿态、小偏航、零初速度。实验在平地进行，未完成此跳跃策略的楼梯、粗地保持或实机部署验收；不替换综合生产父模型。','',
'## 工作区与证据','',
f'本地版本：`{T}`。',
'72 主机独立目录：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_RL_2H_20261114_R1`。Host210 和既有观看器未修改。',
'R1 输入阶段混叠与长期未起跳、R2 稀少腾空收腿、JSON 序列化失败、观察队列误识别日志、示范启动前语法错误及早读 not-ready 均已保留原始证据和修复记录。',
'完整逐回合结果、失败样本、原生轨迹索引、所有检查点、训练日志与 Git 试验记录均位于上述版本目录。',
'交付目录包含完整检查点、逐点评测表、结果 JSON、学习曲线和实际策略姿态录像。录像由原生记录状态渲染，未进行第二次物理积分。','']
report='\n'.join(lines)
(T/'FINAL_REPORT.md').write_text(report,encoding='utf8')
(output/'FINAL_REPORT.md').write_text(report,encoding='utf8')
contract=dict(checkpoint_sha256=best['sha256'],revision=best['revision'],actor_observations=35,critic_observations=78,
    action_dimensions=6,action_order=state['action_order'],task=state['plan']['jump'],
    assets=state['plan']['asset_identity'],root_parent_sha256=parent,
    execution='Learned actor actions; matching phase-input producer required; no deployment promotion')
(T/'evidence/SELECTED_TASK_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
(output/'selected_task_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
details=dict(pass_sample_statistics=stats,checkpoint=dict(format=state['format'],iteration=state['iter'],
    sha256=best['sha256'],bytes=model.stat().st_size,Adam_entries=len(state['optimizer_state_dict']['state']),
    actor_keys=list(state['actor_state_dict']),critic_keys=list(state['critic_state_dict'])),budget=budget,
    source_reports=[str(T/'evidence'/best['job']/'RESULT.json')])
(T/'evidence/FINAL_DETAILS.json').write_text(json.dumps(details,indent=2)+'\n')
print(json.dumps(dict(outcome=outcome,selected=best,budget=budget,pass_statistics=stats),indent=2))
