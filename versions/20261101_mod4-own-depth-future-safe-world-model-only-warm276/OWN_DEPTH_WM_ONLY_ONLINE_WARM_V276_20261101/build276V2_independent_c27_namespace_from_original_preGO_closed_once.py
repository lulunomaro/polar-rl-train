from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;V=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V2_20261101'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
closed=N/'reports/ROOT276_ACTUAL_PREGO_EMPTY_GO_CLOSED_AND_C27_RESOURCE_RETURNED.json';c=read(closed)
assert c['passed']and c['original_owner_node_OUT']and c['original_empty_GO']and c['canonical_None']and c['original_no_fee_segment']and c['candidate_passed']and c['candidate_probe_locks_released']
oldindex=N/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json';assert H(oldindex)=='0187a4065664644755300dddbf23d23946074efb6980196d314433805ada6686'
V.mkdir(exist_ok=False);files=[]
for r in read(oldindex)['files']:
 p=Path(r['path']);assert p.stat().st_size==r['bytes']and H(p)==r['SHA'];q=V/p.relative_to(N);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());files.append(q)
task=read(V/'TASK276_FROZEN.json');stamp=str(time.time_ns());base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_OWN_DEPTH_WM_ONLY_WARM276V2_'+stamp
task.update(run_id='OWN_DEPTH_WM_ONLY_WARM276V2_'+stamp,job_root=base+'/warm72',owner_root=base+'/owner72',GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',generation='SOURCE276V2_C27_FROZEN_BEFORE_GO')
(V/'TASK276_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
proof=V/'reports/ROOT276V2_ONLY_NEW_C27_RUN_TASK_METADATA_BEFORE_USE.json'
with proof.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=True,source_index_SHA=H(oldindex),original_preGO45pct_resource_rejection_preserved=True,original_no_GO_SDK_model_optimizer_or_fee=True,original_empty_GO_closure_receipt=str(closed),different_c27_once_resource=c['different_candidate_GPU_line'],candidate_probe_RELEASED_not_production_held=True,source_worker_controls_learner_unchanged=True,only_Task_run_roots_GPU_generation_changed=True,old_entry_not_replayed=True,no_grant=True),f,indent=2)
files +=[proof,oldindex,closed,Path(__file__).resolve()]
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
idx=V/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='FROZEN_WM_ONLY276V2_NEW_C27_RUN_AFTER_ORIGINAL_PREGO_CLOSED',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=H(idx),path=str(V),run_id=task['run_id'])))
