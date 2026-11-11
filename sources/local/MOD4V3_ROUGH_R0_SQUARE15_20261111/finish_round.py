"""Finish the authorized R0 round; evaluate frozen parent and saved checkpoints only."""
from pathlib import Path
import base64,json,sys,time,hashlib
ROOT=Path(r'D:/claude2/fangzhen')
sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
TRIAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_ROUGH_R0_SQUARE15_20261111'
PLAN=json.loads((TRIAL/'PLAN.json').read_text());REMOTE=PLAN['support'].rsplit('/support',1)[0]
E=TRIAL/'evidence'
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def get(s,path):
 try:
  with s.open(path) as f:return json.loads(f.read().decode())
 except FileNotFoundError:return None
while True:
 c=connect();s=c.open_sftp();final=get(s,REMOTE+'/train020m_rough_r0_square15_r1/FINAL.json');closed=get(s,REMOTE+'/train020m_rough_r0_square15_r1/SAFE_CLOSED.json');error=get(s,REMOTE+'/train020m_rough_r0_square15_r1/ERROR.json');s.close();c.close()
 if error:raise RuntimeError('Training ERROR; retain evidence, no evaluation automatically launched')
 if final and closed:break
 time.sleep(30)
assert final['elapsed_seconds']>=1200
put(E/'TRAIN_FINAL.json',final);put(E/'TRAIN_SAFE_CLOSED.json',closed)
for name,script in [('paired_flat_final_r1','checkpoint_remaining_replay.py'),('paired_rough_final_r1','checkpoint_rough_replay.py')]:
 code=r"""from pathlib import Path
import json,subprocess,os,time,hashlib
base=Path(BASE);plan=json.loads((base/'PLAN.json').read_text());name=NAME
assert not (base/name).exists() and not (base/(name+'.log')).exists()
apps=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
assert not apps.stdout.strip(),'GPU compute owner present'
models=json.loads((base/'FINAL_MODELS_TEMPLATE.json').read_text())
for label,path in models.items():assert Path(path).is_file(),label
cmd=[plan['python'],'-B','-u',str(base/SCRIPT),'--plan',str(base/'PLAN.json'),'--out',str(base/name),'--support',plan['support'],'--version',name,'--models',str(base/'FINAL_MODELS_TEMPLATE.json')]
env=dict(os.environ);root=Path(plan['root']);env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
with (base/(name+'.log')).open('xb',buffering=0) as log:child=subprocess.Popen(cmd,cwd=base/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
r={'pid':child.pid,'epoch':time.time(),'script':SCRIPT,'cmd':cmd,'models':{k:{'path':v,'sha256':hashlib.sha256(Path(v).read_bytes()).hexdigest()} for k,v in models.items()}}
(base/(name+'_LAUNCH.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r))
""".replace('BASE',repr(REMOTE),1).replace('NAME',repr(name),1).replace('SCRIPT',repr(script))
 c=connect();cmd="python3 -c \"import base64;exec(base64.b64decode('"+base64.b64encode(code.encode()).decode()+"'))\""
 _,o,err=c.exec_command(cmd,timeout=45);out=o.read().decode();error=err.read().decode();status=o.channel.recv_exit_status();c.close()
 if status:raise RuntimeError(error[-2500:])
 receipt=json.loads(out);put(E/(name+'_LAUNCH.json'),receipt);print('LAUNCHED '+name,flush=True)
 while True:
  c=connect();s=c.open_sftp();result=get(s,REMOTE+'/'+name+'/RESULT.json');error=get(s,REMOTE+'/'+name+'/ERROR.json');closed=get(s,REMOTE+'/'+name+'/SAFE_CLOSED.json')
  if error:put(E/(name+'_ERROR.json'),error)
  if closed:
   put(E/(name+'_SAFE_CLOSED.json'),closed)
   if result:put(E/(name+'_RESULT.json'),result)
   for f in ('INITIAL_DR.json',):
    d=get(s,REMOTE+'/'+name+'/'+f)
    if d:put(E/(name+'_'+f),d)
   s.get(REMOTE+'/'+name+'.log',str(E/(name+'.log')))
  s.close();c.close()
  if closed:
   if not result:raise RuntimeError('Evaluation closed without RESULT '+name)
   print('COMPLETED '+name+' '+str(result['wall_seconds']),flush=True);break
  time.sleep(20)
put(E/'EVALUATIONS_COMPLETE.json',dict(epoch=time.time(),evaluations=['paired_flat_final_r1','paired_rough_final_r1'],training_seconds=final['elapsed_seconds']))
print('R0_EVALUATIONS_COMPLETE',flush=True)
