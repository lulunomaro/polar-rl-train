"""Launch paired no-optimizer stair evaluations only after this PPO window releases GPU."""
from pathlib import Path
import sys,json,time,shlex,hashlib,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R.parent/'tmp'))
from step7_remote_access import connect
plan=json.loads((T/'PLAN.json').read_text(encoding='utf8'));remote=plan['support'].rsplit('/support',1)[0];job=remote+'/'+plan['training_round']['job'];O=T/'evidence/native_stair_replay';O.mkdir(exist_ok=True)
def run(c,cmd):
 _,out,err=c.exec_command(cmd,timeout=60);text=out.read().decode('utf8','replace');error=err.read().decode('utf8','replace');status=out.channel.recv_exit_status()
 if status:raise RuntimeError(str(status)+' '+text+' '+error)
 return text.strip()
models={'parent':plan['parent'],**{f'{m:03d}m':job+f'/model_{m:03d}m.pt' for m in (5,10,15,20)}}
while True:
 c=None
 try:
  c=connect();s=c.open_sftp();s.stat(job+'/SAFE_CLOSED.json');gpu=run(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits')
  if not gpu:break
 except FileNotFoundError:pass
 finally:
  if c:c.close()
 time.sleep(15)
c=connect();s=c.open_sftp();script=remote+'/checkpoint_stair_replay.py';s.put(str(T/'checkpoint_stair_replay.py'),script)
with s.open(remote+'/STAIR_EVAL_MODELS.json','w') as f:f.write(json.dumps(models))
launcher='''from pathlib import Path
import os,json,subprocess,sys
base=Path(__file__).resolve().parent;p=json.loads((base/'PLAN.json').read_text());name=sys.argv[1];height=sys.argv[2];speed=sys.argv[3];scenario=sys.argv[4];out=base/name
assert not out.exists() and not (base/(name+'.log')).exists()
r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True);assert not r.stdout.strip(),r.stdout
cmd=[p['python'],'-u','-B',str(base/'checkpoint_stair_replay.py'),'--plan',str(base/'PLAN.json'),'--support',p['support'],'--models',str(base/'STAIR_EVAL_MODELS.json'),'--out',str(out),'--version',name,'--level','0','--height',height,'--speed',speed,'--scenario',scenario]
env=dict(os.environ);root=Path(p['root']);env.update(CUDA_VISIBLE_DEVICES='0',PYTHONUNBUFFERED='1',WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
with (base/(name+'.log')).open('xb') as log:proc=subprocess.Popen(cmd,cwd=p['code'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps(dict(pid=proc.pid,command=cmd,out=str(out))))
'''
(T/'launch_stair_eval.py').write_text(launcher,encoding='utf8')
with s.open(remote+'/launch_stair_eval.py','w') as f:f.write(launcher)
s.close();c.close()
for name,height,speed,scenario in [('eval_up038_level0_v1','.38','2.2','up'),('eval_down028_level0_v1','.28','1.0','down')]:
 c=connect();receipt=json.loads(run(c,' '.join(shlex.quote(x) for x in [plan['python'],remote+'/launch_stair_eval.py',name,height,speed,scenario])));c.close();(O/(name+'_LAUNCH.json')).write_text(json.dumps(receipt,indent=2),encoding='utf8');print('NATIVE_EVAL_STARTED '+json.dumps(receipt),flush=True)
 while True:
  c=connect();s=c.open_sftp();complete=False
  try:s.stat(remote+'/'+name+'/SAFE_CLOSED.json');complete=True
  except FileNotFoundError:pass
  if complete:
   dest=O/name;dest.mkdir(exist_ok=True)
   for file in s.listdir(remote+'/'+name):
    if file.endswith(('.json','.npz')):s.get(remote+'/'+name+'/'+file,str(dest/file))
   s.get(remote+'/'+name+'.log',str(O/(name+'.log')))
  gpu=run(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits');s.close();c.close()
  if complete and not gpu:break
  time.sleep(15)
 print('NATIVE_EVAL_FINISHED '+name,flush=True)
 if (O/name/'ERROR.json').exists():raise RuntimeError('Native stair evaluator failed; see '+str(O/name/'ERROR.json'))
(O/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),models=models,no_optimizer=True,suites=2)),encoding='utf8');print('NATIVE_EVAL_COMPLETE',flush=True)

