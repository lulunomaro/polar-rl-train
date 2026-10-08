"""Collect already completed D5 frozen results with exact bridge bytes; no new jobs."""
from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();prefix='clk2500-closure-episode-d3-'
try:
 rows=[];pending=[]
 with n.open_sftp() as nf,w.open_sftp() as wf:
  central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
  for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json'):
   (R/('ACTUAL_'+name)).write_bytes(nf.open(central+'/'+name).read())
  for label in ['70-d5-anchor']+[f'75-d5-b{i}' for i in (1,2,3)]:
   for k in ('flat','spin','world'):
    job=prefix+label+'-'+k;wp='D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+job
    np='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results/'+job
    try:wf.stat(wp+'/complete.json');nf.stat(np+'/probe.json');nf.stat(np+'/result.json')
    except FileNotFoundError:pending.append(job);continue
    folder=R/'windows'/job;folder.mkdir(parents=True,exist_ok=True);files={}
    for name in ('manifest.json','complete.json','probe.json','result.json'):
     raw=wf.open(wp+'/'+name).read();returned=name in ('probe.json','result.json')
     if returned:assert raw==nf.open(np+'/'+name).read()
     (folder/name).write_bytes(raw);files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),automatic_bridge_return_bytes_exact=returned if returned else None)
    result=json.loads((folder/'result.json').read_text(encoding='utf8'))
    rows.append(dict(id=job,files=files,result=result))
 v=dict(epoch=time.time(),jobs=rows,pending=pending,no_GPU_PPO_publication_or_budget_write=True)
 (R/'D5_COMPLETED_SCOPE_FILES.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(complete=[r['id'] for r in rows],pending=pending,errors=[r['result'] for r in rows if r['result']['exit_code'] or r['result']['errors'] or r['result']['error_files']],bridge_JSON_exact=2*len(rows))))
finally:w.close();n.close()
