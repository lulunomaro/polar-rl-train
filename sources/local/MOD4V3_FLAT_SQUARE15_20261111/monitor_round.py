"""Follow one authorized 40-minute run in the current task; local CPU replay."""
from pathlib import Path
import json,sys,time,hashlib,subprocess,traceback,shutil
ROOT=Path(r'D:\claude2\fangzhen')
sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
TRIAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_FLAT_SQUARE15_20261111'
PLAN=json.loads((TRIAL/'PLAN.json').read_text(encoding='utf-8'));REMOTE=PLAN['support'].rsplit('/support',1)[0];JOB=REMOTE+'/train040m_flat_square15_r1'
EVIDENCE=TRIAL/'evidence';MON=EVIDENCE/'training_round';MON.mkdir(exist_ok=True)
ARTIFACT=ROOT/'tmp/flat_square15_20261111_r1';ARTIFACT.mkdir(exist_ok=True)
EVAL=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110/replay_delay_diagnostic.py'
PYTHON=ROOT/'.venv/Scripts/python.exe'
last_checkpoint=set();worker=None;queue=[];seen_final=False;eval_results=[]
def get_json(s,path):
 try:
  with s.open(path,'rb') as f:return json.loads(f.read().decode('utf-8'))
 except FileNotFoundError:return None
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def inspect_eval(label,path):
 d=json.loads(path.read_text(encoding='utf-8'));rows=[]
 for case in json.loads((TRIAL/'CHECKPOINT_EVAL_TEMPLATE.json').read_text())['cases']:
  cases=[x for x in d['replays'][0]['cases'] if x['cmd_vx']==case.get('vx',0.) and abs(x['cmd_wz']-case.get('wz',0.))<1e-6 and abs(x['cmd_height']-case.get('height',.28))<1e-6]
  if not cases:continue
  mean=lambda k:sum(x[k] for x in cases)/len(cases)
  def passed(x):
   if x['reset_count'] or x['completed_steps']!=x['requested_steps']:return False
   if case.get('vx') in (2.,2.2):return x['vx_abs_error']<=.15
   if case.get('vx')==-1.5:return x['vx_abs_error']<=.20
   if case.get('wz',0.)>10:return x['wz_abs_error']<=abs(case['wz'])*.02
   if case.get('height') in (.2,.4):return x['height_abs_error']<=.02
   return None
  rows.append(dict(command=[case.get('vx',0.),case.get('wz',0.),case.get('height',.28)],vx_mean=mean('vx_mean'),wz_mean=mean('wz_mean'),height_mean=mean('height_mean'),resets=sum(x['reset_count'] for x in cases),passed=sum(passed(x) is True for x in cases) if passed(cases[0]) is not None else None,requested=len(cases)))
 summary=dict(checkpoint=label,physics='nominal MuJoCo',scope='same frozen-weight physical5ms replay; not training DR test',rows=rows,inputs_unchanged=d.get('inputs_unchanged'),path=str(path));write(MON/(label+'_EVAL_SUMMARY.json'),summary);eval_results.append(summary);print('CHECKPOINT_EVAL '+json.dumps(summary,ensure_ascii=False),flush=True)
started=time.time();iteration=0
while True:
 iteration+=1
 if worker and worker['proc'].poll() is not None:
  status=worker['proc'].returncode;worker['log'].close()
  if status==0 and worker['result'].exists():inspect_eval(worker['label'],worker['result'])
  else:print('EVAL_ERROR '+json.dumps(dict(label=worker['label'],exit=status,log=str(worker['logpath']))),flush=True)
  worker=None
 c=None
 try:
  c=connect();s=c.open_sftp();progress=get_json(s,JOB+'/LATEST_PROGRESS.json');final=get_json(s,JOB+'/FINAL.json');error=get_json(s,JOB+'/ERROR.json');closed=get_json(s,JOB+'/SAFE_CLOSED.json')
  names=s.listdir(JOB)
  first=get_json(s,JOB+'/FIRST_UPDATE.json')
  if first and not (TRIAL/'weights/model_first_complete.pt').exists():
   receipt=first['checkpoint'];dest=TRIAL/'weights/model_first_complete.pt';s.get(receipt['path'],str(dest));assert hashlib.sha256(dest.read_bytes()).hexdigest()==receipt['SHA'];write(MON/'FIRST_UPDATE.json',first)
  periodic=sorted(x for x in names if x.startswith('PERIODIC_') and x.endswith('M.json'))
  for name in periodic:
   if name in last_checkpoint:continue
   receipt=get_json(s,JOB+'/'+name)
   if not receipt:continue
   model=Path(receipt['path']).name;dest=ARTIFACT/model
   if not dest.exists():
    partial=dest.with_suffix(dest.suffix+'.partial');s.get(receipt['path'],str(partial));digest=hashlib.sha256(partial.read_bytes()).hexdigest();assert digest==receipt['SHA'];partial.rename(dest)
   else:assert hashlib.sha256(dest.read_bytes()).hexdigest()==receipt['SHA']
   shutil.copyfile(dest,TRIAL/"weights"/model)
   label=dest.stem;write(MON/name,receipt)
   check=dict(observed_utc=time.time(),checkpoint_receipt=receipt,progress=progress,checkpoint_local_path=str(dest),checkpoint_sha256=receipt['SHA'],checkpoint_sha_verified=True)
   write(MON/(label+'_CHECK.json'),check);print('FIVE_MINUTE_CHECK '+json.dumps(check,ensure_ascii=False),flush=True);queue.append((label,dest));last_checkpoint.add(name)
  if progress:
   out=dict(observed_utc=time.time(),elapsed=progress.get('training_elapsed_seconds'),iteration=progress['iteration'],mean_reward=progress['mean_reward'],forward_tracking=progress.get('forward_tracking'),done_totals=progress['done_totals'],losses=progress['losses'],actor_drift_l2=progress.get('actor_drift_l2'),checkpoint_count=len(last_checkpoint));print('PROGRESS '+json.dumps(out,ensure_ascii=False),flush=True)
  if error:
   write(MON/'ERROR.json',error);print('TRAINING_ERROR '+json.dumps(error),flush=True);seen_final=True
  if final and not seen_final:
   write(MON/'FINAL.json',final);receipt=final['checkpoint'];dest=ARTIFACT/'model_final.pt';s.get(receipt['path'],str(dest));assert hashlib.sha256(dest.read_bytes()).hexdigest()==receipt['SHA'];queue.append(('model_final',dest));seen_final=True;print('TRAINING_FINAL '+json.dumps(final),flush=True)
  if closed:write(MON/'SAFE_CLOSED.json',closed)
  s.close();c.close();c=None
 except Exception:
  print('MONITOR_READ_ERROR '+traceback.format_exc(),flush=True)
  if c:c.close()
 if not worker and queue:
  label,checkpoint=queue.pop(0);plan=json.loads((TRIAL/'CHECKPOINT_EVAL_TEMPLATE.json').read_text(encoding='utf-8'));plan['models']={label:str(checkpoint)};planpath=MON/(label+'_EVAL_PLAN.json');write(planpath,plan);result=MON/(label+'_EVAL.json');logpath=MON/(label+'_EVAL.log');log=logpath.open('xb');proc=subprocess.Popen([str(PYTHON),'-X','utf8','-B',str(EVAL),'--plan',str(planpath),'--out',str(result)],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);worker=dict(label=label,proc=proc,result=result,log=log,logpath=logpath);print('EVAL_START '+label,flush=True)
 if seen_final and not queue and not worker:
  write(MON/'MONITOR_COMPLETE.json',dict(elapsed_seconds=time.time()-started,checkpoint_receipts=len(last_checkpoint),eval_summaries=eval_results));print('MONITOR_COMPLETE',flush=True);break
 time.sleep(40)
