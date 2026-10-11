"""Prepare new direct authorization and dispatch only the unique budget transaction."""
from pathlib import Path
import sys,json,time,hashlib,traceback,shlex

D=Path(__file__).resolve().parent
R=D/'reports'
R.mkdir(exist_ok=True)
W=D.parent
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope_io import E,B,connect_both,cleanup,put
REMOTE='/home/egde/rl_candidates/'+D.name
CENTRAL=E+'/reports/'
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
H=lambda b:hashlib.sha256(b).hexdigest()


def save(name,value):
 p=R/name
 with p.open('xb') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2).encode())
 return p


def main():
 assert not (R/'DIRECT_HUMAN_APPROVAL.json').exists(),'Already prepared; do not dispatch again'
 now=time.time()
 plan=dict(id='MOD4-BUDGET-RETRAIN-100H-REVISION-005',approved=True,
  human_message='预算再给你100小时，没毕业的可以复训',authorization_basis='direct_human_user_message',
  historical_master_sha256=MASTER,extension_id='USER_ADD100H_20261011_7TH',
  added_seconds=360000,prior_total_seconds=828000,new_total_seconds=1188000,
  canonical=B,scope='Additional100h and bounded retraining of unqualified experts within approved004/RM003 ranges',
  approved_retraining=True,prior_unqualified_checkpoints_are_review_evidence_not_auto_default=True,
  prioritized_work=['CURB20 forward direction/entry repair','WAVE35 complete signed route repair',
                    'remaining audited terrain scopes and trueSTAIR geometry admission','qualified frozen experts then gate and whole-system switching'],
  additional_hours_planning_only=dict(E1_CURB_repair=25,E1_WAVE_repair=25,
       remaining_SLOPE_RM_scopes=15,true_STAIR_geometry_and_skill=10,
       gate_whole_system_switching_and_matched_review=15,new_scope_preflight_and_repairs=10),
  original_S3_30h_plus_new_terrain75h_planning_ceiling_hours=105,
  allowances_not_target_consumption_or_ledger_reservations=True,
  actual_remaining_and_other_experts_gate_protection_precede_allocations=True,
  repair_reserve_formula='min(18h,0.13*actual remaining); planning only',
  isolated_actor_critic_optimizer_std_DR_rng_queues_geometry_commands_output=True,
  E0_frozen=True,accepted_SLOPE_5_8_10deg_scopes_frozen=True,
  CURB_next_warmstart_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',
  CURB_next_scope='New isolated20mm reset-entry single axis; actual fullfootprint and commandhistograms first',
  CURB_next_contracts_pending=True,learning_executor_started_by_this_revision=False,
  first_repair_observation_seconds=300,stable_block_max_seconds=7200,
  same_scope_max_blocks_before_full_review=2,same_failure_without_improvement_requires_diagnosis=True,
  fullsave_and_fourcase_complete_review_before_more_PPO_or_scope_increase=True,
  valid_same_scope_contracts_exact_SHA_reused=True,old_failed_or_completed_once_never_replayed=True,
  new_scope_PPO_preflight_discard_weights_charged_same_canonical=True,
  no_repeat45min_clock=True,unchanged=dict(clock=True,hardware=True,reward=True,
    learning_rate=True,KEEPSTD1=True,DR=True,terrain_family_proportions=True,actor_critic_action_interface=True),
  hardtop1_one_complete6action_no_action_or_parameter_averaging=True,
  no_oracle_environment_terrain_futurecontact_actor_or_gate_input=True,
  S8_new_dangerous_reset_not_authorized=True,hardware_not_calibrated=True,
  no_new_observation_hardware_model_or_unapproved_range_permission=True,
  local_WASD_player_untouched=True,optional93_94_stay_paused=True,
  monitor=dict(automation_id='mod4-10',status='ACTIVE',interval_hours=2,healthy_pending_quiet=True),
  all_trials_saved_reports_errors_sync_monitors_Git_required=True)
 plan_path=save('MOD4_BUDGET_RETRAIN_100H_REVISION_005.json',plan)
 note='''# MOD4 新增100小时与未毕业专家复训修订005

人类直接授权：“预算再给你100小时，没毕业的可以复训”。新增360000秒，仅在唯一canonical账本安全边界登记第七次扩展；总授权由230小时变330小时。原charged、completed segments、六次扩展与active状态不改，不以离线等待计学习。

未毕业专家可以在独立新范围内有界复训。优先修CURB20正向跨坎方向与入口，再修WAVE35正反完整通行。暖启动取已完整实际行为审查来源，不自动续用退化检查点，不覆盖E0或其它专家。SLOPE已接受5/8/10度范围继续冻结；真实RM后续坡面和台阶先审几何与新范围合同。专家自身验收合格后才冻结接门控，整机切换另测。

新增100小时的可调整规划：CURB修复25h、WAVE修复25h、剩余坡面15h、真实台阶10h、门控与整机切换15h、新范围准入及修复10h。原S3含已用E1时间30h上限与本次新增地形75h合计105h规划上限；这些不是必须花完或账本预留，实际B及其它专家/门控保护优先。原E2/S7条件课程和min(18h,.13B)修复规划继续，危险自救/过洞/跳跃reset仍需后续具体批准。

每轮新修复先核真实assignment、完整车轮/collider footprint、镜像起点、selectedreset及命令方向有效暴露；仅一个难度轴。完整来源actor/critic/std/optimizer/allDR/global-named/dict-private CPUCUDA状态先exact核验，再显式新geometry/assignment迁移、CUDA磁盘roundtrip、来源episode+1及独立保存输出。不是PhysX exact resume。必要新CPU/SDK/native/完整小大PPO准入各一次，精确SHA复用已有合同，不重复45min时钟实验；预检权重弃用但成本保留。

首修复正式观察300s包含加载学习保存退出，save25/本机15s guardian；自己的完整save/PID/PASSED/唯一账段与退出后，完整地形+flat+spin+world实际审查，再决定合理续训或下一轴。同范围稳定块最多2h，连续两块同问题无改善先诊断，不靠预算增加盲训、改旧false或延窗缩路线重标失败。

此次只扩大时间和授权未毕业科目复训，不改变既有时钟、reward/LR/KEEPSTD1、硬件、全D0D7、五族比例、35actor/38critic/6action、hardtop1与原健康/接触/数据容差。新的控制器必须按七条登记扩展动态核1188000秒总额；原旧once中828000断言属于历史，不能热改或重跑旧入口。无新S8危险reset/实车部署/硬件标定/传感接口授权；不干预本地WASD、不复活93/94。

mod4-10保持ACTIVE每2h，健康pending静默。所有成功失败、有效未完成前缀、部署拒绝/reader错误、来源和同步巡检报告进入Git；权重、大原件只真实path-size-SHA。具体预算应用以新APPLIED回执与实际canonical为准，不凭本计划声称已应用。
'''
 md=R/'MOD4_BUDGET_RETRAIN_100H_REVISION_005.md'
 with md.open('xb') as f:f.write(note.encode())
 approval=dict(approved=True,authorization_basis='direct_human_user_message',
  human_message=plan['human_message'],recorded_epoch=now,
  quote_source='Direct human user message in current chat; not inferred from heartbeat',
  extension_id=plan['extension_id'],added_seconds=360000,authorized_total_after=1188000,
  historical_master_sha256=MASTER,revision_id=plan['id'],
  revision_json_sha256=H(plan_path.read_bytes()),revision_md_sha256=H(md.read_bytes()),
  central_approval_path=CENTRAL+'MOD4_BUDGET_RETRAIN_100H_005_APPROVAL.json',
  scope='New100h plus unqualified expert bounded retraining; no additional S8/interface/hardware permission')
 ap=save('DIRECT_HUMAN_APPROVAL.json',approval)
 # Meaningful pure checks before any transport or canonical mutation.
 from budget_retrain_contract import extend_once
 test=dict(authorized_training_seconds=828000,charged_training_seconds=511202.45738077164,
           remaining_training_seconds=316797.54261922836,active_segment=None,completed_segments=[{'test':'preserve'}],
           budget_extensions=[dict(extension_id=str(i),state='applied',authorization_basis='explicit_user_request',additional_training_seconds=s)
                             for i,s in enumerate([72000,72000,72000,72000,144000,360000])])
 updated=extend_once(test,approval,now,'receipt')
 assert updated['authorized_training_seconds']==1188000 and updated['completed_segments']==test['completed_segments']
 assert updated['remaining_training_seconds']-test['remaining_training_seconds']==360000
 negative=[]
 for label,value,auth in [('active',dict(test,active_segment={'pid':1}),approval),
                           ('replay',updated,approval),('missing_direct_authorization',test,dict(approval,approved=False)),
                           ('invalid_registered_total',dict(test,authorized_training_seconds=827999),approval)]:
  try:extend_once(value,auth,now,'receipt')
  except ValueError:negative.append(label)
  else:raise AssertionError('Unsafe extension accepted: '+label)
 save('PURE_BUDGET_CONTRACT_VERIFIED.json',dict(epoch=time.time(),valid_new7th_add100h=True,
    history_and_charged_preserved=True,unsafe_cases_rejected=negative,no_canonical_mutation=True))
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   try:f.stat(REMOTE)
   except FileNotFoundError:f.mkdir(REMOTE);f.mkdir(REMOTE+'/reports')
   else:raise AssertionError('New unique remote folder already exists; inspect only')
   prior=f.listdir(E+'/reports')
   mapping={'MOD4_BUDGET_RETRAIN_100H_REVISION_005.json':plan_path,
     'MOD4_BUDGET_RETRAIN_100H_REVISION_005.md':md,'MOD4_BUDGET_RETRAIN_100H_005_APPROVAL.json':ap}
   assert not any(name in prior for name in mapping)
   for name,path in mapping.items():put(f,CENTRAL+name,path.read_bytes())
   for path in (D/'budget_retrain_contract.py',D/'apply_new_seventh_extension_once.py'):
    compile(path.read_bytes(),str(path),'exec');put(f,REMOTE+'/'+path.name,path.read_bytes())
   put(f,REMOTE+'/reports/DIRECT_HUMAN_APPROVAL.json',ap.read_bytes())
  save('DISPATCH_STARTED.json',dict(epoch=time.time(),remote_script=REMOTE+'/apply_new_seventh_extension_once.py',
       budget_only_no_GPU_or_learning=True,do_not_repeat_after_uncertain_outcome=True))
  _,out,err=n.exec_command('/usr/bin/python3 '+shlex.quote(REMOTE+'/apply_new_seventh_extension_once.py'),timeout=50)
  raw=out.read();stderr=err.read();rc=out.channel.recv_exit_status()
  if rc:
   save('BUDGET_TRANSACTION_REJECTED.json',dict(epoch=time.time(),exit_code=rc,stdout=raw.decode(errors='replace'),
      stderr=stderr.decode(errors='replace'),actual_canonical_and_receipt_must_be_read_before_any_new_action=True,
      no_blind_once_replay=True))
   raise RuntimeError('Unique budget transaction refused; inspect actual result')
  value=json.loads(raw)
  save('BUDGET_APPLIED.json',value['budget']);save('METADATA_SYNCED.json',value['metadata'])
  with n.open_sftp() as f:
   for name in ('TRANSACTION_STARTED.json',):
    p=R/('REMOTE_'+name)
    with p.open('xb') as dest:dest.write(f.open(REMOTE+'/reports/'+name).read())
   assert f.open(CENTRAL+'USER_ADD100H_20261011_7TH_APPLIED.json').read()==json.dumps(value['budget'],ensure_ascii=False,indent=2).encode()
  print(json.dumps(dict(applied_once=True,added_hours=100,total_hours=330,
       remaining_hours_snapshot=value['budget']['remaining_hours_snapshot'],charged_unchanged=True,
       metadata_synced=True,expert_retraining_authorized=True,learning_executor_not_started=True)))
 finally:cleanup(n,w)


if __name__=='__main__':
 try:main()
 except BaseException:
  save('PREPARE_OR_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_transaction_replay=True))
  raise
