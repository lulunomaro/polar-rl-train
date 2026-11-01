from pathlib import Path
import ast,copy,hashlib,importlib.util,json,time,types
N=Path(__file__).resolve().parent;T=N.parent;V=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
cpath=N/'reports/ROOT276V2_RECEIPT_FAILURE_ALL_CLOSED_ONE_ORIGINAL_RAW_FEE_RETURNED_ACTUAL.json';closed=read(cpath);assert closed['passed']and closed['original_owner_node_worker_all_OUT']and closed['canonical_None']and closed['one_actual_WM_update_before_receipt_failure']and not closed['qualified_formal']
old=N/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json';assert H(old)=='f9e5d6a85d5c4baa36e55c5125422d680e30e65de50f46f501e4d6560649b3dd'
V.mkdir(exist_ok=False);files=[]
for r in read(old)['files']:
 p=Path(r['path']);assert p.stat().st_size==r['bytes']and H(p)==r['SHA']
 if p.is_relative_to(N):q=V/p.relative_to(N);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());files.append(q)
 else:files.append(p)
wp=V/'source/worker276_online_WM_only.py';text=wp.read_text('utf8');needle="    receipt['actual_resource_admission_SHA']=TASK['actual_resource_admission_SHA']\n"
insert="    native_proof=json.loads((OUT/'NATIVE24_WM_WARM276_ACTUAL.json').read_bytes())\n    receipt['native24_before_first_WM_step_passed']=bool(native_proof['passed']and native_proof['controls']==24 and native_proof['physics_callbacks']==192 and native_proof['feedback_samples']==48 and native_proof['WM_updates']==0 and native_proof['teacher_updates']==0)\n"
assert text.count(needle)==1;text=text.replace(needle,needle+insert);ast.parse(text);wp.write_text(text,encoding='utf8')
stamp=str(time.time_ns());base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_OWN_DEPTH_WM_ONLY_WARM276V3_'+stamp;task=read(V/'TASK276_FROZEN.json');task.update(run_id='OWN_DEPTH_WM_ONLY_WARM276V3_'+stamp,job_root=base+'/warm72',owner_root=base+'/owner72',worker_SHA=H(wp),generation='SOURCE276V3_NATIVE24_RECEIPT_FIX_FROZEN_BEFORE_GO',prior276V2_teacher_read_decode_consumed=1,prior276V2_partial_WM_updates=1,prior_partial_not_promoted_or_input=True,new_teacher_read_decode_purpose='Complete live WM warm after original receipt-only refusal; frozen policy preserved; fresh WM explicit new trial')
(V/'TASK276_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
s=importlib.util.spec_from_file_location('root276v3_receipt_source_fixture',V/'control276/wm_task275.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.validate_task(task)
# New worker-receipt integration fixture only; no old fixture entry is replayed.
now=time.time();first=dict(closed['partial_checkpoint_metadata_only'],path='/SOURCE_ONLY_METADATA_FIXTURE/model.pt',save_epoch=now+1,epoch=now+1)
go=dict(m.flat_go_fields(task),run_id=task['run_id'],source_SHA=task['source_SHA'],source_CPU_SHA='a'*64,source_qualification_kind=m.READY_KIND,manifest_SHA='b'*64,max_parent_seconds=3900,exit_headroom_seconds=300,learning_started_epoch=now,save_deadline=now+3600,nominal_end_epoch=now+3900)
tree=ast.parse(text);expr=next(x.value for x in ast.walk(tree)if isinstance(x,ast.Assign)and any(isinstance(y,ast.Name)and y.id=='receipt'for y in x.targets)and isinstance(x.value,ast.Call)and any(k.arg=='first_complete'for k in x.value.keywords))
value=eval(compile(ast.Expression(expr),'<NEW276V3_SOURCE_ONLY_WORKER_RECEIPT_FIXTURE>','eval'),dict(time=time,TASK=task,FIRST_KIND=m.FIRST_KIND,controls=32,diagnostic=dict(source_only=True),first=first))
value['actual_resource_admission_SHA']='c'*64;value['native24_before_first_WM_step_passed']=True;assert m.validate_first(value,task,go)
bad=copy.deepcopy(value);bad.pop('native24_before_first_WM_step_passed');refused=False
try:m.validate_first(bad,task,go)
except ValueError:refused=True
assert refused
report=V/'reports/ROOT276V3_NEW_WORKER_RECEIPT_POSITIVE_AND_MISSING_NATIVE24_REJECT_CPU.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),new_source_metadata_positive=1,missing_native24_rejection=1,synthetic_metadata_fixture_not_actual_GO_or_FIRST=True,old_fixtures_replayed=0,original275_protocol_unchanged=True,algorithm_reward_terrain_physics_controls_unchanged=True,only_worker_receipt_native24_proof_added=True,original276V2_one_WM_update_partial_preserved=True,original_fee_SUMONCE=closed['original_raw_fee_SUMONCE'],model_raw_Torch_SDK_GPU_remote_optimizer=0),f,indent=2)
files +=[report,cpath,old,Path(__file__).resolve()]
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
idx=V/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='FROZEN276V3_NATIVE24_RECEIPT_ONLY_REPAIR_NEW_TRIAL',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=H(idx),path=str(V),run_id=task['run_id'])))
