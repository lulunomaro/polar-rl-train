"""Offline review of every matched case; never launches a simulator or optimizer."""
from pathlib import Path
import json,sys,math,statistics,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D/'review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
def read(p):return json.loads(p.read_text(encoding='utf8'))
native=read(R/'FROZEN_PROTOCOL_CURRENT_ACTUAL.json');old=read(R/'FROZEN_MATCHED_CURRENT_ACTUAL.json')
def raw(host,variant,kind):
 if host=='native':return old['receipts']['behavior_anchor_'+kind+'.json'] if variant=='anchor' else read(R/'native_frozen'/('behavior_'+variant+'_'+kind+'.json'))
 return read(next(p for p in (R/'clock1000_eval').iterdir() if '-sdk-' not in p.name and p.name.endswith('-'+variant.lower()+'-'+kind))/'probe.json')
def params(r):return r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
def facts(r,kind):
 v=evidence(r,'spin' if kind=='world' else kind,minimum_seconds=15);assert v['pass_'],v
 a=r['frozen_architecture_audit'];assert a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
 out=dict(v4=v,closure_mm=1000*r['max_closure_after_grace_m' if kind=='flat' else 'max_closure_m'],inference=a)
 if kind=='flat':
  out['constant_speed']=[dict(command=g['command_vx'],error=g['vel_error'],steady_error=g['steady_vel_error'],tilt=g['tilt']) for g in r['groups'] if g['profile']=='constant']
  out['ramp_stop_reverse']=[dict(command=g['command_vx'],error=g['vel_error'],stop_abs_speed=g['stop_abs_speed']) for g in r['groups'] if g['profile']!='constant']
 if kind=='spin':
  out['pure4pi']=[]
  for g in r['groups']:
   if g['profile']=='spin' and abs(abs(g['wz'])-4*math.pi)<1e-6:
    vals=[r['per_environment']['yaw_rate'][i] for i,gid in enumerate(r['group_ids']) if gid==g['group_id']]
    out['pure4pi'].append(dict(command=g['wz'],passed=sum(abs(x-g['wz'])<=.2 for x in vals),total=len(vals),values=vals,mean=statistics.mean(vals)))
  out['group_metrics']=[dict(command=g['wz'],profile=g['profile'],means=g['means']) for g in r['groups']]
 if kind=='world':
  t=target(r,.5);rows=t['rows'];assert len(rows)==64
  out['world_target']=t;out['target_count']=sum(x['pass_'] for x in rows)
  out['max_abs_cross']=max(abs(x['cross_m_s']) for x in rows);out['along_range']=[min(x['along_m_s'] for x in rows),max(x['along_m_s'] for x in rows)]
  out['direction_groups']=[]
  for w in (-2.,-1.,1.,2.):
   xs=[x for x in rows if x['command_yaw_rad_s']==w]
   out['direction_groups'].append(dict(yaw=w,passed=sum(x['pass_'] for x in xs),total=len(xs),mean_abs_cross=statistics.mean(abs(x['cross_m_s']) for x in xs),max_abs_cross=max(abs(x['cross_m_s']) for x in xs),mean_along=statistics.mean(x['along_m_s'] for x in xs)))
 return out
report=dict(epoch=time.time(),scope='First development seed20261002/white_v3, all80/88 environments and15s; no held-out final graduation',hosts={},pairing=[],platform=[],optimizer_confound_disclosed=True,no_new_learning=True)
for host in ('native','windows'):
 report['hosts'][host]={}
 for variant in ('anchor','A0','A1','A2'):
  report['hosts'][host][variant]={}
  for kind in ('flat','spin','world'):
   r=raw(host,variant,kind);b=raw(host,'anchor',kind)
   pairing=dict(host=host,variant=variant,kind=kind,root_exact=r['reset_root_before_physics']==b['reset_root_before_physics'],q_exact=r['reset_joint_pos_before_physics']==b['reset_joint_pos_before_physics'],parameters_exact=params(r)==params(b),probe_sha_exact=r.get('probe_sha256')==b.get('probe_sha256'),seed=r['seed'],profile=(params(r) or {}).get('profile'))
   assert pairing['root_exact'] and pairing['q_exact'] and pairing['parameters_exact'] and pairing['probe_sha_exact'],pairing
   report['pairing'].append(pairing);report['hosts'][host][variant][kind]=facts(r,kind)
for kind in ('flat','spin','world'):
 a,b=raw('native','anchor',kind),raw('windows','anchor',kind)
 assert a['reset_root_before_physics']==b['reset_root_before_physics'] and a['reset_joint_pos_before_physics']==b['reset_joint_pos_before_physics'] and params(a)==params(b)
 row=dict(kind=kind,root_q_parameters_exact=True,native_admission=True,windows_admission=True,dynamic_bit_exact_claimed=False)
 if kind=='world':
  na=target(a,.5)['rows'];wb=target(b,.5)['rows'];assert [x['env_id'] for x in na]==[x['env_id'] for x in wb]
  row.update(native_targets=sum(x['pass_'] for x in na),windows_targets=sum(x['pass_'] for x in wb),max_net_cross_platform_difference=max(abs(x['cross_m_s']-y['cross_m_s']) for x,y in zip(na,wb)),max_net_along_platform_difference=max(abs(x['along_m_s']-y['along_m_s']) for x,y in zip(na,wb)))
 report['platform'].append(row)
cost=[]
for d in sorted((R/'clock1000_eval').iterdir()):
 if d.is_dir():
  j=read(d/'result.json');assert j['exit_code']==0 and not j['errors'] and j['result_present'];cost.append({k:j[k] for k in ('job_id','physics_process_wall_seconds','transfer_seconds','observed_GPU_memory_mib','observed_peak_not_continuous_peak')})
report['windows_cost']=dict(jobs=cost,physics_wall_total_s=sum(x['physics_process_wall_seconds'] for x in cost),transfer_total_s=sum(x['transfer_seconds'] for x in cost),sampled_peak_mib=max(x['observed_GPU_memory_mib'] for x in cost),sampling_is_not_continuous_peak=True)
report['returned_all14_exact']=read(R/'COMPLETED_RETURN_AND_CONTRACT_READBACK.json')['all14_returned_exact']
assert report['returned_all14_exact']
(R/'S1A_ALL_MATCHED_BEHAVIOR_REVIEW.json').write_text(json.dumps(report,indent=2))
summary={host:{v:dict(world=report['hosts'][host][v]['world']['target_count'],worst_cross=report['hosts'][host][v]['world']['max_abs_cross'],straight={g['command']:g['error'] for g in report['hosts'][host][v]['flat']['constant_speed'] if abs(g['command'])==1.5},pure4pi=[(g['passed'],g['total'],g['mean']) for g in report['hosts'][host][v]['spin']['pure4pi']]) for v in ('anchor','A0','A1','A2')} for host in report['hosts']}
print(json.dumps(dict(summary=summary,platform=report['platform'],cost={k:v for k,v in report['windows_cost'].items() if k!='jobs'}),indent=2))
