"""Record a direct-human execution amendment; do not hot-edit the running trainer."""
from pathlib import Path
import json,hashlib,time,sys,shutil
from physics_baseline_contract import validate_baseline

D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;repo=W/'polar-rl-train'
plans=repo/'history/plans';E=W/'MOD4_MOE_PLAN_EXECUTION_20261007/reports'
out=R/'DT2000_BASELINE_LOCKED.json'
assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(E/'PLAN_APPROVAL.json');v=read(R/'FREEZE_ACTUAL_INPUT.json')
assert a['approved'] and a['version']=='1.5' and sha(plans/'MOD4_MOE_MASTER_PLAN.md')==a['approved_plan_sha256']
assert v['own_checkpoint']['finite_tensors']==68 and len(v['runtime_source_freeze']['sha256'])==184
assert sha(D/'env.json')==v['environment_sha256']
clock=validate_baseline(v['environment'])
assert v['manifest']['robot_usd_sha256']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
assert v['manifest']['init_checkpoint_sha256']=='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
lock=dict(id='MOD4-DT2000-BASELINE-LOCK-001',epoch=time.time(),status='HUMAN_LOCKED_CURRENT_HEALTHY_BASELINE',
 plan_version='1.5',approved_master_sha256=a['approved_plan_sha256'],
 human_message='2ms健康就暂时固化训练参数，按照这个参数推进我们的计划训练',
 clock=clock,contact_model={'history_bins':3,'cross_bin_solver_step_average_impulse':True,'legacy_instantaneous_sensor_effective_period_s':.006,'within_step_piecewise_constant_force_assumption':True},
 production_PPO={'num_envs':20000,'steps_per_env':24,'initial_learning_rate':.0001,'learning_rate_schedule':'adaptive','save_interval':25,'clip_actions':6.,'activation':'elu','value_loss_coef':2.,'clip_param':.2,'entropy_coef':.005,'learning_epochs':5,'minibatches':4,'gamma':.99,'lam':.95,'desired_kl':.01,'max_grad_norm':1.,'KEEP_STD':1,'actual_std_not_reinitialized_to_nominal':True},
 baseline_env=v['environment'],baseline_env_sha256=v['environment_sha256'],
 runtime_root=v['root'],runtime_source_freeze=v['runtime_source_freeze'],
 actual_validation_snapshot_epoch=v['epoch'],own_run=v['own_run'],own_manifest_sha256=v['manifest_sha256'],own_checkpoint_snapshot=v['own_checkpoint'],
 robot_usd_sha256=v['manifest']['robot_usd_sha256'],import_contract_sha256=v['manifest']['import_contract_sha256'],
 data_contract={'closure_max_m':.002,'mimic_max_rad':.01,'original_torque_speed_hardware_envelope':True,'nonfinite_or_actual_task_failure_not_ignored':True},
 baseline_profile='white_v3',nominal_PD_COM_spring_armature_unchanged=True,
 plan_changes_allowed_only_as_separately_validated_stage={'S1A':'A0/A1/A2 history175/encoder3 comparison, same2ms/source23509 and matched actual learning exposure','experts_and_DR':'Only already-approved expert task and independently read-back DR groups; baseline clock/PPO do not drift','S8':'Still not authorized'},
 continuation={'current_A0_runs_to_own45min_complete_save':'unchanged','later_stable_block_max_seconds':7200,'S1A_total_ceiling_seconds':21600,'no_same_clock_repeat_benchmark_or_preflight_without_new_scope':True,'3060_old_clock_not_newclock_evidence':True,'encoder_CPU_preparation_not_SDK_or_training_deployment':True},
 fault_policy='Actual fault requests own complete STOP_AFTER_SAVE; preserve weights/raw, audit exit/active and use a new isolated reviewed recovery. No hot dt/solver edits or legacy entry resumption.',
 new_budget_seconds=0,budget_or_active_mutations=0,trainer_signal_or_runtime_change=0,
 future_stage_assertion_helper='physics_baseline_contract.py; CPU-tested, not injected into current184-source runtime')
out.write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bp=plans/'MOD4_DT2000_TRAINING_BASELINE.json';shutil.copyfile(out,bp)
doc=plans/'MOD4_DT2000_TRAINING_BASELINE.md'
doc.write_text('''# MOD4 2 ms训练基线固化（v1.5执行补充）

用户明确：“2ms健康就暂时固化训练参数，按照这个参数推进我们的计划训练”。本补充锁定已经实际验证的参数；总计划v1.5的原SHA与专家、DR、危险任务授权边界保持，不热改当前184来源或活跃trainer。

| 固定项 | 当前训练基线 |
|---|---|
| 物理步 / 策略周期 | 2 ms × 5；10 ms，100 Hz |
| 接触冲量积分 | 原5 ms窗口、3个历史bin；跨边界按时间重叠分摊求解器平均力 |
| solver | 16位置 / 4速度迭代 |
| PPO | 20k环境 × 24策略步；初始LR1e-4、原adaptive调度；每25iter完整保存 |
| 其余PPO | ELU、clip .2、entropy .005、5epochs/4minibatches、gamma .99/lam .95、KL .01、原gradnorm与value系数 |
| 当前参数随机化 | white_v3；质量惯量与6个独立输出.9–1.1、轮μ.7–1；非完整高DR |
| 原物理与硬件 | 详细闭链USD/原包络、PD/COM/3500N每米弹簧/armature保持 |
| 模型与数据检查 | 原2mm闭链/.01rad mimic、实际task/nonfinite/参数和积分一致性检查保留 |

这轮CPU/SDK、20k物理、三个15秒旧能力回放、128×2/20k×4完整PPO已经完成，明确复用，不继续扫其他步长。完整PPO实测81,252.645策略步/s；当前首45分钟A0正在学习。正式段尚未回放，不把周期完整保存说成能力毕业。

后续按原计划先完成A0，并在其学习期间准备A1五帧历史+速度监督、A2同历史联合PPO的接口；从同23509、同2ms和实际匹配学习量对照，收益不足保留A0。新增观察/encoder需要自己的真实缓存/reset/标签/critic合同和必要完整PPO，不省略新风险检查。架构选择后再推进独立技能专家、分组DR和学习门控；不是继续用一个策略覆盖所有科目。

训练时钟、PPO和名义硬件保持这一基线。计划内的专家任务、反馈接口和DR组，分别在批准范围内验证后变更；不因“固化”漏掉已列的完整DR，不把其队列冒称部署。S8自救/洞/跳跃具体reset仍需要原计划规定的后续批准。

3060继续独立评测，新2ms包须携带实际源码/资产/时钟和跨窗口积分并完成自身SDK/功能校准。旧.5ms六份结果已审查，但不能充当2ms证明；平台校准等待不阻塞4090自己已验证范围的学习。稳定块不再每45min做18份回归，沿用计划少量抽查/约6h或切科完整评审、精确复用。

实际故障先请求自己的完整保存，保留所有证据并审查账段，不静默热切步长或放松闭链门槛。canonical总230h及六次既有扩展保持，无新增时间、不重计尾段。本补充改变执行约束和准备工作，当前trainer与预算操作0。
''',encoding='utf8')
contract=plans/'MOD4_MOE_EXECUTION_CONTRACT.json';cc=read(contract)
cc['locked_training_baseline']=dict(id=lock['id'],document='history/plans/'+doc.name,machine='history/plans/'+bp.name,sha256=sha(bp),physics_dt_s=.002,decimation=5,control_period_s=.01,contact_bin_s=.005,solver=[16,4],human_message=lock['human_message'],no_further_clock_sweep_without_actual_fault=True)
cc['execution_state'].update(stage='S1A',status='A0_dt2000_locked_baseline_learning',root=v['root'],actual_epoch=v['epoch'])
contract.write_text(json.dumps(cc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
a.setdefault('execution_amendments',{})[lock['id']]=dict(epoch=lock['epoch'],human_message=lock['human_message'],baseline_sha256=sha(bp),document_sha256=sha(doc),scope='Lock validated2ms baseline and continue existing approved plan; no new budget/task/DR permission',master_document_unchanged=True)
(E/'PLAN_APPROVAL.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
t=read(E/'EXECUTION_TRACKS.json');t['learning']['locked_training_baseline']=lock['id'];t['performance'].update(stage='S0P_completed_validated2ms',further_clock_sweep_planned=False,baseline_lock=lock['id']);(E/'EXECUTION_TRACKS.json').write_text(json.dumps(t,indent=2),encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  er='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  for p in (bp,doc,contract,E/'PLAN_APPROVAL.json',E/'EXECUTION_TRACKS.json'):
   s.put(str(p),er+p.name+'.locked');s.posix_rename(er+p.name+'.locked',er+p.name)
   with s.open(er+p.name,'rb') as f:assert hashlib.sha256(f.read()).hexdigest()==sha(p)
  s.put(str(out),v['root']+'/reports/'+out.name)
finally:c.close()
print(json.dumps({'baseline_id':lock['id'],'baseline_sha256':sha(bp),'master_sha256_unchanged':sha(plans/'MOD4_MOE_MASTER_PLAN.md'),'new_GPU_PPO_budget_operations':0}))
