"""LOCAL226 source hash/AST/saved metadata join sealing only."""
from pathlib import Path
import argparse,ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
ID='NEW226_E2_QUALIFIED_SAVED_JSON_AND_SOURCE_GRAPH_METADATA_JOIN_V1'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','AST','seal'));a=p.parse_args();R.mkdir(exist_ok=True)
 if a.mode=='freeze':
  names=('prepare226_E2_QUALIFIED_SOURCE_JOIN.py','probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py','finalize226_E2_TASK_FROM_ACTUAL_METADATA_UNUSED.py')
  put(R/'LOCAL226_PURPOSE_FROZEN.json',dict(purpose_id=ID,frozen_epoch=time.time(),source_files=[ref(N/x) for x in names],
   scope='AST and actual saved-qualified JSON/source table join only;no behavioral/old213 fixture',model_asset_raw_SDK_GPU_SSH_Git_reads_or_calls=0))
  put(R/'LOCAL226_JOIN_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=ID,no_old_once_or_fixture_replay=True))
  print(json.dumps(dict(source_metadata_purpose_frozen=True,model_reads=0)));return
 if a.mode=='AST':
  f=json.loads((R/'LOCAL226_PURPOSE_FROZEN.json').read_bytes())
  for r in f['source_files']:
   b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA'];ast.parse(b.decode('utf8'))
  probe=(N/'probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py').read_text(encoding='utf8')
  tree=ast.parse(probe)
  assert not any(isinstance(x,(ast.Import,ast.ImportFrom)) and any(y.name in ('torch','pxr','isaaclab','isaacsim') for y in getattr(x,'names',[])) for x in ast.walk(tree))
  join=json.loads((R/'QUALIFIED226_SAVED_JSON_SOURCE_JOIN_ACTUAL.json').read_bytes());assert join['passed_saved_metadata_join']
  put(R/'LOCAL226_METADATA_JOIN_AST_ACTUAL.json',dict(epoch=time.time(),purpose_id=ID,passed_source_metadata=True,
   qualified_saved_JSON_join=True,source_AST_files=3,old213_fixture_replays=0,
   Torch_Actor_SDK_scene_model_asset_raw_SSH_Git_calls=0,actual_target_metadata='EXPLICIT_PENDING_ROOT'))
  print(json.dumps(dict(passed_source_metadata=True,model_or_actualSDK_reads=0)));return
 actual=json.loads((R/'LOCAL226_METADATA_JOIN_AST_ACTUAL.json').read_bytes());assert actual['passed_source_metadata']
 put(R/'SOURCE226_READER_ERRORS_AND_TARGET_PENDING.json',dict(
  notes=[dict(id='SOURCE226_EXPERT_ARRAY_SELECTOR',result='First saved189 reader treated experts as mapping and printed null;correct213 normalized experts array used,not a model change'),
   dict(id='SOURCE226_V5_MANIFEST_OUTPUT_CLIP',result='Source metadata selection output clipped;followed by exact narrow original_run_manifest/CPU/source fields'),
   dict(id='SOURCE226_BROAD_SOURCE_JSON_RG_CLIP',result='Broad source/json rg matched large embedded metadata strings and clipped output;no raw trajectory/model/NPZ was opened;subsequent exact files only')],
  old_source_false_and_consumed_once_unchanged=True,actual_target_metadata_wait_resource_link_and_fullcase='EXPLICIT_PENDING_ROOT',
  no_guessed_PID_GPU_or_source_model_SHA=True,all_files_pending_root_Git=True))
 files=[]
 for p in sorted(N.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md','.txt') and not p.name.endswith(('.partial','.active'))
  r=ref(p);r['relative']=str(p.relative_to(N)).replace('\\','/');files.append(r)
 value=dict(schema='mod4.226.E2_qualified_metadata_Task_source_index.v1',frozen_epoch=time.time(),files=files,file_count=len(files),
  status='QUALIFIED_SAVED_JSON_JOIN_SOURCE_READY_TARGET_METADATA_AND_GPU_CASE_PENDING_ROOT',
  selected213_worker_unchanged=True,model_or_asset_raw_Torch_SDK_GPU_SSH_Git_calls=0,old213_fixture_replays=0,
  no_actor_PPO_or_new_learning_GO=True,full_E2_skill=False,full_SuperMimic=False,Git_status='PENDING_ROOT_NEXT_UNIFIED_ARCHIVE')
 path=N/'INDEX226_FROZEN.json';put(path,value)
 print(json.dumps(dict(INDEX=ref(path),files=len(files),source_side_ready=True,actual_target_metadata=False)))
if __name__=='__main__':main()
