"""Consume completed original pairs; no transport, CUDA, training or ledger writes."""
from pathlib import Path
import hashlib,json,os,subprocess,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');return p
def main():
 complete=read(R/'FIRST_GATE_RETENTION_FIXED_NINE_COMPLETE.json')
 aggregate=read(R/'FIRST_GATE_FULL_THREE_RETENTION_RULE_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json')
 assert complete['all_nine_closed_and_CPU_admitted'] and len(complete['completed'])==9 and len(complete['pairs'])==3
 assert aggregate['actual_all_three_full1500_pairs_complete'] and not (R/'FIRST_GATE_RETENTION_FIXED_NINE_ORIGINAL_ERROR.json').exists()
 code="$x=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -and ($_.CommandLine -like '*run_first_gate_retention_fixed_nine_case_batch_once.py*' -or $_.CommandLine -like '*launch_first_gate_fixed_nine_local_hidden_once.py*') } | Select-Object ProcessId,CreationDate,CommandLine); ConvertTo-Json -InputObject $x -Compress"
 out=subprocess.run(['powershell','-NoProfile','-Command',code],capture_output=True,text=True,encoding='utf8',check=True)
 actual=json.loads(out.stdout);assert actual==[],actual
 evidence=[ref(R/'FIRST_GATE_RETENTION_FIXED_NINE_COMPLETE.json'),ref(R/'FIRST_GATE_FULL_THREE_RETENTION_RULE_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json')]
 total=0.;cases=[]
 for row in complete['completed']:
  b=read(row['boundary']);p=read(row['data']);route=read(row['routing'])
  assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free'] and b['original_failure'] is None
  assert b['actual_parent_exit']['exit_code']==0 and b['actual_parent_exit']['no_PPO'] and not b['actual_parent_exit']['canonical_budget_written']
  assert p['result']['data']['complete_data_contract'] and route['passed'] and route['all24_initial_final_source_exact']
  total+=b['actual_parent_exit']['unique_actual_parent_load_run_save_exit_seconds']
  cases.append(dict(case=row['case'],steps=row['steps'],physical=ref(Path(row['data'])),routing=ref(Path(row['routing'])),boundary=ref(Path(row['boundary'])),original_EXIT_NATURAL_missing=b['original_EXIT_NATURAL_missing']))
 for x in complete['pairs']:assert H(x['path'])==x['sha256'];evidence.append(ref(Path(x['path'])))
 diagnostics={}
 for kind in ('flat','spin','world'):
  stats=aggregate['summary'][kind];parts=[]
  for mode in ('rule_eval','gate_eval'):
   case=f's4_retention_{mode}_{kind}_1500_v1'
   receipt=read(sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'))[-1])
   def path(name):return Path(next(x['local_path'] for x in receipt['collected_files'] if x['relative']==f'attempts/{case}/output/{name}'))
   q=path('S4_ROUTING_FULL_CONTROL_ACTUAL.npz')
   with np.load(q,allow_pickle=False) as z:obs=z['shared_obs'];choice=z['z']
   command=obs[...,:3];groups=[]
   for cmd in np.unique(command.reshape(-1,3),axis=0):
    mask=(command==cmd).all(-1);n=int(mask.sum())
    if n>=80:groups.append(dict(command=cmd.tolist(),envcontrols=n,E0_W35=np.bincount(choice[mask],minlength=2).tolist()))
   groups.sort(key=lambda x:-x['envcontrols'])
   high=abs(command[...,2])>2.0001
   parts.append(dict(mode=mode,source_raw_routing=ref(q),high_yaw_gt2_envcontrols=int(high.sum()),high_yaw_gt2_E0_W35=np.bincount(choice[high],minlength=2).tolist(),command_rows_at_least80_envcontrols=groups,all_actual_feedback_only=True,not_counterfactual_physics_or_unique_cause=True))
  item=dict(rule_ordinary=stats['rule_ordinary'],gate_ordinary=stats['gate_ordinary'],routing=parts,old_false_rule=stats['old_original_flags_rule'],old_false_gate=stats['old_original_flags_gate'])
  if kind=='flat':
   item['straight']=[dict(command=a['command'],rule_error=a['error'],gate_error=b['error'],gate_minus_rule=b['error']-a['error'],original_strict_rule=a['original_strict'],original_strict_gate=b['original_strict']) for a,b in zip(stats['rule_straight'],stats['gate_straight'])]
  if kind=='spin':
   item['pure4pi']=[]
   for a,b in zip(stats['rule_pure4pi'],stats['gate_pure4pi']):
    ea=np.abs(np.asarray(a['values'])-a['command']);eb=np.abs(np.asarray(b['values'])-b['command'])
    item['pure4pi'].append(dict(command=a['command'],rule_count=a['within_original_absolute02_count'],gate_count=b['within_original_absolute02_count'],count=8,original_absolute_tolerance_rad_s=.2,mean_abs_error_rule=float(ea.mean()),mean_abs_error_gate=float(eb.mean()),max_abs_error_rule=float(ea.max()),max_abs_error_gate=float(eb.max()),individual_gate_minus_rule_abs_error=(eb-ea).tolist()))
  if kind=='world':
   old={x['env_id']:x for x in stats['rule_whole_signedcircle']['rows']};new={x['env_id']:x for x in stats['gate_whole_signedcircle']['rows']};assert old.keys()==new.keys() and len(old)==64
   rows=[]
   for i,a in old.items():
    b=new[i];rows.append(dict(env_id=i,pass_rule=a['pass_'],pass_gate=b['pass_'],along_abs_error_rule=abs(a['along_m_s']-a['goal_m_s']),along_abs_error_gate=abs(b['along_m_s']-b['goal_m_s']),cross_abs_rule=abs(a['cross_m_s']),cross_abs_gate=abs(b['cross_m_s']),yaw_abs_error_rule=abs(a['observed_yaw_rad_s']-a['command_yaw_rad_s']),yaw_abs_error_gate=abs(b['observed_yaw_rad_s']-b['command_yaw_rad_s']),complete_cycles_rule=a['cycles'],complete_cycles_gate=b['cycles']))
   item.update(rule_count=stats['rule_world_count'],gate_count=stats['gate_world_count'],improved_pass_ids=[x['env_id'] for x in rows if x['pass_gate'] and not x['pass_rule']],regressed_pass_ids=[x['env_id'] for x in rows if x['pass_rule'] and not x['pass_gate']],per_env_original_signedcircle=rows,all_64_valid_prefixes_preserved=True)
  diagnostics[kind]=item
 handoff=dict(epoch=time.time(),actual_local_CIM_matching_coordinator_and_launchhelper=actual,coordinator12232_and_launchhelper40800_absent=True,all_nine_cases_original_EXIT0_and_actual_PIDsout_shared_msvcrt_free=True,cases=cases,aggregate_evidence=evidence,total_unique_frozen_eval_parent_seconds=total,frozen0PPO_seconds_not_canonical_cost=True,no_new_connection_GPU_or_budgetwrite=True,root_reclaimed_sole_sequential210_249_transport=True,original_missing_EXIT_NATURAL_preserved=True)
 hand=save('FIRST_GATE_RETENTION_COMPLETE_NINE_ACTUAL_CIM_HANDOFF_CPU.json',handoff)
 diag=save('FIRST_GATE_RETENTION_ACTUAL_ROUTING_AND_CONTINUOUS_PAIR_DIAGNOSTICS_CPU.json',dict(epoch=time.time(),source_gate_SHA='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3',evidence=evidence,diagnostics=diagnostics,no_GPU_SSH_PPO=True,original_thresholds_and_false_unchanged=True))
 master=W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/actual_original_metadata/1791972851450503600/27_MOD4_MOE_MASTER_PLAN.md'
 assert H(master)=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 decision=dict(epoch=time.time(),decision_id='S4_FIRST_GATE148_LIMITED_PROTOTYPE_REVIEW_COMPLETE_S5_MATCHED_COMPARISON_NEXT',approved_master=ref(master),handoff=ref(hand),diagnostics=ref(diag),evidence=evidence,
  actual_S4_first_prototype_learning_and_complete_35_flat_spin_world_review_closed=True,
  practical_closeout_scope='Frozen E0b109 + W35b026 with gate148, original single development seed per protocol and retained exact DR realization; observed prototype only.',
  observed=dict(original35_forward_reverse=[27,27],original35_rule_forward_reverse=[27,27],flat_straight_gate_minus_rule=diagnostics['flat']['straight'],pure4pi_each_sign_rule_gate=[[8,8],[8,8]],world_rule_gate=[64,64],all_three_retention_ordinary_rule_gate=[[0,0],[0,0],[0,0]]),
  gate_advantage_over_rule_established=False,reason='No route or strict signedcircle count improvement in these matched cells; continuous metrics and switches differ. Same-cell preservation permits S5 comparison without another gate learning window.',
  keep_all_experts_gate_and_rule_sources=True,production_architecture_selected=False,allskills_hardware_or_50_70_qualified=False,
  current_plan_position='S4 first trained prototype limited review complete; entering S5 matched comparison preparation. S3 overall and S5 fair combination remain incomplete.',
  next_actual_scope='Audit and fill only genuinely missing single-policy A cells for same-feedback/robot/initialq/DR/source/runtime/seed/protocol as existing ruleB and gateC. Reuse exact existing evidence only after actual initial/source contract match. No automatic new PPO.',
  S5_gaps=['Matched single-policy A counterpart with identical physical initial state, information and evaluation source; cannot call protected Wave50 or arbitrary older SDK data matched.', 'Second development seed and nominal/white_v2/white_v3 profile coverage for combined architecture; heldout20261011/12 remain untouched by selection.', 'True task changes and switching/combination DR evidence; fixed35 moving route mostly selectsW35 and cannot prove terrain identification.', 'Per-task mean/worst/failure-prefix/switch/action-effort jumps/model-size/latency/total learning and frozen-eval costs; host latency is not board deadline.'],
  no_new_PPO_or_second_gate_block_admitted=True,no_new_native_or_full_case_dispatched_by_this_CPU_review=True,
  diagnostic_reader_path_misses_preserved=[dict(requested='review_s4_gate35_shared_routing_CPU.py',actual='review_first_trained_gate35_shared_routing_CPU.py',error='Get-Content path not found; read-only shell lookup, no source/data/GPU mutation'),dict(requested='prepare_first_gate_frozen35_CPU_package.py',actual='prepare_first_trained_gate_frozen35_CPU_package.py',error='Get-Content path not found; independent correct file read, no GPU replay')])
 dec=save('S4_FIRST_GATE_COMPLETE_RETENTION_LIMITED_PRACTICAL_CLOSEOUT_AND_S5_SCOPE_DECISION_CPU.json',decision)
 order=dict(epoch=time.time(),read_first=[str(dec),str(hand),str(diag)],next='Implement and actually validate the missing S5 matched single-policy counterpart, with explicit information and source identity. New unused namespace only after own CPU/source/resource admission; preserve all original physical thresholds. Do not retrain gate without a separate evidence-based axis decision.',sole_transport_owner='root after current actual CIM absence; any later genuinely active finite owner takes exclusive210/249 transport',budget='No new canonical transaction by frozen eval/CPU. Existing firstgate original parent2668.750717s remains once-settled, no secondgate learning granted.',do_not_repeat='All finite9 native/fullcases, firstgate learner and original35 rule/gate cases/Tasks/leases are consumed. No raw re-collection solely to duplicate SHA.',no_allcourse_completion=True)
 p=D/'NEXT_S4_RETENTION_COMPLETE_S5_MATCHED_SINGLE_POLICY_ACTUAL_WORK_ORDER.json';assert not p.exists();p.write_text(json.dumps(order,indent=2),encoding='utf8')
 print(json.dumps(dict(limited_review_complete=True,world_rule_gate=[64,64],pure_each_sign_rule_gate=[8,8],frozen_eval_unique_seconds=total,decision=str(dec),S5_not_yet_complete=True,new_PPO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('FINAL_SCOPE_CPU_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_transport=True));raise
