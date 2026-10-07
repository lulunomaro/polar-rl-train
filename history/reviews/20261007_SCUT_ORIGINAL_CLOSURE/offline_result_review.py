"""Offline review of actual immutable SCUT closure measurements; no simulation or budget authority."""
from pathlib import Path
import ast,json,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';A=R/'api_review18';V=R/'metric_validation'
a=json.loads((A/'closure_original_30s.json').read_text());v=json.loads((V/'closure_original_30s.json').read_text())
z=np.load(A/'closure_original_30s.npz');vz=np.load(V/'closure_original_30s.npz');e=z['closure_m'];commands=z['commands'];omega=z['root_omega_body']
assert a['phase']==v['phase']=='completed' and e.shape==(6000,32,6)
assert all(np.isfinite(z[k]).all() for k in z.files)
assert hashlib.sha256((A/'closure_original_30s.npz').read_bytes()).hexdigest()==a['raw_sha256']
assert hashlib.sha256((V/'closure_original_30s.npz').read_bytes()).hexdigest()==v['raw_sha256']
assert a['policy_sha256']==v['policy_sha256'] and a['saved_env_sha256']==v['saved_env_sha256'] and a['USD_sha256']==v['USD_sha256']
assert not a['closure_termination_added'] and not v['closure_termination_added']
assert float(e.max())*1000==a['max_closure_mm'] and int((e>.002).sum())==a['samples_over_2mm']
assert all(abs(float(np.percentile(e,q))*1000-a['percentile_mm'][str(q)])<1e-12 for q in [50,95,99,99.9])
stage=json.loads((V/'STAGE_CONSTRAINT_READBACK.json').read_text())
assert len(stage['solver'])==32 and all(row['position']==12 and row['velocity']==6 for row in stage['solver'])
assert len(stage['enabled_external_loop_paths'])==32*6
maximum=np.unravel_index(np.argmax(e),e.shape);frames,env,joint=map(int,maximum)
above=e>.002;run=np.zeros((32,6),dtype=int);longest={'frames':0};reset_at={}
for row in a['resets']:reset_at.setdefault(row['physics_frames_before_reset'],[]).extend(row['envs'])
episode_start=np.zeros(32,dtype=int);settled=np.zeros((6000,32),dtype=bool)
for tick,b in enumerate(above):
 for row in reset_at.get(tick,[]):run[row]=0;episode_start[row]=tick
 settled[tick]=(tick-episode_start)>=100 # Separate diagnostic: at least 0.5 s after episode/reset, never a selected pass window.
 run=np.where(b,run+1,0);local=int(run.max())
 if local>longest['frames']:
  row,col=np.unravel_index(np.argmax(run),run.shape)
  longest={'frames':local,'end_frame':tick,'env':int(row),'joint':int(col),'seconds':local*.005}
assert longest['seconds']==a['longest_contiguous_over_2mm_seconds']
def stats(x):
 return {'max_mm':float(x.max())*1000,'rms_mm':float(np.sqrt(np.mean(x.astype(np.float64)**2)))*1000,
  'percentile_mm':{str(q):float(np.percentile(x,q))*1000 for q in [50,95,99,99.9]},'over_2mm_samples':int((x>.002).sum()),'samples':int(x.size),'over_2mm_percent':float(np.mean(x>.002))*100}
source=D/'original/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py';text=source.read_text(encoding='utf8');tree=ast.parse(text)
node=next(n for c in tree.body if isinstance(c,ast.ClassDef) and c.name=='Wheelbipe25V3Env' for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_get_dones')
term=ast.get_source_segment(text,node)
assert 'closure' not in term.lower() and '0.002' not in term
out={'scope':'SCUT flat_and_rotation published V14_2 robot and model_15000; current Isaac Sim 6.0.1 / Isaac Lab 6.1.14 with explicit platform API adapters. This is not their original-engine performance or MOD4 validation.',
 'source_commit':a['commit'],'model_sha256':a['policy_sha256'],'USD_sha256':a['USD_sha256'],'saved_config_sha256':a['saved_env_sha256'],
 'physics_dt_s':.005,'decimation':4,'policy_hz':50,'position_velocity_solver':[12,6],'num_envs':32,'simulated_seconds':30,'wall_seconds_dynamic':a['wall_seconds'],
 'whole_window':stats(e),'separate_after_reset_0p5s_diagnostic':stats(e[settled]),'per_joint_max_mm':[{'joint':row['path'].split('/')[-1],'max_mm':float(e[:,:,i].max())*1000} for i,row in enumerate(a['loop_joints'])],
 'maximum':{'frame':frames,'simulated_time_s':(frames+1)*.005,'env':env,'joint':a['loop_joints'][joint]['path'].split('/')[-1],
  'command':commands[frames//4,env].tolist(),'body_omega_previous_control_sample':omega[frames//4,env].tolist(),'seconds_since_last_reset':(frames-max([0]+[r['physics_frames_before_reset'] for r in a['resets'] if env in r['envs'] and r['physics_frames_before_reset']<=frames]))*.005},
 'longest_over_2mm':longest,'original_task_terminations':sum(len(x['terminated']) for x in a['termination_events']),'original_timeouts':sum(len(x['timeout']) for x in a['termination_events']),
 'all_recorded_arrays_finite':True,'observed_actual_signed_yaw_rate_rad_s':[float(omega[...,2].min()),float(omega[...,2].max())],
 'measurement_validation':v['measurement_validation'],'independent_validation_initial_1000_error_frames_exact':bool(np.array_equal(e[:1000],vz['closure_m'])),
 'all_192_loop_joints_enabled_in_stage':True,'all_32_stage_solver_properties_12_6':True,
 'original_SCUT_get_dones_has_closure_threshold':False,'SCUT_get_dones_AST_source_sha256':hashlib.sha256(term.encode()).hexdigest(),'SCUT_get_dones_line':node.lineno,
 'production_MOD4_2mm_contract_changed':False,'production_MOD4_dt_changed':False,'4090_operation':False,'PPO_updates':0,'canonical_budget_operations':0,
 'interpretation':['The public termination function inspected contains no 2 mm closure reset rule.',
 'Measured original-model closure can exceed 2 mm in this current-engine playback, including a multi-second excursion; not merely a single spike.',
 'No universal mechanical-health or sim2real safety threshold follows from this measurement.',
 'The four original task terminations were not classified by cause here; do not call the entire run fault-free.',
 'Separate settling diagnostics retain all primary full-window samples and are not used to select passing windows.']}
(R/'SCUT_CLOSURE_RESULT_REVIEW.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
