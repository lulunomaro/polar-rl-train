"""Follow this authorized course to closure, then compare frozen weights; no extra PPO."""
from pathlib import Path
import base64,json,sys,time,hashlib,subprocess,shlex
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=Path(__file__).resolve().parent;E=T/'evidence';M=E/'training_round'
PLAN=json.loads((T/'PLAN.json').read_text(encoding='utf-8'));REMOTE=PLAN['support'].rsplit('/support',1)[0]
def put(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(path):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except (FileNotFoundError,json.JSONDecodeError):return None
def get(s,path):
 try:
  with s.open(path,'rb') as f:return json.loads(f.read().decode('utf-8'))
 except FileNotFoundError:return None
while not (M/'MONITOR_COMPLETE.json').exists():
 if (M/'ERROR.json').exists():raise RuntimeError('Training error; retain evidence; no automatic extra PPO')
 time.sleep(30)
final=read(M/'FINAL.json');closed=read(M/'SAFE_CLOSED.json')
assert final and closed and final['elapsed_seconds']>=7200
summaries=[]
for path in sorted(M.glob('model_*m_EVAL_SUMMARY.json')):
 d=read(path);rows=[x for x in d['rows'] if x['passed'] is not None]
 score=sum(x['passed'] for x in rows)
 errors=sum(abs(x['vx_mean']-x['command'][0]) for x in rows if x['command'][0]!=0)
 summaries.append((score,-errors,path.name,d))
intermediate=[x for x in summaries if x[3]['checkpoint']!='model_120m']
assert intermediate
best=max(intermediate)
label=best[3]['checkpoint'];model_id='scutroughv1_'+label.removeprefix('model_')
models={'parent':PLAN['parent'],model_id:REMOTE+'/'+PLAN['training_round']['job']+'/'+label+'.pt','scutroughv1_120m':REMOTE+'/'+PLAN['training_round']['job']+'/model_120m.pt'}
put(T/'FINAL_MODELS_TEMPLATE.json',models)
put(E/'ASSESSMENT_SELECTION.json',dict(models=models,intermediate_selection='Highest original six-task pass count in identical nominal MuJoCo replay; tie by forward/back absolute mean error. This selects an assessment candidate, not a promoted policy.',selected_intermediate=model_id,cpu_rankings=[dict(checkpoint=x[3]['checkpoint'],six_task_passed=x[0],speed_error_sum=-x[1]) for x in sorted(summaries,reverse=True)]))
c=connect();s=c.open_sftp()
for file in ('FINAL_MODELS_TEMPLATE.json','checkpoint_unified_replay.py','checkpoint_remaining_replay.py','checkpoint_v0_retention.py'):
 s.put(str(T/file),REMOTE+'/'+file)
s.close();c.close()
runs=[('paired_flat_unified_r1','checkpoint_remaining_replay.py',None,None)]
runs += [(f'paired_unified_traverse_L{level}_r1','checkpoint_unified_replay.py',level,'traverse') for level in (0,5,9)]
runs += [('paired_unified_fast_L9_r1','checkpoint_unified_replay.py',9,'fast'),('paired_unified_gyro_L9_r1','checkpoint_unified_replay.py',9,'gyro')]
runs += [(f'paired_unified_landing_L{level}_r1','checkpoint_unified_replay.py',level,'landing') for level in (0,9)]
runs += [('paired_v0_retention_traverse_L9_r1','checkpoint_v0_retention.py',9,'traverse'),('paired_v0_retention_gyro_L9_r1','checkpoint_v0_retention.py',9,'gyro')]

for name,script,level,skill in runs:
 code='''from pathlib import Path
import json,subprocess,os,time,hashlib
base=Path(BASE);plan=json.loads((base/'PLAN.json').read_text());name=NAME
assert not (base/name).exists() and not (base/(name+'.log')).exists()
apps=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
assert not apps.stdout.strip(),'GPU compute owner present'
models=json.loads((base/'FINAL_MODELS_TEMPLATE.json').read_text())
cmd=[plan['python'],'-B','-u',str(base/SCRIPT),'--plan',str(base/'PLAN.json'),'--out',str(base/name),'--support',plan['support'],'--version',name,'--models',str(base/'FINAL_MODELS_TEMPLATE.json')]
if LEVEL is not None:cmd+=['--level',str(LEVEL)]
if SKILL is not None:cmd+=['--skill',SKILL]
env=dict(os.environ);root=Path(plan['root']);env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
with (base/(name+'.log')).open('xb',buffering=0) as log:child=subprocess.Popen(cmd,cwd=base/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
r={'pid':child.pid,'epoch':time.time(),'script':SCRIPT,'cmd':cmd,'models':{k:{'path':v,'sha256':hashlib.sha256(Path(v).read_bytes()).hexdigest()} for k,v in models.items()}}
(base/(name+'_LAUNCH.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r))
'''.replace('BASE',repr(REMOTE),1).replace('NAME',repr(name),1).replace('SCRIPT',repr(script)).replace('LEVEL',repr(level)).replace('SKILL',repr(skill))
 c=connect();i,o,err=c.exec_command('python3 -c '+shlex.quote('import base64;exec(base64.b64decode('+repr(base64.b64encode(code.encode()).decode())+'))'),timeout=45)
 out=o.read().decode();error=err.read().decode();status=o.channel.recv_exit_status();c.close()
 if status:raise RuntimeError(error[-2500:])
 receipt=json.loads(out);put(E/(name+'_LAUNCH.json'),receipt);print('LAUNCHED '+name,flush=True)
 while True:
  c=connect();s=c.open_sftp();result=get(s,REMOTE+'/'+name+'/RESULT.json');error=get(s,REMOTE+'/'+name+'/ERROR.json');closed=get(s,REMOTE+'/'+name+'/SAFE_CLOSED.json')
  progress=get(s,REMOTE+'/'+name+'/PROGRESS.json')
  if progress:put(E/(name+'_PROGRESS.json'),progress)
  if error:put(E/(name+'_ERROR.json'),error)
  if closed:
   put(E/(name+'_SAFE_CLOSED.json'),closed)
   dest=E/'remote_evaluations'/name;dest.mkdir(parents=True,exist_ok=True)
   for filename in s.listdir(REMOTE+'/'+name):
    if filename.endswith(('.json','.npz')):s.get(REMOTE+'/'+name+'/'+filename,str(dest/filename))
   s.get(REMOTE+'/'+name+'.log',str(E/(name+'.log')))
   s.get(REMOTE+'/'+name+'_LAUNCH.json',str(E/(name+'_LAUNCH.json')))
   if result:put(E/(name+'_RESULT.json'),result)
  s.close();c.close()
  if closed:
   if not result:raise RuntimeError('Evaluation closed without result '+name)
   log=(E/(name+'.log')).read_text(encoding='utf-8',errors='replace')
   capacity=[line for line in log.splitlines() if any(x in line for x in ('foundLostAggregatePairsCapacity','increase its value','buffer overflow','missed interactions','dropped contacts'))]
   if capacity:
    put(E/(name+'_INVALID_CAPACITY.json'),dict(warnings=capacity));raise RuntimeError('Evaluation capacity warning; retain invalid result and stop further assessments')
   print('COMPLETED '+name+' '+str(result['wall_seconds']),flush=True);break
  time.sleep(20)
put(E/'EVALUATIONS_COMPLETE.json',dict(epoch=time.time(),evaluations=[x[0] for x in runs],training_seconds=final['elapsed_seconds'],no_further_PPO=True))
print('UNIFIED_ROUGHV1_EVALUATIONS_COMPLETE',flush=True)
