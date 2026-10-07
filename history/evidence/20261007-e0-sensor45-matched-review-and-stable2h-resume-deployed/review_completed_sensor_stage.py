"""Read-only actual-source metadata and offline review; no GPU or ledger writes."""
from pathlib import Path
import sys,json,math,statistics,time,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
def read(p):return json.loads(p.read_text(encoding='utf8'))
c=connect()
try:
 sf=c.open_sftp();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
 names=['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','S1A_ARCHITECTURE_SELECTION.json','SENSOR_STAGE1_GIT_RECORDED.json','SENSOR_FORMAL_CURRENT_SOURCE_VERIFIED.json','SENSOR_COMPLETE_ASYNC_CANDIDATE_PUBLISHED.json']
 meta={n:json.loads(sf.open(E+'/reports/'+n).read()) for n in names}
 meta['LATEST_HANDOFF.md']=sf.open(E+'/reports/LATEST_HANDOFF.md').read().decode()
 (R/'SENSOR_FINAL_EXECUTION_METADATA_READ.json').write_text(json.dumps(meta,indent=2))
 assert meta['PLAN_APPROVAL.json']['approved'] and meta['PLAN_APPROVAL.json']['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b' and 'S2' in meta['PLAN_APPROVAL.json']['allowed_stages']
 returned=[]
 for d in sorted((R/'sensor_windows').iterdir()):
  if not d.is_dir():continue
  for n in ('probe.json','result.json'):
   local=(d/n).read_bytes();remote=sf.open(E+'/eval_results/'+d.name+'/'+n).read()
   assert local==remote,(d.name,n,'returned bytes mismatch')
   returned.append(dict(job=d.name,file=n,sha256=hashlib.sha256(local).hexdigest(),returned_exact=True))
finally:c.close()
def raw(variant,kind):
 job=('clk1000-s2complete-0'+str({'flat':1,'spin':2,'world':3}[kind])+'-'+kind) if variant=='baseline' else 'clk1000-s2complete-10-candidate-'+kind
 return read(R/'sensor_windows'/job/'probe.json')
def params(r):return r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
def facts(r,kind):
 v=evidence(r,'spin' if kind=='world' else kind,minimum_seconds=15);assert v['pass_'],v
 a=r['frozen_architecture_audit'];assert a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
 assert r['sensor_recipe']['profile']=='noise_bias_mild_v1'
 out=dict(v4=v,closure_mm=1000*r['max_closure_after_grace_m' if kind=='flat' else 'max_closure_m'])
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
actual=read(R/'SENSOR_DEPENDENCY_CURRENT_ACTUAL.json');formal=actual['receipts']['sensor_formal45_COMPLETE.json']
assert actual['owner'] is None and actual['child'] is None and actual['budget']['active_segment'] is None and actual['S_active_training'] is None
report=dict(epoch=time.time(),formal=formal,baseline={},candidate={},pairing=[],platform=[],returned_files=returned,scope='First seed20261002/white_v3; engineering noise_bias_mild_v1, new candidate evaluated on3060; no dualseed/threeprofile or clean-feedback candidate proof yet',no_new_learning=True)
for kind in ('flat','spin','world'):
 b,n=raw('baseline',kind),raw('candidate',kind)
 row=dict(kind=kind,root_exact=b['reset_root_before_physics']==n['reset_root_before_physics'],q_exact=b['reset_joint_pos_before_physics']==n['reset_joint_pos_before_physics'],parameters_exact=params(b)==params(n),probe_exact=b.get('probe_sha256')==n.get('probe_sha256'),seed_exact=b['seed']==n['seed'])
 assert all(v for k,v in row.items() if k!='kind'),row
 report['pairing'].append(row);report['baseline'][kind]=facts(b,kind);report['candidate'][kind]=facts(n,kind)
 native=read(R/'native_evidence/dependency'/('sensor_baseline_'+kind+'.json'))
 assert native['reset_root_before_physics']==b['reset_root_before_physics'] and native['reset_joint_pos_before_physics']==b['reset_joint_pos_before_physics'] and params(native)==params(b)
 nf=facts(native,kind);p=dict(kind=kind,initial_root_q_parameters_exact=True,native_v4_pass=nf['v4']['pass_'],windows_v4_pass=report['baseline'][kind]['v4']['pass_'],dynamic_bit_exact_claimed=False)
 if kind=='world':
  x,y=nf['world_target']['rows'],report['baseline'][kind]['world_target']['rows']
  assert [r['env_id'] for r in x]==[r['env_id'] for r in y]
  p.update(native_count=nf['target_count'],windows_count=report['baseline'][kind]['target_count'],max_cross_difference=max(abs(a['cross_m_s']-b['cross_m_s']) for a,b in zip(x,y)))
 report['platform'].append(p)
cost=[read(d/'result.json') for d in (R/'sensor_windows').iterdir() if d.is_dir()]
assert all(j['exit_code']==0 and not j['errors'] and j['result_present'] for j in cost)
report['cost']=dict(process_wall_s=sum(j['physics_process_wall_seconds'] for j in cost),transfer_s=sum(j['transfer_seconds'] for j in cost),sampled_peak_mib=max(j['observed_GPU_memory_mib'] for j in cost),continuous_peak_claimed=False)
(R/'SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json').write_text(json.dumps(report,indent=2))
summary={v:dict(world=report[v]['world']['target_count'],maxcross=report[v]['world']['max_abs_cross'],along=report[v]['world']['along_range'],straight={g['command']:g['error'] for g in report[v]['flat']['constant_speed'] if abs(g['command'])==1.5},pure4pi=[(g['passed'],g['total'],g['mean']) for g in report[v]['spin']['pure4pi']]) for v in ('baseline','candidate')}
print(json.dumps(dict(summary=summary,platform=report['platform'],cost=report['cost'],formal=dict(source=formal['checkpoint'],health=formal['health'],actual_updates=formal['health']['control_steps']//24,steps=formal['actual_environment_steps'],charged_seconds=formal['unique_completed_segment'][0]['ended_epoch']-formal['unique_completed_segment'][0]['started_epoch'])),indent=2))
