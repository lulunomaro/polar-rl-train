"""Offline review of existing seven3060 results and stopped own25525; no simulation."""
from pathlib import Path
import sys,json,math,statistics,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def raw(role,kind):return read(R/'windows'/('clk2500-solver32-'+('10-anchor-' if role=='anchor24827' else '20-candidate-')+kind)/'probe.json')
def params(r):return r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
def facts(r,kind):
 v=evidence(r,'spin' if kind=='world' else kind,15);assert v['pass_'],v
 a=r['frozen_architecture_audit'];assert a['variant']=='A0' and a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
 solver=r['clock2500_actual_solver'];assert solver['all_position32_velocity4'] and solver['physics_dt_s']==.0025 and solver['control_dt_s']==.01,solver
 assert r['seed']==20261002 and r['sensor_recipe']['profile']=='noise_bias_mild_v1'
 out=dict(v4=v,closure_mm=1000*r['max_closure_after_grace_m' if kind=='flat' else 'max_closure_m'],actual_solver=solver)
 if kind=='flat':out['constant_speed']=[dict(command=g['command_vx'],error=g['vel_error'],steady_error=g['steady_vel_error']) for g in r['groups'] if g['profile']=='constant']
 if kind=='spin':
  out['pure4pi']=[]
  for g in r['groups']:
   if g['profile']=='spin' and abs(abs(g['wz'])-4*math.pi)<1e-6:
    vals=[r['per_environment']['yaw_rate'][i] for i,gid in enumerate(r['group_ids']) if gid==g['group_id']]
    out['pure4pi'].append(dict(command=g['wz'],passed=sum(abs(x-g['wz'])<=.2 for x in vals),total=len(vals),values=vals,mean=statistics.mean(vals)))
 if kind=='world':
  t=target(r,.5);xs=t['rows'];assert len(xs)==64
  out.update(world_target=t,target_count=sum(x['pass_'] for x in xs),max_abs_cross=max(abs(x['cross_m_s']) for x in xs),along_range=[min(x['along_m_s'] for x in xs),max(x['along_m_s'] for x in xs)])
  out['directions']=[dict(yaw=w,passed=sum(x['pass_'] for x in xs if x['command_yaw_rad_s']==w),total=sum(x['command_yaw_rad_s']==w for x in xs),mean_abs_cross=statistics.mean(abs(x['cross_m_s']) for x in xs if x['command_yaw_rad_s']==w)) for w in (-2.,-1.,1.,2.)]
 return out
stop=read(R/'SAVED_STOP_SOURCE_ACTUAL.json');assert stop['S_active_training'] is None and not stop['actual_trainers'] and stop['all213_and_own_snapshot_exact']
health=stop['health'];tb=stop['tensorboard'];assert health['actual_task_reset_events']==1 and health['max_closure_error_m']<.002
assert tb['Episode_Termination/bad_orientation']['maximum']>0
assert all(tb['Episode_Termination/'+n]['maximum']==0 for n in ('base_contact','closure','mimic','low_base'))
report=dict(epoch=time.time(),scope='New2.5ms/TGS32-4 Windows functional scope and same-platform firstseed20261002-white_v3/noise-bias comparison24827→25211. Not dualseed/threeprofile or full cross-host dynamics proof;25525 not behavior-evaluated.',own25525=stop['own_full_CPU'],stopped_health=health,stop_classification='One bad_orientation episode termination; no observed closure/mimic/base-contact/low-base termination. Existing any-task global stop contract triggered.',termination_source_threshold_rad=.75,exact_failed_environment_ID_not_recorded=True,anchor24827={},candidate25211={},pairing=[],returned_files=[],no_new_PPO_or_probe=True)
for kind in ('flat','spin','world'):
 b,n=raw('anchor24827',kind),raw('candidate25211',kind)
 p=dict(kind=kind,root_exact=b['reset_root_before_physics']==n['reset_root_before_physics'],q_exact=b['reset_joint_pos_before_physics']==n['reset_joint_pos_before_physics'],parameters_exact=params(b)==params(n),probe_exact=b.get('probe_sha256')==n.get('probe_sha256'),seed_exact=b['seed']==n['seed'],solver_exact=b['clock2500_actual_solver']==n['clock2500_actual_solver'])
 assert all(v for k,v in p.items() if k!='kind'),p
 report['pairing'].append(p)
 for role in ('anchor24827','candidate25211'):report[role][kind]=facts(raw(role,kind),kind)
for d in sorted((R/'windows').iterdir()):
 if not d.is_dir():continue
 result=read(d/'result.json');manifest=read(d/'manifest.json');assert result['exit_code']==0 and result['errors']==[] and result['result_present']
 assert manifest['physics_dt_s']==.0025 and manifest['solver_position']==32 and manifest['no_learning'] and not manifest['canonical_write_authority']
 for n in ('probe.json','result.json','manifest.json'):
  p=d/n;report['returned_files'].append(dict(job=d.name,file=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
jobs=[read(d/'result.json') for d in (R/'windows').iterdir() if d.is_dir()]
report['cost']=dict(process_wall_seconds=sum(j['physics_process_wall_seconds'] for j in jobs),transfer_seconds=sum(j['transfer_seconds'] for j in jobs),sampled_peak_MiB=max(j['observed_GPU_memory_mib'] for j in jobs),continuous_peak_claimed=False)
(R/'CLOCK2500_COMPLETED_BEHAVIOR_AND_STOP_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
summary={role:dict(world=report[role]['world']['target_count'],max_abs_cross=report[role]['world']['max_abs_cross'],along=report[role]['world']['along_range'],directions=report[role]['world']['directions'],straight=[g for g in report[role]['flat']['constant_speed'] if abs(g['command'])==1.5],pure4pi=[{k:v for k,v in g.items() if k!='values'} for g in report[role]['spin']['pure4pi']],closure_mm={kind:report[role][kind]['closure_mm'] for kind in ('flat','spin','world')}) for role in ('anchor24827','candidate25211')}
print(json.dumps(dict(summary=summary,cost=report['cost'],stop=report['stop_classification']),indent=2))
