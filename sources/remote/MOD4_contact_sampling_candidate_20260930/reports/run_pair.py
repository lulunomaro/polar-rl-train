from pathlib import Path
import subprocess,json,os,time,fcntl,hashlib
r=Path('/home/egde/rl_candidates/MOD4_contact_sampling_candidate_20260930');p=r/'reports';old=Path('/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930')
lock=(p/'pair.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ck=old/'logs/2026-09-30_02-58-27_scut_straight_1.5m_repair/model_7450.pt'
files=[old/'isaac/mod4'/x for x in ['env.json','mod4_env.py','mod4_task.py','skills_isaac.py']]
before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
s={'status':'waiting_for_regular_evaluation','checkpoint':str(ck),'checkpoint_sha256':hashlib.sha256(ck.read_bytes()).hexdigest(),'started':time.time(),'runs':[],'source_before':before}
(p/'pair_status.json').write_text(json.dumps(s,indent=2))
while True:
 state=json.loads((old/'status.json').read_text());pid=state.get('evaluation_pid')
 if not pid or not Path('/proc/'+str(pid)).exists():break
 time.sleep(5)
for name,flag in [('legacy10ms',0),('eager5ms',1)]:
 s['status']='running';s['active_run']=name
 cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','isaac/mod4/sampling_pair_probe.py','--headless','--checkpoint',str(ck),'--num_envs','8','--steps','500','--seed','20260927','--solver_pos','16','--solver_vel','4','--output',str(p/(name+'.json'))]
 env=dict(os.environ,ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_CONTACT_EAGER5MS=str(flag))
 start=time.time()
 with (p/(name+'.log')).open('w') as log:
  child=subprocess.Popen(cmd,cwd=r,env=env,stdout=log,stderr=subprocess.STDOUT)
  s['active_pid']=child.pid;(p/'pair_status.json').write_text(json.dumps(s,indent=2))
  try:rc=child.wait(timeout=900)
  except subprocess.TimeoutExpired:child.terminate();rc=child.wait(timeout=60)
 output=p/(name+'.json')
 if rc==0 and not output.exists():rc=250
 s['runs'].append({'name':name,'returncode':rc,'elapsed_s':time.time()-start,'result_exists':output.exists()})
 if rc:s['status']='failed';break
else:s['status']='complete'
s['active_pid']=None;s['finished']=time.time();s['production_source_unchanged']=all(hashlib.sha256(f.read_bytes()).hexdigest()==before[str(f)] for f in files)
(p/'pair_status.json').write_text(json.dumps(s,indent=2))
