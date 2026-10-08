"""Read completed D6 jobs and verify automatic bridge bytes; no replay/restart."""
from pathlib import Path
import sys,json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval();pub='D6_INDEX_REVIEW_SDK_PUBLISHED.json' if (R/'D6_INDEX_REVIEW_SDK_PUBLISHED.json').exists() else 'D6_ACTUAL_DAMPING_SDK_PUBLISHED.json'
jobs=json.loads((R/pub).read_text())['jobs']
try:
    out=dict(epoch=time.time(),jobs={},no_GPU_PPO_publication_budget_or_restart=True)
    with n.open_sftp() as nf,w.open_sftp() as wf:
        root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
        for name in ('GAS_DAMPING_REVIEW_WORKER_STARTED.json','GAS_DAMPING_REVIEW_WORKER_STATE.json','GAS_DAMPING_REVIEW_WORKER_ATTENTION.json'):
            try:out[name]=json.loads(wf.open(root+'/'+name).read())
            except FileNotFoundError:out[name]=None
        for row in jobs:
            job=row['job_id'];wp=root+'/jobs/'+job;np='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results/'+job
            try:wf.stat(wp+'/complete.json');nf.stat(np+'/result.json')
            except FileNotFoundError:out['jobs'][job]=dict(pending=True);continue
            dest=R/'windows'/job;dest.mkdir(parents=True,exist_ok=True);info={}
            for name in ('manifest.json','complete.json','result.json'):
                raw=wf.open(wp+'/'+name).read();(dest/name).write_bytes(raw);info[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
                if name=='result.json':assert raw==nf.open(np+'/'+name).read()
            result=json.loads((dest/'result.json').read_text(encoding='utf8'))
            if result['phase']=='complete':
                raw=wf.open(wp+'/probe.json').read();assert raw==nf.open(np+'/probe.json').read();(dest/'probe.json').write_bytes(raw)
                info['probe.json']=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw));out['jobs'][job]=dict(pending=False,result=result,files=info,bridge_bytes_exact=True)
            else:
                try:log=wf.open(wp+'/probe.log').read().decode(errors='replace')[-6000:]
                except FileNotFoundError:log=None
                out['jobs'][job]=dict(pending=False,result=result,files=info,last_error_log=log)
    (R/'D6_ACTUAL_DAMPING_SDK_CURRENT.json').write_text(json.dumps(out,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=out['epoch'],jobs={k:dict(pending=v['pending'],phase=v.get('result',{}).get('phase'),error=v.get('last_error_log')) for k,v in out['jobs'].items()},attention=out['GAS_DAMPING_REVIEW_WORKER_ATTENTION.json'])))
finally:w.close();n.close()
