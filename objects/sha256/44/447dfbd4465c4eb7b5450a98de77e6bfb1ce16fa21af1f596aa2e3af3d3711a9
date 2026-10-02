import pathlib,json,subprocess,hashlib,time,fcntl,os
r=pathlib.Path('/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930');p=r/'reports/contact_probe_7450_20260930'
lock=(p/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ck=r/'logs/2026-09-30_02-58-27_scut_straight_1.5m_repair/model_7450.pt'
files=[r/'isaac/mod4'/k for k in ['env.json','mod4_task.py','mod4_env.py','skills_isaac.py']]
before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
manifest={'checkpoint':str(ck),'checkpoint_sha256':hashlib.sha256(ck.read_bytes()).hexdigest(),'started':time.time(),'training_pid_at_start':json.loads((r/'status.json').read_text()).get('training_pid'),'source_before':before,'runs':[],'status':'running'}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
while True:
 s=json.loads((r/'status.json').read_text());pid=s.get('evaluation_pid')
 if not pid or not pathlib.Path('/proc/'+str(pid)).exists():break
 time.sleep(5)
for pos,vel in [(16,4),(32,8)]:
 name=f'solver_{pos}_{vel}'
 cmd=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','isaac/mod4/contact_probe_v2.py','--headless','--checkpoint',str(ck),'--num_envs','8','--steps','500','--seed','20260927','--solver_pos',str(pos),'--solver_vel',str(vel),'--output',str(p/(name+'.json'))]
 start=time.time()
 with (p/(name+'.log')).open('w') as out:
  child=subprocess.Popen(cmd,cwd=r,stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES'))
  manifest['active_pid']=child.pid;manifest['active_run']=name;(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
  try:rc=child.wait(timeout=900)
  except subprocess.TimeoutExpired:child.terminate();rc=child.wait(timeout=60)
 manifest['runs'].append({'name':name,'returncode':rc,'elapsed_s':time.time()-start})
 if rc:manifest['status']='failed';break
else:manifest['status']='complete'
manifest['active_pid']=None;manifest['finished']=time.time();manifest['production_source_unchanged']=all(hashlib.sha256(f.read_bytes()).hexdigest()==before[str(f)] for f in files)
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
