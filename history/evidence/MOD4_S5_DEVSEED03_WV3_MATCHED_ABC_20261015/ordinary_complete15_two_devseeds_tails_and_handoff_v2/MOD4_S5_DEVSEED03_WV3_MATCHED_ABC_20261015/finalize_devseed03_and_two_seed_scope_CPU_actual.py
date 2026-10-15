"""Consume completed own cases; no transport, GPU, learning, or threshold changes."""
from pathlib import Path
import hashlib,json,subprocess,time,os,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';A=W/'MOD4_S5_SINGLE_W35_RETENTION_A_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def stats(x):
 x=np.asarray(x,dtype=float);assert x.size and np.isfinite(x).all();return dict(mean=float(x.mean()),p95=float(np.percentile(x,95)),p99=float(np.percentile(x,99)),worst=float(x.max()))
def metrics(row):
 case=row['case'];O=Path(row['attempt'])/'output';source=read(row['routing']);physical=read(row['data'])['result'];probe=read(O/'probe.json');raw=O/'retention_full_control_substep_actual.npz'
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in ('processed_action','terminated','truncated','substep_actual_applied_effort','command')}
 done=a['terminated']|a['truncated'];valid=np.ones(done.shape,bool)
 for i in range(done.shape[1]):
  ids=np.flatnonzero(done[:,i]);last=int(ids[0]) if len(ids) else len(done);valid[last:,i]=False
 jump=np.max(abs(np.diff(a['processed_action'],axis=0)),axis=-1);v=valid[:-1]&valid[1:];effort=np.max(abs(np.diff(a['substep_actual_applied_effort'],axis=0)),axis=-1);sv=np.repeat(valid,4,axis=0);ev=sv[:-1]&sv[1:]
 out=dict(source_CPU_SHA=H(row['routing']),raw=dict(path=str(raw),bytes=raw.stat().st_size,sha256=physical['data']['raw_sha256']),ordinary=physical['data']['ordinary'],truncation=physical['data']['truncation'],valid_prefix_controls=valid.sum(0).tolist(),failed_env_ids=np.flatnonzero(done.any(0)).tolist(),original_flags=physical['old_original_flags'],per_environment_original_metrics=probe.get('per_environment',{}),valid_control_action_jump=stats(jump[v]),valid_substep_effort_jump=stats(effort[ev]),latency_ms=source['latency_ms'],switches=source.get('switches',0),selected_E0_W35=source.get('selected_E0_W35_envcontrols'),descriptive_statistics_no_new_threshold_or_board_deadline=True)
 if row['kind']=='flat':out['straight']=physical['straight']
 if row['kind']=='spin':out['pure4pi']=physical['pure4pi']
 if row['kind']=='world':
  target=physical['whole_signedcircle_original_target'];rows=target['rows'];out.update(world_count=physical['world_count'],world_rows=rows,world_failures=[x for x in rows if not x['pass_']],world_all_valid_prefixes=physical['all_valid_prefixes'],world_along_abs_error=stats([abs(x['along_m_s']-x['goal_m_s']) for x in rows]),world_cross_abs_error=stats([abs(x['cross_m_s']) for x in rows]),world_signed_yaw_abs_error=stats([abs(x['observed_yaw_rad_s']-x['command_yaw_rad_s']) for x in rows]))
  if row['mode']!='single_eval':
   with np.load(O/'S4_ROUTING_FULL_CONTROL_ACTUAL.npz',allow_pickle=False) as z:choice=z['z'];obs=z['shared_obs']
   outside=(abs(obs[...,0])>.300001)|(abs(obs[...,1:3]).max(-1)>1e-6)
   diagnostics={}
   for i in (20,40,49):
    decisions=choice[:,i];diagnostics[str(i)]=dict(E0_W35_counts=np.bincount(decisions,minlength=2).tolist(),switches=int(np.count_nonzero(np.diff(decisions))),W35_selections_outside_necessary_registered_command_condition=int(((decisions==1)&outside[:,i]).sum()),command_yaw_rad_s=float(obs[0,i,2]))
   out['routing_response_descriptive_only']=dict(world_env20_40_49=diagnostics,all_W35_choices_outside_necessary_command_condition=int(((choice==1)&outside).sum()),not_unique_contact_policy_or_mechanism_cause=True,no_inference_truth_or_action_change=True)
 return out
def main():
 c=read(R/'DEVSEED03_ABC_FIXED15_COMPLETE.json');assert c['all15_closed_and_CPU_admitted'] and len(c['completed'])==15 and len(c['pairs'])==9 and not (R/'DEVSEED03_ABC_FIXED15_ORIGINAL_ERROR.json').exists()
 cmd='$p=Get-CimInstance Win32_Process -Filter "ProcessId = 24348";@($p|Select-Object ProcessId,CreationDate,CommandLine)|ConvertTo-Json -Compress'
 proc=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True);assert not proc.stdout.strip() or json.loads(proc.stdout) in ([],None)
 seconds=0.;proofs=[]
 for row in c['completed']:
  b=read(row['boundary']);d=read(row['data'])['result'];s=read(row['routing']);e=b['actual_parent_exit'];assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free'] and e['exit_code']==0 and e['no_PPO'] and not e['canonical_budget_written'] and not e['original_error_present'] and d['data']['complete_data_contract'] and s['passed'];seconds+=e['unique_actual_parent_load_run_save_exit_seconds'];proofs.append(dict(case=row['case'],boundary_SHA=H(row['boundary']),data_SHA=H(row['data']),source_SHA=H(row['routing'])))
 for row in c['pairs']:
  assert H(row['path'])==row['sha256'] and read(row['path'])['result']['actual_initial_root_q30_parameters_recipes_RNG_queues_exact']
 put('DEVSEED03_COMPLETE15_ACTUAL_CIM_HANDOFF_CPU.json',dict(epoch=time.time(),actual_all15_closed_CPU_and9_initialpairs=True,former_owner_pid=24348,former_creation=1792041319.320,actual_CIM_command=cmd,actual_CIM_stdout=proc.stdout,actual_owner_absent=True,root_reclaims_exclusive_sequential210_249_transport=True,all_original_parent_EXIT0_and_actual_PIDout_shared_msvcrt_free=True,unique_frozen_parent_seconds=seconds,no_canonical_transaction=True,proofs=proofs))
 summary={k:{} for k in ('flat','spin','world')}
 for row in c['completed']:
  if row['steps']==1500:summary[row['kind']][{'single_eval':'A_single_W35','rule_eval':'B_rule','gate_eval':'C_gate148'}[row['mode']]]=metrics(row)
 previous=read(A/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json');assert previous['actual_four_domain_single_rule_gate_cellset_complete']
 combined={}
 for label in ('A_single_W35','B_rule','C_gate148'):
  old=next(x for x in previous['summary']['world']['configurations'] if x['configuration']==label);new=summary['world'][label];combined[label]=dict(seed02_world_count=old['world_count'],seed03_world_count=new['world_count'],world_successes_out_of128=old['world_count']+new['world_count'],seed03_fail_ids=[x['env_id'] for x in new['world_failures']],seed02_flags_preserved=old['original_flags'],seed03_flags_preserved=new['original_flags'])
 v=dict(epoch=time.time(),actual_second_development_seed_threeway_complete=True,seed=20261003,profile='white_v3',all15_CPU_and_original_exit_boundary_passed=True,all9_initial_rootq30_params_staticrecipes_RNGqueues_loadedDLL_exact=True,summary=summary,two_development_seed_world=combined,previous_seed02_evidence=dict(path=str(A/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json'),sha256=H(A/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json')),cost=dict(second_seed_frozen15_unique_parent_seconds=seconds,no_PPO_or_canonical_charge=True,extra_gate_learning_unique_seconds=2668.750717163086,ancestral_learning_not_asserted_balanced=True),scope_conclusion='In white_v3 across the two development seeds rule B world is128/128 and learnedgate C126/128. Gate C adds no success-count benefit over rule here and loses two world targets onseed03; both seed03 signed straight errors exceed rule. Preserve B as reference/fallback for these observed cells, keep C frozen for remaining fair conditions. Not a global architecture or all-skill verdict.',single_A_caveat='Existing W35 single-policy ancestor retention comparator; highspeed/pure/world stress is not its registered35mm low-speed terrain qualification or equal mixed-training ancestry.',all_old_false_and_failed_valid_prefixes_retained=True,no_statistical_significance_claimed_or_tick_as_independent_episode=True,remaining_gaps=['nominal andwhite_v2 matchedthreeway onboth developmentseeds','original35 seconddevseed/profile matching','combinationDR boundary stress','real within-episode task/terrain transitions','matched mixedsingle-policy trainingancestry fairness','hardware deadline and calibration'],next_scope='Frozen sameA/B/C; originalnominal andwhite_v2 profiles withseed02/03, actualsource/profile/API/native/resource admission before eachunusedscope. No secondgatePPO.',second_gate_PPO_not_admitted=True,S3_S5_overall_or_50_70_hardware_qualification_not_claimed=True)
 put('DEVSEED03_COMPLETE15_TWO_DEVSEED_THREEWAY_SCOPE_TAIL_COST_CPU_ACTUAL.json',v);print(json.dumps(dict(complete=True,world=combined,frozen_seconds=seconds,root_transport_returned=True,new_PPO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put('DEVSEED03_FINAL_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_SSH_PPO_budget=True));raise
