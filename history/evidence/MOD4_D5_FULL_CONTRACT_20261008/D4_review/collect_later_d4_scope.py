"""Read existing b2/b3 results; no GPU, publication or budget writes."""
from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from remote_io import connect
from eval_remote_io import connect_eval
native=connect();evaluator=connect_eval();prefix='clk2500-closure-episode-d3-'
labels=[f'50-d4-b{b}-{k}' for b in (2,3) for k in ('flat','spin')]+[f'55-d4world-b{b}-world' for b in (2,3)]
try:
    rows=[];pending=[]
    with native.open_sftp() as n,evaluator.open_sftp() as w:
        central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
        for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','NEXT_D5_FORCE_STROKE_WORK_ORDER.json'):
            (R/('ACTUAL_'+name)).write_bytes(n.open(central+'/'+name).read())
        a=json.loads((R/'ACTUAL_PLAN_APPROVAL.json').read_text(encoding='utf8'))
        assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
        for label in labels:
            job=prefix+label;wp='D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+job
            np='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results/'+job
            try:w.stat(wp+'/complete.json');n.stat(np+'/probe.json');n.stat(np+'/result.json')
            except FileNotFoundError:pending.append(job);continue
            folder=R/'windows'/job;folder.mkdir(parents=True,exist_ok=True);files={}
            for name in ('manifest.json','complete.json','probe.json','result.json'):
                raw=w.open(wp+'/'+name).read();returned=name in ('probe.json','result.json')
                if returned:assert raw==n.open(np+'/'+name).read()
                (folder/name).write_bytes(raw);files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),automatic_bridge_return_bytes_exact=returned if returned else None)
            result=json.loads((folder/'result.json').read_text(encoding='utf8'))
            assert result['exit_code']==0 and not result['errors'] and not result['error_files']
            rows.append(dict(id=job,files=files,result=result))
    v=dict(epoch=time.time(),jobs=rows,pending=pending,no_GPU_PPO_publication_or_budget_write=True)
    (R/'LATER_D4_SCOPE_FILES.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(complete=[r['id'] for r in rows],pending=pending,returned_JSON_byte_exact=2*len(rows))))
finally:evaluator.close();native.close()
