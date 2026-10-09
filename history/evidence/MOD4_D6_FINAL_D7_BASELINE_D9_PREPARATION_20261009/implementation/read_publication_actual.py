"""Read publisher phase and own real process; compare completed SDK bridge bytes."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();root='/home/egde/rl_candidates/MOD4_D9_COMBINATION_PREPARE_20261009';E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with n.open_sftp() as nf,w.open_sftp() as wf:
  reports={}
  for name in ('STARTED.json','STATE.json','ATTENTION.json','REVIEW_STARTED.json','REVIEW_STATE.json','REVIEW_ATTENTION.json','D9_NOMINAL_ACTUAL_SDK_REVIEW.json','PUBLISHED.json','SELECTED_D7_BEHAVIOR_SOURCE.json'):
   try:raw=nf.open(root+'/reports/'+name).read()
   except FileNotFoundError:continue
   reports[name]=json.loads(raw);(R/name).write_bytes(raw)
  start=reports.get('REVIEW_STARTED.json') or reports['STARTED.json'];pid=start['pid'];actual=None
  try:
   st=nf.open('/proc/'+str(pid)+'/stat').read().decode().rsplit(')',1)[1].split();argv=nf.open('/proc/'+str(pid)+'/cmdline').read().decode().split('\0');actual=dict(pid=pid,start_ticks=int(st[19]),state=st[0],ppid=int(st[1]),argv=[x for x in argv if x])
  except FileNotFoundError:pass
  if actual:assert actual['start_ticks']==start['start_ticks'] and any(x in actual['argv'] for x in (root+'/supervise_combination_publication.py',root+'/supervise_combination_sdk_reset_review.py'))
  else:assert reports.get('PUBLISHED.json') or reports.get('REVIEW_ATTENTION.json') if 'REVIEW_STARTED.json' in reports else reports.get('ATTENTION.json')
  job='clk2500-closure-episode-d3-100-d9-nominal-sdk';sdk={}
  try:res=json.loads(nf.open(E+'/eval_results/'+job+'/result.json').read())
  except FileNotFoundError:res=None
  if res and res.get('phase')=='complete':
   folder=R/'nominal_sdk';folder.mkdir(exist_ok=True)
   for name in ('probe.json','result.json'):
    raw=nf.open(E+'/eval_results/'+job+'/'+name).read();assert raw==wf.open(W+'/jobs/'+job+'/'+name).read();(folder/name).write_bytes(raw);sdk[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bridge_return_bytes_exact=True)
  v=dict(epoch=time.time(),actual_publisher=actual,reports=reports,SDK_result=res,SDK_return_files=sdk,no_remote_mutation=True)
  (R/'D9_PUBLICATION_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(epoch=v['epoch'],publisher=actual,state=reports.get('REVIEW_STATE.json') or reports.get('STATE.json'),attention=reports.get('REVIEW_ATTENTION.json') if 'REVIEW_STARTED.json' in reports else reports.get('ATTENTION.json'),SDK_phase=(res or {}).get('phase'),SDK_errors=(res or {}).get('errors'),interface_proof=reports.get('D9_NOMINAL_ACTUAL_SDK_REVIEW.json'),published=bool(reports.get('PUBLISHED.json')))))
finally:w.close();n.close()
