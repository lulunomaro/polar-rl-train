"""Fetch already-completed pressure SDK evidence; never publish or launch."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect_eval();n=connect();root='D:/MOD4_async_eval/closure_episode_clock2500_v15';native='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results'
try:
    with c.open_sftp() as w,n.open_sftp() as f:
        def optional(path):
            try:return json.loads(w.open(path).read())
            except FileNotFoundError:return None
        jobs=[]
        for label in ('00-off','01-on'):
            prefix='67-d5-stiffness-index-sdk-' if (R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json').exists() else '66-d5-stiffness-sdk-'
            job='clk2500-closure-episode-d3-'+prefix+label
            if label=='01-on' and (R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json').exists():
                job='clk2500-closure-episode-d3-68-d5-stiffness-audit-sdk-on'
            res=optional(root+'/jobs/'+job+'/result.json');complete=optional(root+'/jobs/'+job+'/complete.json')
            value=dict(job=job,result=res,complete=bool(complete))
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
                if res['exit_code']!=0 or res['errors'] or not res['result_present']:
                    value['last_error_log']=w.open(root+'/jobs/'+job+'/probe.log').read().decode(errors='replace')[-5000:]
                elif 'probe.json' in hashes:
                    probe=json.loads((folder/'probe.json').read_text(encoding='utf8'))
                    value['adapter_summary']=probe.get('D5_pressure_adapter_actual_SDK')
                    value['actual_contact_callback_delta']=probe.get('actual_physics_callback_delta')
            jobs.append(value)
        audit_worker=optional(root+'/SPRING_AUDIT_WORKER_STARTED.json')
        new_worker=audit_worker or optional(root+'/PRESSURE_DEPENDENCY_WORKER_STARTED.json')
        value=dict(epoch=time.time(),jobs=jobs,new_worker=new_worker,
                   attention=optional(root+'/SPRING_AUDIT_WORKER_ATTENTION.json') if audit_worker else optional(root+'/PRESSURE_DEPENDENCY_WORKER_ATTENTION.json') if new_worker else optional(root+'/WORKER_ATTENTION.json'),
                   historical_previous_worker_attention=optional(root+'/WORKER_ATTENTION.json'),no_GPU_launch_PPO_or_budget_write=True)
        (R/'PRESSURE_SDK_CURRENT_ACTUAL.json').write_text(json.dumps(value,indent=2),encoding='utf8')
        print(json.dumps(value))
finally:n.close();c.close()
