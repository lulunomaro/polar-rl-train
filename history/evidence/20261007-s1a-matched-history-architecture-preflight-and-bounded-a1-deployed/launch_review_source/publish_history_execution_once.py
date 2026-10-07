"""Publish actual healthy clock and real history scope; retain approved master SHA and all failures."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;PL=W/'polar-rl-train/history/plans'
E=W/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'
assert not (R/'HISTORY_EXECUTION_PUBLISHED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
clock=read(R/'CLOCK1000_COMPLETE_AND_SOURCE_APIS.json')
sdk=read(R/'MOD4_S1A_HISTORY_LABEL_LIFECYCLE_20261007_HISTORY_SDK_PASSED.json')
cpu=read(R/'ARCHITECTURE_LABEL_REVIEW.json');launch=read(R/'S1A_LAUNCH_REVIEW_LAUNCHED.json')
actual=read(R/'S1A_HISTORY_CURRENT_ACTUAL.json')
assert clock['formal_health']['adoption_retained'] and sdk['canonical_bytes_exact'] and cpu['passed']
assert actual['owner'] and actual['owner']['start_ticks']==launch['owner']['start_ticks'] and not actual['receipts'].get('S1A_HISTORY_ATTENTION.json')
master=PL/'MOD4_MOE_MASTER_PLAN.md';MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert hashlib.sha256(master.read_bytes()).hexdigest()==MASTER
baseline=dict(id='MOD4-DT1000-WORKING-BASELINE-001',status='HEALTHY_LONGRUN_APPROVED_FALLBACK',
 approved_plan='MOD4-MOE-PLAN-001',version='1.5',master_sha256=MASTER,
 authority='Existing approved v1.5 fallback after conditional2ms health lock actually failed; no new human approval inferred',
 physics_dt_s=.001,decimation=10,policy_period_s=.01,contact_bin_s=.005,contact_history_bins=3,solver=[16,4],
 original_source=clock['ready']['checkpoint'] if False else clock['ready']['checkpoint'],
 actual_A0_checkpoint=clock['full_save'],actual_health=clock['formal_health']['actual_health'],
 actual_updates=275,actual_control_steps=6600,actual_environment_policy_steps=132000000,
 unique_completed_segment=clock['actual_segment'],actual_learning_seconds=clock['ready']['actual_learning_seconds'],
 source_runtime_count=189,preflight_source23509_retention_passed=True,trained23783_behavior_replay_pending=True,
 original_dt2000_lock_suspended_not_rewritten=True,all_previous_rejections_preserved=True,
 runtime_nominal_model_reward_DR_hardware_unchanged=True,new_budget_seconds=0,
 historical_native_steps_per_second=58138.84094988423,not_200000_steps_per_second=True)
baseline['initial_source']=dict(path='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt',sha256='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a')
baseline.pop('original_source')
bp=PL/'MOD4_DT1000_WORKING_BASELINE.json';bp.write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
md='''# MOD4 1ms工作基线：实际长段健康后的批准内接续

主计划v1.5与原SHA保持。原2ms固化以健康为条件，真实closure超过2mm后已经暂停；原文件和失败权重全部保留。按已批准回退条款采用1ms×10、100Hz控制、5ms冲量bin/三历史、solver16/4。停止扫步长，依此真实健康范围继续S1A。

原23509完整初始化的A0实际完成275更新、6600控制步、132000000环境策略步，加载/学习/保存/退出2726.870833873749秒已唯一结账。完整23783 SHA9eb36866f29fd223b2c41ebf4829a9847ef8842a9f6e7dc6105e93656fdfe3c8，CPU68浮点有限。真实任务失败0、最大closure0.70377189mm、mimic0.001953125rad、66000物理回调精确。原父/guardian/trainer计划退出、active为空。新23783尚未技能回放，不能借23509准入宣布新策略能力成熟。

本机真实SDK已验证5×35历史40ms、同tick缓存、三次选中reset与其他行保持、原35policy/38critic反馈逐值保持、初始扩维actor动作差0。速度标签是根部COM速度以根部机体坐标表达，原critic位置7:10且scale0.5；原生Warp四元数为xyzw。reset当帧SDK派生Body速度缓存不作监督目标，明确validity mask排除，后续物理帧恢复有效；不改变原critic、plant或reset。有效标签独立坐标误差1.1920928955078125e-7m/s。接口失败与reader错误/raw保留，不改写为生产物理失败。

A1只由当前反馈35和五帧175推理，encoder175→128→64→3、actor新增3列初值0，速度标签仅供辅助训练，latent对PPO detach；A2同接口仅联合PPO、无辅助速度优化器。目标Torch2.10实际RSL20项CPU合同及独立command/DR RNG保存合同通过，包括合成完整PPO更新、优化器分工、RNG/history/actor/critic/encoder/std回读、JIT输出与特权actor拒绝。合成CPUfixture不是机器人学习，未扣PPO。

新213源码独立执行器先128×2/20k×4完整新架构PPO，预检权重丢弃；再各从同23509、seed20260928、white_v3、当前1ms按实际275更新有界匹配。首块最多45min，不足匹配量仅从自己的完整保存接续，包含同S1A6h与唯一230h账本；不得用预检策略、目录最大iter或失败23875作源。A0原optimizer恢复，新增架构明确新optimizer，此差异披露，不称纯架构因果隔离。训练准入或总reward不选赢家，实际同钟技能保持/DR、更新量、wall和部署成本仍须比较。当前没有MoE gate训练。

模型/真实任务/nonfinite/closure2mm/mimic.01/参数和完整接触数据及原硬件限幅不放松，有限质量仍诊断；新时钟3060包需独立校准，旧0.5ms功能证据不代新时钟，也不阻塞4090已验证范围。没有新增时间或重复结账。
'''
(PL/'MOD4_DT1000_WORKING_BASELINE.md').write_text(md,encoding='utf8')
contract=read(PL/'MOD4_MOE_EXECUTION_CONTRACT.json')
contract['current_working_training_baseline']=dict(document='history/plans/MOD4_DT1000_WORKING_BASELINE.json',sha256=hashlib.sha256(bp.read_bytes()).hexdigest(),status=baseline['status'],physics_dt_s=.001)
contract['execution_state']=dict(stage='S1A',status='ACTUAL_HISTORY_SDK_PASSED_MATCHED_ARCHITECTURE_PPO_IN_PROGRESS',runtime_root=launch['root'],source_count=213,actual_A0=clock['full_save'],A1_A2_behavior_winner_pending=True)
contract['architecture']['history_candidate'].update(actual_SDK_verified=True,CPU20_checkpoint_contract_verified=True,reset_teacher_validity_required=True,actual_architecture_training_root=launch['root'],selected_for_all_experts=False)
(PL/'MOD4_MOE_EXECUTION_CONTRACT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks=read(E/'EXECUTION_TRACKS.json')
tracks['physics_performance']=dict(status='HEALTHY_1MS_LONGRUN_WORKING_BASELINE',actual_A0=clock['full_save'],actual_health=baseline['actual_health'],physics_dt_s=.001,decimation=10,failed2ms_lock_retained=True)
tracks['learning']=dict(status='S1A actual new architecture preflight/learning follows own receipts',root=launch['root'],actual_phase=actual['receipts']['S1A_HISTORY_STATE.json']['phase'],parent=actual['owner'],guardian=actual['guardian'],child=actual['child'],architecture_compare_updates=275,source_count=213)
tracks['history_interface']=dict(native_SDK=sdk,CPU20=cpu,teacher_validity_mask=True,actual_encoder_training_effect_pending=True)
(E/'EXECUTION_TRACKS.json').write_text(json.dumps(tracks,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
approval=read(E/'PLAN_APPROVAL.json')
approval.setdefault('execution_events',{})['MOD4-DT1000-WORKING-BASELINE-001']=dict(status=baseline['status'],source='Actual healthy fallback under approved v1.5; original2ms lock remains suspended',baseline_document=bp.name,new_human_approval_inferred=False)
(E/'PLAN_APPROVAL.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
handoff='''# Actual1ms healthy A0 and S1A native history readback, matched architecture authority

Approved master v1.5/SHA unchanged.2ms lock remains suspended after actual closure failure; no new timestep sweep.1ms A0 own23783 complete/CPU68 finite,275updates/6600control/132Mpolicyenvsteps,task0,closure.703772mm,66000callbacks;2726.870833873749s uniquely settled. Trained23783 skill behavior still pending; source23509 three frozen checks must not be attributed to new policy.

History native202 root MOD4_S1A_HISTORY_LABEL_LIFECYCLE_20261007 finished accepted.5x35/40ms,300ticks/3000callbacks,3selected resets, other rows/current35/critic38/lastactualaction/cache exact; initial expanded actor action diff0; actual COM Body velocity valid-frame oracle1.19209e-7m/s. Reset-frame derived velocity cache explicitly invalid for auxiliary targets; actor/gate never receives label. Old API/tick/frame reader failures, rejected raw and CPU fixture RNG-order error retained.

Current training authority /home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007 has213sources. Only supervise_matched_history_launch_review_once.py executed; current actual own owner/guardian/child/active take precedence over cached state. Original212 preserved exactly, actual runtime() launch API fixed before any GPU/segment. Both CPU20 architecture and independentRNG passed. Necessary new128x2/20kx4 discard preflights each A1/A2 then from original23509 at same1ms, seed20260928/white_v3, matched275actualupdates. Each block<=45min, own complete resume if needed, totalS1A6h; health failure ownSTOP_AFTER_SAVE, preserve all weights/actual exit/unique ledger. No old main or once/resume/cleanactive/recharge. Complete actor/encoder/critic/std/optimizers/RNG/history serialization, fresh simulator episodes reset history; not PhysX exact-state resume. A0 inheritedoptimizer vs new architectures freshoptimizer disclosed, not causal isolation. Actual behavior/wall/deploy comparison still pending, no MoE gate maturity.

Canonical230h/six extensions each once, newbudget0. Guardian15s,save25, stageactual cap6h includes prior partial/rejectedmoe_S1A costs; preflights loading/save/exit sameledger. Frozen SDK/CPU bytes exact before new PPO, active PPO now normal accounting.3060 old.5ms proof remains scoped, new1ms immutable package pending, no4090 blocking. Two-hour healthy quiet monitor remainsACTIVE; review/hold not all curricula finished. New experiment Git receipt to follow. Do not repeat any this-turn staging/readback launch/fixture review/old entry; only read_* collectors reusable.
'''
(E/'LATEST_HANDOFF.md').write_text(handoff,encoding='utf8')
out=dict(epoch=time.time(),baseline_sha256=hashlib.sha256(bp.read_bytes()).hexdigest(),main_plan_sha256=MASTER,current_root=launch['root'],source_count=213,current_actual_timestamp=actual['epoch'],new_budget_seconds=0)
(R/'HISTORY_EXECUTION_PUBLISHED.json').write_text(json.dumps(out,indent=2),encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  er='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  paths=[bp,PL/'MOD4_DT1000_WORKING_BASELINE.md',PL/'MOD4_MOE_EXECUTION_CONTRACT.json',E/'PLAN_APPROVAL.json',E/'EXECUTION_TRACKS.json',E/'LATEST_HANDOFF.md']
  for p in paths:
   s.put(str(p),er+p.name+'.history_actual');s.posix_rename(er+p.name+'.history_actual',er+p.name)
   with s.open(er+p.name,'rb') as f:assert hashlib.sha256(f.read()).digest()==hashlib.sha256(p.read_bytes()).digest()
  for root in [launch['root'],'/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007']:
   for p in (bp,E/'LATEST_HANDOFF.md',R/'HISTORY_EXECUTION_PUBLISHED.json'):
    s.put(str(p),root+'/reports/'+p.name)
finally:c.close()
print(json.dumps(out))
