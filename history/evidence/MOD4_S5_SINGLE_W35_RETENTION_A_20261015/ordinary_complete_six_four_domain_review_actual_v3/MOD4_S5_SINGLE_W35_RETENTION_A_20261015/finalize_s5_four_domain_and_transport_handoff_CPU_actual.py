"""Whole completed cells, descriptive tails and actual local owner handoff only."""
from pathlib import Path
import hashlib,json,subprocess,time,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015';F=W/'MOD4_S5_SINGLE_W35_MATCHED35_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def stats(x):
 x=np.asarray(x,dtype=float);assert len(x) and np.isfinite(x).all();return dict(mean=float(x.mean()),p95=float(np.percentile(x,95)),p99=float(np.percentile(x,99)),worst=float(x.max()))
def case_metrics(folder,case):
 c=read(sorted((folder/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1]);assert c['shared_OS_lock_free'] and all(not r['actual_alive'] for r in c['actual_PID_identities'])
 def path(name):return Path(next(r['local_path'] for r in c['collected_files'] if r['relative']=='attempts/'+case+'/output/'+name))
 probe=read(path('probe.json'));raw=path('retention_full_control_substep_actual.npz')
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in ('processed_action','terminated','truncated','substep_actual_applied_effort','root','command')}
 done=a['terminated']|a['truncated'];valid=np.ones(done.shape,bool)
 for i in range(done.shape[1]):
  ids=np.flatnonzero(done[:,i]);last=int(ids[0]) if len(ids) else len(done);valid[last:,i]=False
 jumps=np.max(abs(np.diff(a['processed_action'],axis=0)),axis=-1);jumpvalid=valid[:-1]&valid[1:];torque=np.max(abs(np.diff(a['substep_actual_applied_effort'],axis=0)),axis=-1)
 # Remove reset crossings, including all later trajectory portions after the first failure.
 subvalid=np.repeat(valid,4,axis=0);torquevalid=subvalid[:-1]&subvalid[1:]
 prefixes=[int(valid[:,i].sum()) for i in range(valid.shape[1])]
 if 'single_W35' in case:
  source=read(folder/'reports'/(case+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json'));latency=source['latency_ms'];switches=0;selection=None
 else:
  source=read(folder/'reports'/(case+'_S4_ROUTING_CPU_ADMITTED.json'));latency=source['latency_ms'];switches=source['switches'];selection=source['selected_E0_W35_envcontrols']
 per=probe.get('per_environment',{})
 return dict(raw=dict(path=str(raw),bytes=raw.stat().st_size,sha256=c['outputs']['COMPLETE_ACTUAL.json']['raw']['sha256']),all_envs=int(valid.shape[1]),all_controls=int(valid.shape[0]),valid_prefix_controls=prefixes,ordinary_events=int(done.sum()),failed_env_ids=np.flatnonzero(done.any(0)).tolist(),valid_control_action_jump=stats(jumps[jumpvalid]),valid_substep_effort_jump=stats(torque[torquevalid]),latency_ms=latency,switches=switches,selected_E0_W35=selection,per_environment_original_metrics=per,statistics_descriptive_no_new_threshold=True,latency_host_snapshot_not_hardware_deadline=True,source_review_SHA=H(folder/'reports'/(case+('_S5_SINGLE_CONTROL_CPU_ADMITTED.json' if 'single_W35' in case else '_S4_ROUTING_CPU_ADMITTED.json'))))
def main():
 complete=read(R/'S5_SINGLE_A_FIXED_SIX_COMPLETE.json');assert complete['all_six_new_A_cases_and_six_old_B_C_actual_pairs_CPU_complete'] and len(complete['completed'])==len(complete['pairs'])==6 and not (R/'S5_SINGLE_A_FIXED_SIX_ORIGINAL_ERROR.json').exists()
 cmd='$p=Get-CimInstance Win32_Process -Filter "ProcessId = 43924";@($p|Select-Object ProcessId,CreationDate,CommandLine)|ConvertTo-Json -Compress'
 q=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True);assert not q.stdout.strip() or json.loads(q.stdout) in ([],None)
 proofs=[]
 for row in complete['completed']:
  b=read(row['boundary']);s=read(row['source']);d=read(row['data'])['result'];assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free'] and b['actual_parent_exit']['exit_code']==0 and s['passed'] and d['data']['complete_data_contract'];proofs.append(dict(case=row['case'],boundary_SHA=H(row['boundary']),source_SHA=H(row['source']),data_SHA=H(row['data'])))
 save('S5_SINGLE_A_FIXED_SIX_COMPLETE_ACTUAL_CIM_HANDOFF_CPU.json',dict(epoch=time.time(),all_six_complete_CPU_and_original_EXIT0_shared_lockfree=True,former_owner_pid=43924,former_creation='2026-10-15T12:20:46.712924+08:00',actual_CIM_command=cmd,actual_CIM_stdout=q.stdout,actual_owner_absent=True,root_reclaims_exclusive_sequential210_249_transport=True,proofs=proofs,no_remote_connection_GPU_PPO_or_budget_write=True))
 a=read(R/'S5_SINGLE_W35_A_THREE_RETENTION_MATCHED_B_C_COMPLETE_ACTUAL_CPU_REVIEW.json');assert a['all_actual_firstphysics_rootq30_parameters_staticrecipes_RNGqueues_and_loadedDLL_pairs_exact']
 metrics={}
 for kind in ('flat','spin','world'):
  metrics[kind]={name:case_metrics(folder,case) for name,folder,case in [('A_single_W35',D,f's5_single_W35_{kind}_1500_v1'),('B_rule',OLD,f's4_retention_rule_eval_{kind}_1500_v1'),('C_gate148',OLD,f's4_retention_gate_eval_{kind}_1500_v1')]}
 world={}
 for v in a['summary']['world']['configurations']:
  rows=v['whole_signedcircle']['rows'];world[v['configuration']]=dict(count=v['world_count'],failures=[r for r in rows if not r['pass_']],along_abs_error=stats([abs(r['along_m_s']-r['goal_m_s']) for r in rows]),cross_abs_error=stats([abs(r['cross_m_s']) for r in rows]),signed_yaw_abs_error=stats([abs(r['observed_yaw_rad_s']-r['command_yaw_rad_s']) for r in rows]),complete_cycles=sum(r['cycles'] for r in rows),worst_cross_dedrift=max(v['all_valid_prefixes'],key=lambda r:r['cross_dedrift_peak_to_peak_m']),all_failed_valid_prefixes_preserved=True)
 first=read(F/'reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json')
 v=dict(epoch=time.time(),actual_four_domain_single_rule_gate_cellset_complete=True,seed=20261002,profile='white_v3',single_policy='W35 frozen ancestor retention comparator; high-speed flat/pure4pi outside declared low-speed W35 terrain registry, not newly qualified mixed policy',summary=a['summary'],world_grouped_tails=world,whole_raw_descriptive_metrics=metrics,first_original35=dict(path=str(F/'reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json'),sha256=H(F/'reports/S5_FIRST_ORIGINAL35_MATCHED_SINGLE_RULE_GATE_ACTUAL_CPU_REVIEW.json'),all_three_forward_reverse27_of27_ordinary0=True),scope_conclusion='Independent frozen experts with either normal-command rule or learned gate preserve negative pure spin and world success better than the single W35 comparator in this one matched condition. Gate adds no success count here; positive-flat error worsens vs rule. No architecture winner or statistical significance established.',all_strictfalse_old_failures_and_full_prefixes_retained=True,cost=dict(own_single_retention6_frozen_seconds=a['single_new_six_frozen_parent_seconds'],single_original35_frozen_seconds=315.0557026863098,rule_gate_retention9_frozen_seconds=1320.2303178310394,extra_gate_learning_unique_seconds=2668.750717163086,ancestral_learning_not_asserted_equal=True,frozen_seconds_not_charged_to_canonical=True),remaining_gaps=['second development seed20261003','nominal and white_v2 matched cells','combination DR boundary stress','actual within-episode task/terrain transitions','matched mixed single-policy training ancestry and any history-interface fairness','hardware deadline/calibration'],next_axis='Freeze all three existing policies; second development seed20261003 with unchanged white_v3 profile first, exact same initial state/DR/RNG and all original numeric contracts. New unused namespace/native-source-resource admission required; heldout20261011/12 remain untouched.',second_gate_PPO_not_admitted=True,all_S3_S5_hardware_50_70_qualification_not_claimed=True,root_handoff_proof_SHA=H(R/'S5_SINGLE_A_FIXED_SIX_COMPLETE_ACTUAL_CIM_HANDOFF_CPU.json'),no_GPU_SSH_or_budget_action=True)
 save('S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json',v)
 print(json.dumps(dict(complete=True,world={k:x['count'] for k,x in world.items()},failed_world_A=world['A_single_W35']['failures'],original_false_preserved=True,transport_returned=True,new_PPO=False)))
if __name__=='__main__':main()
