from pathlib import Path
import getpass,json,os,sys,time,traceback
import deploy_two50_reconciled_original_writer_once as d
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def event(kind,**v):
 with (R/'TWO50_FIRST_METADATA_APPEND_ONLY_JOURNAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(dict(epoch=time.time(),kind=kind,**v))+'\n');f.flush();os.fsync(f.fileno())
READ210=r'''
from pathlib import Path
import json,os,psutil,subprocess,time
B=Path(v['owner_root']);specs=v['specs'];until=time.monotonic()+550;read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
while True:
 current=read(B/'OWNER_CURRENT.json') or {};rows=current.get('rows') or {};go=current.get('go') or {};errors=[str(p) for p in B.glob('*ORIGINAL_ERROR*.json')];errors+=sum([x.get('errors',[]) for x in rows.values()],[]);positive=all(k in go and rows.get(k,{}).get('phase')=='production' and (rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in specs)
 if positive or errors or (B/'OWNER_EXIT_ACTUAL.json').exists() or time.monotonic()>=until:break
 time.sleep(3)
identity=read(B/'OWNER_IDENTITY.json');own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith((str(B)+'/',v['roots']['e2']+'/')) for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);row=rows.get('e2',{});worker=row.get('worker') or {};worker_match=any(p['pid']==worker.get('pid') and abs(p['create_time']-worker.get('creation',-1))<.01 and p['cmdline']==worker.get('argv') for p in own);GPU_match=any(len(a:=line.split(','))>=2 and a[0].strip()==specs['e2']['GPU_UUID'] and a[1].strip()==str(worker.get('pid')) for line in compute.splitlines());clock=read(Path(v['roots']['e2'])/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');owner_match=bool(identity and any(p['pid']==identity['pid'] and abs(p['create_time']-identity['creation'])<.01 and p['cmdline']==identity['argv'] for p in own));proof=dict(epoch=time.time(),positive_PPO_both=positive,errors=errors,current=current,owner_identity=identity,owner_actual_create_argv_verified=owner_match,only_project_own_processes=own,compute_snapshot=compute,E2_worker_create_argv_verified=worker_match,E2_UUID_compute_verified=GPU_match,E2_actual_clock=clock,original_writer_two_fcntl_active=bool(current.get('original_canonical_active') and current.get('original_two_fcntl_held')),no_model_download_or_new_GO_or_account_write=True);print(json.dumps(proof))
'''
READ72=r'''
from pathlib import Path
import json,os,psutil,subprocess,time
B=Path(v['root']);q=json.loads((B/'NODE_CURRENT.json').read_bytes());row=q['row'];worker=row.get('worker') or {};own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);worker_match=any(p['pid']==worker.get('pid') and abs(p['create_time']-worker.get('creation',-1))<.01 and p['cmdline']==worker.get('argv') for p in own);GPU_match=any(len(a:=line.split(','))>=2 and a[0].strip()==v['spec']['GPU_UUID'] and a[1].strip()==str(worker.get('pid')) for line in compute.splitlines());clockp=B/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json';clock=json.loads(clockp.read_bytes()) if clockp.is_file() else None;print(json.dumps(dict(epoch=time.time(),current=q,own_processes=own,compute_snapshot=compute,worker_create_argv_verified=worker_match,UUID_compute_verified=GPU_match,actual_clock=clock,no_model_download_or_account_write=True)))
'''
def main():
 q=json.loads((R/'TWO50_ORIGINAL_ACCOUNT_COHORT_DETACHED_ACTUAL.json').read_bytes());put('TWO50_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv));event('started',run_id=q['run_id']);pw=getpass.getpass('72 E3 first actual PPO under original writer (hidden): ');c=None
 try:
  c=d.t.connect();a=d.code(c,d.t.PY,READ210,q,timeout=600);put('TWO50_OWNER_E2_FIRST_GO_PPO_COMPUTE_ACTUAL.json',a);event('source210_returned',positive=a['positive_PPO_both'],errors=a['errors']);c.close();c=None
  c=d.connect72(pw);pw=None;b=d.code(c,d.PY72,READ72,dict(root=q['roots']['recovery'],spec=q['specs']['recovery']),timeout=60);put('TWO50_E3_FIRST_GO_PPO_COMPUTE_ACTUAL.json',b)
  checks=dict(both_positive_PPO=a['positive_PPO_both'],no_errors=not a['errors'],owner_create_argv=a['owner_actual_create_argv_verified'],original_one_writer_two_fcntl=a['original_writer_two_fcntl_active'],E2_worker=a['E2_worker_create_argv_verified'],E2_GPU=a['E2_UUID_compute_verified'],E3_worker=b['worker_create_argv_verified'],E3_GPU=b['UUID_compute_verified'],E2_clock50=bool(a['E2_actual_clock'] and a['E2_actual_clock']['policy_hz']==50),E3_clock50=bool(b['actual_clock'] and b['actual_clock']['policy_hz']==50))
  for k,spec in q['specs'].items():
   row=a['current']['rows'].get(k,{}) if k=='e2' else b['current']['row'];save=row.get('latest_save') or {};go=a['current']['go'].get(k) or {};checks[k+'_actual_source_GO']=go.get('source_SHA')==spec['source_SHA'] and go.get('run_id')==q['run_id'] and go.get('save_deadline',0)-go.get('learning_started_epoch',0)==3600;checks[k+'_actual_Adam_updates']=save.get('updates',0)>0 and save.get('Adam_step')==spec['source_Adamstep']+20*save.get('updates',0)
  v=dict(epoch=time.time(),passed=all(checks.values()),checks=checks,source210=a,target72=b,actual_finite_transport_returned=True,one_original_writer_not_pending_accounting=True,not_future_FINAL_or_skill_PASS=True);put('TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json',v);event('actual_finite_returned',passed=v['passed']);print(json.dumps(dict(passed=v['passed'],checks=checks)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO50_FIRST_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_GPU_or_old_reader=True));raise
