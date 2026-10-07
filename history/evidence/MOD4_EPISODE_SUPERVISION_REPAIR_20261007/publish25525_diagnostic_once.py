from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,time,shutil,os,sys
D=Path('/home/egde/rl_candidates/MOD4_EPISODE_SUPERVISION_REPAIR_20261007');sys.path.insert(0,str(D));import supervise_episode_repair as w
s=w.s;OLD=w.OLD;row=s.q.w.read(OLD/'reports/env20k_S2_D1D2_stable2h_SAVED_EXIT.json');source=row['checkpoint'];p=Path(source['path']);assert s.q.base.sha(p)==source['sha256'];s.fullsave(p)
assert row['health']['actual_task_reset_events']==1 and row['health']['max_closure_error_m']<=.002
assert not (D/'reports/DIAGNOSTIC25525_PUBLISHED.json').exists()
E=s.q.ER.parent;package=s.q.w.read(OLD/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json')['package'];assert s.q.base.sha(Path(package['path']))==package['sha256']
t=E/'artifacts'/('clock2500-diagnostic25525-'+source['sha256']+'.pt');assert not t.exists();shutil.copyfile(p,str(t)+'.partial');assert s.q.base.sha(Path(str(t)+'.partial'))==source['sha256'];os.replace(str(t)+'.partial',t)
cp=dict(path=str(t),sha256=source['sha256'],bytes=t.stat().st_size);a=s.q.w.read(s.q.ER/'PLAN_APPROVAL.json');jobs=[]
for kind in ('flat','spin','world'):
 job='clk2500-solver32-40-diagnostic25525-'+kind;path=E/'eval_queue'/(job+'.json');assert not path.exists()
 item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Diagnostic25525 preserved after one bad_orientation training reset; not healthy-final or adopted source',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,protocol='Explicit diagnostic evaluation of retained candidate. Existing publisher refusal preserved. No claim of task-free training or new capability before actual replay.',artifacts=dict(runtime=package,checkpoint=cp),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=False)
 s.q.base.atomic_json(path,item);jobs.append(item)
s.write('DIAGNOSTIC25525_PUBLISHED.json',dict(epoch=time.time(),source=source,known_training_task_events=row['health']['actual_task_reset_events'],diagnostic_only_not_current_learning_source=True,jobs=jobs,no_canonical_write=True));print(json.dumps(dict(source=source,jobs=[j['job_id'] for j in jobs],diagnostic_only=True)))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();(R/'DIAGNOSTIC25525_PUBLISHED.json').write_bytes(raw);print(raw.decode())
finally:c.close()
