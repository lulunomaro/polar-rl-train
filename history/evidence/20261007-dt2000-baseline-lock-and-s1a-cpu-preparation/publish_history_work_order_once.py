"""Publish the next approved interface work, without claiming a GPU executor exists."""
from pathlib import Path
import json,time,hashlib,sys
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;E=W/'MOD4_MOE_PLAN_EXECUTION_20261007/reports';repo=W/'polar-rl-train'
out=R/'S1A_HISTORY_COMPONENT_WORK_ORDER.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
cpu=read(R/'HISTORY_COMPONENT_CPU_PASSED.json');lock=read(R/'DT2000_BASELINE_LOCKED.json')
assert cpu['passed'] and cpu['tests']==22 and not cpu['CUDA_initialized']
v=dict(epoch=time.time(),plan_version='1.5',stage='S1A',status='CPU_COMPONENT_PREPARED_SDK_AND_CONTROLLER_PENDING',
 baseline_id=lock['id'],baseline_sha256=hashlib.sha256((repo/'history/plans/MOD4_DT2000_TRAINING_BASELINE.json').read_bytes()).hexdigest(),
 component_root=cpu['component_root'],source_checkpoint_sha256=cpu['source_checkpoint_sha256'],CPU_evidence=cpu,
 current_A0_not_interrupted=True,encoder_GPU_deployed=False,A1_A2_PPO_started=False,
 next_required=['Clone actual184-source dt2000 root into a new isolated architecture candidate, preserving frozen old files.',
 'Apply only approved history/encoder/optimizer interface changes; integrate the baseline assertion at the new authority boundary.',
 'Read real deployable35 feedback history/current tick, selected episode resets, last actual action, body-velocity frame/point/scaling and clean38 critic in native SDK.',
 'A1: independent actual Body velocity supervision and actor latent detach; A2: joint PPO gradients. Do not use arbitrary critic first-three slots.',
 'Preserve source actor/std/critic and zero new latent columns; allocate explicit new architecture optimizers. Save encoder, actor, critic, both optimizers, RNG and history configuration.',
 'Run meaningful native interface/reset/parameter/contact and complete128/20k PPO checks for the new architecture; discard preflight weights and charge the single canonical ledger.',
 'After current A0 actual complete-save/physical-health/exit/settled-active and both canonical locks, choose one new explicit authority for matched A1/A2 training from original23509.',
 'Compute matched update counts from complete actual control steps /24 and log iteration count; stored iteration index alone is not an update ledger.',
 'New2ms immutable3060 runtime/asset/clock package needs own SDK/function calibration; old.5ms results remain separate, without blocking4090 validated-scope learning.'],
 forbidden=['Do not execute CPU preparation files as an Isaac/PPO entry.','Do not repeat old one-shots, benchmark clocks again, hot-edit the current trainer or choose highest directory iteration.','Do not claim CPU output equivalence is real SDK labels, trained state estimation or deployed MoE.'],
 total_S1A_learning_limit_seconds=21600,record_prior_partial_A0_and_rejected_clock_learning_costs=True,new_budget_seconds=0,canonical_write_operations=0)
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
contract=repo/'history/plans/MOD4_MOE_EXECUTION_CONTRACT.json';cc=read(contract)
cc['S1A_history_component_actual']=dict(status=v['status'],root=v['component_root'],tests=22,actual_source_CPU_migration_output_max_abs_difference=cpu['full128_fixture_actor_output_max_abs_difference'],SDK_verified=False,architecture_PPO_started=False,baseline_id=lock['id'])
contract.write_text(json.dumps(cc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks=read(E/'EXECUTION_TRACKS.json');tracks['architecture_preparation']=cc['S1A_history_component_actual'];(E/'EXECUTION_TRACKS.json').write_text(json.dumps(tracks,indent=2),encoding='utf8')
handoff=E/'LATEST_HANDOFF.md'
note='''

# 最新人类参数固化：2ms基线与S1A接口准备

人类明确“2ms健康就暂时固化训练参数，按照这个参数推进我们的计划训练”。当前已锁MOD4-DT2000-BASELINE-LOCK-001；见MOD4_DT2000_TRAINING_BASELINE.json/md和当前root/reports/DT2000_BASELINE_LOCKED.json。主计划v1.5原SHA保持，新增补充按直接人类消息登记；当前184source/PPO/runtime不热改、预算操作0。固定2ms×5/100Hz、5ms积分3history、solver16/4、20k×24/LR1e-4adaptive/save25，其余现有PPO与硬件保持。不再重复步长扫参；新架构或计划内DR/任务在原批准范围独立验证后推进。

A0当前自己的完整保存/source freeze/manifest有限已核查；周期checkpoint尚未回放，不宣布技能成熟。当前45min完成后按真实FORMAL_CLOCK_HEALTH_REVIEW和完整保存/原父计划退出/active结清边界推进，不能复活旧entry。A1/A2源为原23509，不挑当前最高iter或预检权重；匹配实际更新量，S1A6h上限与所有已有费用保留。

隔离CPU组件根/home/egde/rl_candidates/MOD4_S1A_HISTORY_COMPONENT_20261007已完成22项目标Torch2.10 CPU合同，无CUDA初始化/GPU/PPO/账本权限。5×35历史40ms跨度、同tick缓存、选中episode行reset、独立初始化RNG、A1 detach/独立速度监督梯度和A2联合梯度、实际source35→38第一层新增列0/std及其余weights exact/128fixture动作差0均通过。这里只是CPU数学/真实来源权重准备，不是Isaac SDK或训练执行器；teacher真实frame/point/scale、clean critic、真实缓存reset/命令/参数/接触、完整新checkpoint/optim/RNG与必要PPO尚待补齐。S1A_HISTORY_COMPONENT_WORK_ORDER明确下一实际工作，不无限停在队列。

3060旧.5ms六份功能校准已完成并限定scope接受：23509world64/64、23621world60/64，两主机一致；平台净cross最大逐env差.00912236m/s，旧raw/flags保持。新2ms评测包还需实际源码/资产/时钟/跨bin校准，不能拿旧包当新clock proof，也不阻塞4090自身验证学习。下一巡检自主完成新接口/新clock评测所需真实证据及安全接管，已授权合理步骤无需重复确认。
'''
handoff.write_text(handoff.read_text(encoding='utf8')+note,encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  er='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  for p in (out,R/'HISTORY_COMPONENT_CPU_PASSED.json',contract,E/'EXECUTION_TRACKS.json',handoff):
   s.put(str(p),er+p.name+'.history_prep');s.posix_rename(er+p.name+'.history_prep',er+p.name)
  s.put(str(out),v['component_root']+'/reports/'+out.name)
  s.put(str(handoff),lock['runtime_root']+'/reports/LATEST_HANDOFF.md')
finally:c.close()
print(json.dumps({'stage':v['stage'],'status':v['status'],'current_learning_not_interrupted':True,'new_GPU_PPO_budget_operations':0}))
