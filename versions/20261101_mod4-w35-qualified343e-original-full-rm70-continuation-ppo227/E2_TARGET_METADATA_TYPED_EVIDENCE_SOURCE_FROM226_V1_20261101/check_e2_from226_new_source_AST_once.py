"""New interface AST/read-scope checks only. No old probe/fixture execution."""
from pathlib import Path
import ast,hashlib,json,time,traceback

N=Path(__file__).resolve().parent


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 purpose=json.loads((N/'reports/LOCAL_E2_FROM226_SOURCE_PURPOSE_FROZEN.json').read_bytes())
 put(N/'reports/LOCAL_E2_FROM226_SOURCE_ONCE_CONSUMED.json',dict(ID=purpose['ID'],epoch=time.time()))
 trees={};texts={}
 for r in purpose['sources']:
  b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
  name=Path(r['path']).name;trees[name]=ast.parse(b);texts[name]=b.decode('utf8')
 entry=trees['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py']
 child=[ast.literal_eval(n.value) for n in entry.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHILD_CODE' for t in n.targets)]
 assert len(child)==1;ast.parse(child[0])
 c=texts['contract_e2_from226.py'];runner=texts['run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py'];final=texts['finalize_e2_from226_actual_evidence_ROOT_ONLY.py']
 assert "mode=='FRESH_CNONE'" in c and "mode=='EXACT227D_ACTIVE'" in c and "'227D' in expected['run_id']" in c
 assert "current['go']==expected['go']" in c and "c['active_segment']['owner_parent_pid']" in c
 assert "current['checked_epoch']>=wait_finished" in c and "value['GPU_UUID'] not in current['active_GPU_UUIDs']" in c
 assert 'original_private_EX_held' in c and "link['model_byte_reads_or_copies']==0" in c
 constants={n.targets[0].id:ast.literal_eval(n.value) for n in trees['contract_e2_from226.py'].body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)}
 base=N.parent/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101'
 for key,path in [('EXPECTED',base/'source_payload226/EXPECTED226_TARGET_METADATA.json'),('PENDING_TASK',base/'source_payload226/FROZEN_CASE_TASK_PENDING226.json'),('PROBE',base/'probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'),('WORKER',N.parent/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101/source/evaluate_e2_world213.py')]:
  assert hashlib.sha256(path.read_bytes()).hexdigest()==constants[key],key
 assert "CUDA_VISIBLE_DEVICES=''" in runner and "child.wait()" in runner
 assert "METADATA226_ONCE_CONSUMED.json" in runner and 'PROBE' in runner
 assert "if a.actual_runtime_admission:" in final and "canonical72_known_owner_readonly_passed=True" in final
 assert "READY_FROM226_CURRENT_AUTHORITY" in final and "source_SHA" in final
 for name,tree in trees.items():
  # Source helpers may mention Torch/SDK as text; none is imported by this new interface.
  for n in ast.walk(tree):
   if isinstance(n,ast.Import):assert all(x.name.split('.')[0] not in ('torch','pxr','isaacsim','isaaclab','paramiko') for x in n.names),name
   if isinstance(n,ast.ImportFrom):assert (n.module or '').split('.')[0] not in ('torch','pxr','isaacsim','isaaclab','paramiko'),name
 put(N/'reports/LOCAL_E2_FROM226_SOURCE_AST_ACTUAL.json',dict(passed=True,ID=purpose['ID'],
  source_AST_count=len(trees),embedded_child_AST_count=1,frozen_source_contract_hashes_checked=4,authority_modes=['EXACT227D_ACTIVE','FRESH_CNONE'],
  real_authority_resource_report_wait_or_Task_generated=False,ROOT_target_metadata_execution='PENDING',
  original213_worker_and226_probe_modified=False,old_probe_or_fixture_replays=0,
  PT_NPZ_USD_actualraw_Torch_SDK_GPU_network_Git_calls=0,actual_E2_24s_or_fullskill='PENDING'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/LOCAL_E2_FROM226_SOURCE_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_automatic_retry=True));raise
