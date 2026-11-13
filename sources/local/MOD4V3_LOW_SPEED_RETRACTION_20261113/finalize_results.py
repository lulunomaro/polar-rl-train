"""Build the measured final report and an index of every large original."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil
import numpy as np
import torch

T=Path(__file__).resolve().parent;E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
baseline=json.loads((E/'BASELINE_SUMMARY.json').read_text())
native=json.loads((E/'native_nominal_r1/RESULT.json').read_text())
bank=json.loads((E/'BLOCKED_BANK.json').read_text())
suites=['blocked_bank_parent_frozen_r1','blocked_bank_teacher_frozen_r1','blocked_bank_retraction_r1',
        'blocked_bank_teacher_005m_r1','blocked_bank_parent_005m_r1',
        'blocked_bank_teacher_final_r1','blocked_bank_parent_final_r1']
recoveries={name:json.loads((E/name/'RESULT.json').read_text()) for name in suites}
training={}
for model in ('parent','teacher'):
    job=E/('train010m_'+model+'_r1')
    assert (job/'SAFE_CLOSED.json').is_file() and not (job/'ERROR.json').exists()
    final=json.loads((job/'FINAL.json').read_text())
    training[model]=dict(elapsed_seconds=final['elapsed_seconds'],iteration=final['last_progress']['iteration'],
                         done_totals=final['last_progress']['done_totals'],
                         max_closure_m=final['last_progress']['max_closure_m'],
                         final_sha256=hashlib.sha256((job/'model_final.pt').read_bytes()).hexdigest())
elapsed=sum(x['elapsed_seconds'] for x in training.values())
assert elapsed<2400.

retention={}
for name in ['whole_teacher_005m_r1','whole_teacher_final_r1','whole_parent_final_r1']:
    rows=[json.loads(x.read_text()) for x in sorted((E/name).glob('*/RESULT.json'))]
    assert len(rows)==10
    retention[name]={str(speed):dict(first=sum(x['first_landed'] for x in rows if x['speed_command']==speed),
        two_steps=sum(x['success'] for x in rows if x['speed_command']==speed),
        boundary_failures=sum(x['reason']=='tile_boundary' for x in rows if x['speed_command']==speed),requested=5)
        for speed in [.4,2.2]}

pilot=np.load(E/'pilot_teacher_r1/teacher_v0.4_s0/trajectory.npz')
i=int(np.abs(pilot['time']-6.).argmin());j=int(np.abs(pilot['time']-5.).argmin());b=int(pilot['base_body_id']);g=pilot['guide_body_ids'];w=pilot['wheel_body_ids']
f=pilot['body_contact_force'][j:i]
projection=float((pilot['chassis_max'][i,0]+2.9)/(pilot['chassis_max'][i,0]-pilot['chassis_min'][i,0]))
example=dict(time_s=float(pilot['time'][i]),root_x_relative_edge_m=float(pilot['root'][i,0]+2.9),
    com_x_relative_edge_m=float(pilot['com'][i,0]+2.9),chassis_x_span_fraction_past_edge=projection,
    mean_vertical_force_N=dict(drive_wheels=float(f[:,w,2].sum(1).mean()),guide_rollers=float(f[:,g,2].sum(1).mean()),chassis=float(f[:,b,2].mean())))
pulse=recoveries['blocked_bank_retraction_r1']['rows']
closest=max(pulse,key=lambda x:x['pair_wheel_clearance_peak_m'])
closest_path=E/'blocked_bank_retraction_r1'/('from_'+closest['blocked_source'])/closest['id']/'trajectory.npz'
with np.load(closest_path) as source:
    k=int((source['wheel'][:,:,2].min(1)-.2625).argmax())
    closest_geometry=dict(time_s=float(source['time'][k]),wheel_centers=source['wheel'][k].tolist(),
        wheel_center_x_relative_edge_m=(source['wheel'][k,:,0]+2.9).tolist(),
        paired_lower_rim_clearance_m=float(source['wheel'][k,:,2].min()-.2625),
        root=source['root'][k].tolist(),com=source['com'][k].tolist(),pitch_roll_deg=source['pose_deg'][k,:2].tolist())

notes=dict(
    observer_restore_r1='blocked_control_r1, blocked_height020_r1 and blocked_height028_r1 omitted the lagged base rotation used by the original policy. Retained as invalid paired continuations; excluded from causal conclusions. r2 restores that cache; its3s unchanged-control continuation exactly reproduces the source arrays.',
    gpu_launch_receipt='The first teacher launch template accidentally rendered a UUID prefix as1-. nvidia-smi subsequently confirmed PID3222155 on the intended physicalGPU1, with no process on the protected210 host. The template was corrected for later launches; the original receipt is retained.',
    native_scope='Two nominal replicas, not fullDR. Original native boundaries and first physical episode are retained; post-reset traces never become a valid first-episode success.',
    legacy_summary='The copied native terrain_summary still describes historical mid0.2/oblique0.5. Actual task code changes both RNG thresholds to0; actual group counters show no mid or oblique starts. Rewards/DR/BC/Adam remain the previous recipe.',
    training_exposure='Changing low-speed task distribution alone did not yield first-wheel landings during either bounded PPO run. Many episodes ended at the original4m terrain boundary; those failures are preserved. The exposure limitation is part of this result.',
    extrapolation='These finite failures do not prove mechanical impossibility. They reject height-only, the tested short retraction pulses and this low-speed-only PPO contrast as demonstrated solutions.',
    next_task_definition='Sustained chassis-supported climbing would change the current ordinary contact termination task. It was not enabled here. Brief permitted contact impulses are measured separately from sustained support.')
(E/'EXPERIMENT_NOTES.json').write_text(json.dumps(notes,indent=2)+'\n')

checkpoint_checks=[]
for path in sorted(E.glob('train010m_*/*.pt')):
    data=torch.load(path,map_location='cpu',weights_only=False)
    required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','terrain_curriculum_state','domain_randomization_state']
    missing=[x for x in required if x not in data]
    assert not missing,(str(path),missing)
    assert 'distribution.std_param' in data['actor_state_dict']
    checkpoint_checks.append(dict(path=path.relative_to(T).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        bytes=path.stat().st_size,iteration=data['iter'],optimizer_entries=len(data['optimizer_state_dict']['state']),
        full_state_verified=True,STD=data['actor_state_dict']['distribution.std_param'].tolist(),action_order=data['action_order']))
(E/'FULL_CHECKPOINTS.json').write_text(json.dumps(checkpoint_checks,indent=2)+'\n')

artifact_index=[]
for path in sorted(T.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.suffix not in ('.npz','.msh','.pt','.usd','.usda','.stl','.obj'):
        continue
    artifact_index.append(dict(path=path.relative_to(T).as_posix(),absolute_source=str(path),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),git_storage='ordinary full PT blob' if path.suffix=='.pt' else 'original retained; SHA/path index'))
(E/'ARTIFACT_INDEX.json').write_text(json.dumps(artifact_index,indent=2)+'\n')
summary=dict(result='No verified post-block first-step or two-step recovery in the tested cases',
    baseline=baseline['summary'],actual_contact_speed_bins=baseline['by_actual_contact_speed'],
    blocked_state_count=len(bank),recoveries={k:{x:v[x] for x in ['requested','first_landed','two_steps']} for k,v in recoveries.items()},
    closest_pulse_state=closest_geometry,blocked_geometry_example=example,training=training,
    total_PPO_seconds=elapsed,maximum_authorized_PPO_seconds=2400,automatic_extension=False,
    retention=retention,models_promoted=False,default_model='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283',
    full_checkpoints=checkpoint_checks,notes=notes)
(T/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')

lines=['# 低速卡阶后收腿实验结果','',
'本轮尚未实现“已卡住后收腿、越沿落轮承重、再上第二阶”。现有策略、直接收腿脉冲和本次低速PPO对照均没有通过独立受阻续播验收。',
'','## 机身看起来在台面上，实际由谁支撑','',
f'教师0.4m/s指令的代表性受阻帧在仿真6.000秒：机身碰撞几何的前后向投影约{projection*100:.1f}%已越过边缘，root越过{example["root_x_relative_edge_m"]*1000:.1f}mm，全机器人质心仍在边缘后{abs(example["com_x_relative_edge_m"])*1000:.1f}mm。这个比例是x向投影跨度，不能解释为质量或支撑比例。',
f'前1秒平均向上接触力：驱动轮{example["mean_vertical_force_N"]["drive_wheels"]:.1f}N、导轮{example["mean_vertical_force_N"]["guide_rollers"]:.1f}N、机身{example["mean_vertical_force_N"]["chassis"]:.1f}N。机身几何越沿没有意味着机身已承重。',
'','## 冻结MuJoCo对照','',
'两级各200mm，踏面和顶台沿用原level3；每档5初态，准备升高后3秒开始前进。表内为第一阶落轮数/连续两阶完成数。',
'','| 速度指令m/s | 综合父db6 | 教师715c |','|---|---:|---:|']
for speed in [.2,.4,.6,.8,1.,1.8,2.2]:
    rr=[next(x for x in baseline['summary'] if x['model']==model and x['command']==speed) for model in ('parent','teacher')]
    lines.append(f'| {speed:.1f} | {rr[0]["first"]}/5 / {rr[0]["two_steps"]}/5 | {rr[1]["first"]}/5 / {rr[1]["two_steps"]}/5 |')
lines+=['','按驱动轮首次立面接触的实际速度分组：','',
'| 实际触阶速度m/s | 综合父完成两阶 | 教师完成两阶 |','|---|---:|---:|']
for bounds in [(-10,.5),(.5,1.),(1.,1.5),(1.5,2.),(2.,10.)]:
    rr=[next(x for x in baseline['by_actual_contact_speed'] if x['model']==model and x['contact_actual_vx_interval']==list(bounds)) for model in ('parent','teacher')]
    label=f'<=0.5' if bounds[0]==-10 else ('>2.0' if bounds[1]==10 else f'({bounds[0]:.1f},{bounds[1]:.1f}]')
    values=[f'{x["two_steps"]}/{x["requested"]}' if x['requested'] else '无样本' for x in rr]
    lines.append(f'| {label} | {values[0]} | {values[1]} |')
lines+=['','实际触阶速度<=1m/s的样本均未完成第一阶；1.0m/s指令下的部分通过不能称为低速卡住后恢复。成功参考的平均阶间耗时：父2.2档1.253秒，教师2.2档1.046秒。',
'','## 已卡住状态的独立对照','',
'从真实接近轨迹保存17个受阻状态：持续1秒双轮各自净进展绝对值<10mm、平均实际vx绝对值<0.10m/s、近期驱动轮有>5N立面接触，双轮仍在边缘外侧且未达到目标轮心高度。阈值根据先导轨迹制定，仅用于标记受阻事件，没有改变物理或成功判定。',
'','| 同一受阻状态后的策略/动作 | 第一阶 | 连续两阶 |','|---|---:|---:|']
labels=['原综合父','原教师','原教师+收腿脉冲','教师低速PPO005m','综合父低速PPO005m','教师低速PPO终点','综合父低速PPO终点']
for label,name in zip(labels,suites):
    value=recoveries[name];lines.append(f'| {label} | {value["first_landed"]}/{value["requested"]} | {value["two_steps"]}/{value["requested"]} |')
lines += ['',
'直接降低高度会收腿，但也会降低机身；测试的对称收腿脉冲和有限髋角偏置没有形成越沿落轮。代表性6秒触发案例双轮下缘最高约0.181m，距上沿约18mm。',
f'整批脉冲中最接近的一例为{closest["blocked_source"]}，瞬间双轮下缘净空{closest_geometry["paired_lower_rim_clearance_m"]*1000:+.3f}mm；当时两轮中心距边缘仍为{closest_geometry["wheel_center_x_relative_edge_m"]}m，未落轮承重。这个瞬间很小的竖向余量不代表已经跨过边缘。',
'短暂机身/导轮冲击力保留在原始轨迹中。持续机身承载超过原接触驻留条件会触发终止；本轮没有开放机身托住后拖轮上台的新任务。',
'','## 双卡PPO和原生对照','',
'主机72为amax，双RTX4090；工作目录为`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_LOW_SPEED_RETRACTION_20261113_R1`。只改变原专项的训练任务分布：全程正向接近、无第一阶中途起步、前进指令0.2~0.6m/s。原奖励、完整DR、示范数据/BC、PPO参数、电机包络和保护保留。',
f'父模型实际PPO窗口{training["parent"]["elapsed_seconds"]:.3f}秒，教师{training["teacher"]["elapsed_seconds"]:.3f}秒，含完整迭代与保存结算合计{elapsed:.3f}秒（{elapsed/60:.3f}分钟）；原合计目标1200秒，未超过用户40分钟合计上限。两者均自然保存关闭；每5分钟完整PT、first/final均已取回核验。',
'原生PhysX名义冻结对照共280环境（两模型、两侧、7速度、5初态、2个名义副本）：0.2~0.8m/s指令下每模型80例均未落轮第一阶。原生和MuJoCo结果分开保存；本轮没有斜向或新增fullDR验收，因为正向受阻恢复尚未成立。',
'训练中的两组均未产生第一阶落轮；边界重置和20秒超时按原条件保留。大量边界重置限制了有效台阶样本，结果不能解释为充分训练后机构绝对无法完成。',
'教师高速2.2参考：原5/5、005m为1/5、终点恢复5/5；父高速参考原4/5、终点1/5。父终点有4/5在正式接近前后退越界，不能把这些归成已经卡住后的失败。两模型终点的0.4档均0/5。',
'','## 结论与边界','',
'收腿确实能显著抬起受阻轮子，但目前没有把抬轮、前向越边、支撑转移、落轮承重和第二阶串起来。单纯降低高度、固定收腿脉冲，以及只改低速训练任务分布，都没有成为有效的最小改动。',
'本轮没有证明机构物理上不可能，也没有验证出可交付的最小控制修改。下一项有针对性的方向是基于真实受阻状态训练支撑转移与收腿/前摆/落轮时序；若转为持续机身承载，需先明确任务定义和接触终止规则变化。没有自动续训或扩大预算。',
'默认综合模型仍为db6，冻结715c教师及原用户窗口保留；210上的两小时训练未被修改、停止或占用GPU。',
'','## 原件与记录','',
'`RESULTS.json`提供结构化摘要；`evidence/BASELINE_SUMMARY.json`含逐案实际速度、阶间时间和失败；`BLOCKED_PROTOCOL.json`、`BLOCKED_BANK.json`含受阻协议与原始状态索引。所有400Hz轨迹、接触力、力矩、质心、轮位、腿长与失败原件保存在本独立版本的`evidence/`，大文件路径/大小/SHA见`ARTIFACT_INDEX.json`。',
'`FULL_CHECKPOINTS.json`核对actor/critic/STD、Adam、RNG、DR和课程状态；完整新PT本体作为普通Git二进制归档，不仅保存路径。初次续播漏姿态缓存的无效对照、启动UUID模板问题和后续修复均在`EXPERIMENT_NOTES.json`保留，未混入有效结论。',
'归档标签：`trial-20261113-low-speed-blocked-retraction-01`。实际commit和远端main/tag/peeled核验以归档工具回执为准。登录凭据不进入实验包或Git。','']
report='\n'.join(lines)
(T/'FINAL_REPORT.md').write_text(report,encoding='utf8')
(T/'README.md').write_text('# Low-speed blocked-wheel retraction experiment\n\nCompleted. The requested post-block first-step/two-step recovery was not achieved.\n\nSee FINAL_REPORT.md and RESULTS.json for all frozen, pulse, native and bounded PPO contrasts.\nFull new PT files are retained in evidence/train010m_parent_r1 and evidence/train010m_teacher_r1.\nTwo jobs used %.3f PPO seconds in total; no extension and no model promotion.\nOriginal210 training and viewer were preserved.\n' % elapsed)
for filename in ['FINAL_REPORT.md','RESULTS.json']:
    shutil.copy2(T/filename,out/filename)
media=T/'media';media.mkdir(exist_ok=True)
for filename in ['blocked_retraction_curves.png','blocked_retraction_keyframes.png','rendered_robot_states.png']:
    if (out/filename).exists():shutil.copy2(out/filename,media/filename)
weights=out/'complete_training_checkpoints';weights.mkdir(exist_ok=True)
for path in sorted(E.glob('train010m_*/*.pt')):
    name=path.parent.name.removeprefix('train010m_')+'_'+path.name
    shutil.copy2(path,weights/name)
print(json.dumps(dict(completed=True,total_PPO_seconds=elapsed,new_full_PT_files=len(checkpoint_checks),report=str(out/'FINAL_REPORT.md'),closest=closest_geometry),indent=2))
