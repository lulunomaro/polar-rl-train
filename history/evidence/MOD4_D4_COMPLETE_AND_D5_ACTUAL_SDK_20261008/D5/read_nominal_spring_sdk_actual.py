"""Read the actual frozen nominal SDK job and returned bytes, never starts work."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from eval_remote_io import connect_eval
from remote_io import connect
job='clk2500-closure-episode-d3-65-d5-nominal-spring-sdk'
root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
native='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results'
c=connect_eval();n=connect()
try:
    with c.open_sftp() as w,n.open_sftp() as f:
        def optional(path):
            try:return json.loads(w.open(path).read())
            except FileNotFoundError:return None
        res=optional(root+'/jobs/'+job+'/result.json');complete=optional(root+'/jobs/'+job+'/complete.json')
        value=dict(epoch=time.time(),job=job,result=res,complete=bool(complete),
                   attention=optional(root+'/WORKER_ATTENTION.json'),new_GPU_PPO_budget_operations=0)
        if complete and res:
            folder=R/'windows'/job;folder.mkdir(parents=True,exist_ok=True);hashes={}
            for name in ('manifest.json','complete.json','result.json','probe.json'):
                try:raw=w.open(root+'/jobs/'+job+'/'+name).read()
                except FileNotFoundError:continue
                (folder/name).write_bytes(raw);exact=None
                if name in ('probe.json','result.json'):
                    try:returned=f.open(native+'/'+job+'/'+name).read()
                    except FileNotFoundError:returned=None
                    if returned is not None:assert returned==raw;exact=True
                hashes[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),bridge_return_exact=exact)
            value['files']=hashes
            log=w.open(root+'/jobs/'+job+'/probe.log').read().decode(errors='replace')
            if res['exit_code']!=0:
                value['last_error_log']=log[-5000:]
            else:
                p=json.loads((folder/'probe.json').read_text(encoding='utf8'));a=p.get('D5_nominal_spring_actual_SDK')
                value['nominal_sdk_audit_present']=bool(a)
                if a:value['summary']={k:v for k,v in a.items() if k!='per_physical_write'}
                value['actual_write_delta']=p.get('D5_nominal_spring_physical_write_delta')
                value['actual_callback_delta']=p.get('actual_physics_callback_delta')
        (R/'NOMINAL_SPRING_SDK_CURRENT_ACTUAL.json').write_text(json.dumps(value,indent=2),encoding='utf8')
        print(json.dumps(value))
finally:n.close();c.close()
