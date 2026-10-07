"""Read-only source/authority/ledger evidence for the SCUT threshold audit."""
from pathlib import Path
import sys,json,hashlib,time

D=Path(__file__).resolve().parent;R=D/'evidence';R.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
N='/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007'
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
T='/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007'
def sha(raw):return hashlib.sha256(raw).hexdigest()
c=connect()
try:
    s=c.open_sftp();files=[]
    def get(remote,local):
        with s.open(remote,'rb') as f:raw=f.read()
        out=R/local;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
        files.append(dict(remote=remote,local=local,sha256=sha(raw),bytes=len(raw)))
        return raw
    freeze=json.loads(get(N+'/reports/SOURCE_FREEZE.json','current/SOURCE_FREEZE.json'))
    keys=freeze['sha256']
    exact_names={'mod4_task.py','physics_clock.py','scut_curriculum_gate_v4.py','world_progress_contract.py','train_sensor_resume_ppo.py','supervise_sensor_stable_continuation.py','supervise_sensor_parallel_continuation.py','sensor_a0_runtime.py','train_sensor_ppo.py'}
    selected=[]
    for name,h in keys.items():
        if Path(name).name in exact_names or ('clock' in name.lower() and any(x in name.lower() for x in ('health','monitor','hook'))):
            raw=get(N+'/'+name,'current/source/'+name);assert sha(raw)==h,name
            selected.append(name)
    for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','S1A_ARCHITECTURE_SELECTION.json'):
        get(E+'/reports/'+name,'plan/'+name)
    get(E+'/reports/LATEST_HANDOFF.md','plan/LATEST_HANDOFF.md')
    for name in ('SENSOR_STABLE_STATE.json','PARALLEL_STARTED.json','ASYNC_CURRENT_REVIEW.json'):
        get(N+'/reports/'+name,'current/'+name)
    get(T+'/reports/SENSOR_STABLE_COMPLETE.json','prior/SENSOR_STABLE_COMPLETE.json')
    for kind in ('flat','spin','world'):
        job='clk1000-s2complete-20-stable-'+kind
        for name in ('probe.json','result.json'):
            get(E+'/eval_results/'+job+'/'+name,'returned/'+kind+'/'+name)
        get(E+'/eval_queue/'+job+'.json','returned/'+kind+'/job.json')
    canonical='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
    with s.open(canonical,'rb') as f:raw=f.read()
    b=json.loads(raw);now=time.time()
    rows=[x for x in b['completed_segments'] if 'moe_S2' in x.get('kind','')]
    ledger=dict(observed_epoch=now,canonical_sha256=sha(raw),authorized_seconds=b['authorized_training_seconds'],charged_seconds=b['charged_training_seconds'],active_segment=b.get('active_segment'),S2_completed_segments=rows,read_only=True)
    (R/'S2_LEDGER_OBSERVED.json').write_text(json.dumps(ledger,indent=2))
    if b.get('active_segment'):
        pid=b['active_segment']['pid']
        for f in ('stat','cmdline'):get('/proc/'+str(pid)+'/'+f,'current/proc_'+f)
    s.close()
    v=dict(observed_epoch=now,source_count=len(keys),selected_sources=selected,files=files,active_segment=b.get('active_segment'),no_GPU_probe=True,no_runtime_or_budget_mutation=True)
    (R/'COLLECTION.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in ('observed_epoch','source_count','selected_sources','active_segment','no_GPU_probe','no_runtime_or_budget_mutation')}))
finally:c.close()
