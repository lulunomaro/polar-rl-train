from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 old=T/'H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026/reports/CURRENT_SOURCE_ONLY86_NATIVE_PHASE_COVERAGE_MONITOR_SOURCE_ACTUAL.txt'
 with (R/'PREVIOUS_SOURCE_ONLY86_AND_CLOSED85_MONITOR_HISTORICAL.txt').open('xb') as f:f.write(old.read_bytes())
 rows=[];unmapped=[]
 for stage in (T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026',N):
  for model in stage.rglob('*.pt'):
   st=model.stat();found=None
   for parent in model.parents:
    if not parent.is_relative_to(stage):break
    manifest=parent/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
    if manifest.is_file():
     obj=json.loads(manifest.read_bytes());match=[r for r in obj['files'] if r['relative']==model.relative_to(parent).as_posix()]
     if match and match[0]['bytes']==st.st_size:
      found=dict(path=str(model),bytes=st.st_size,SHA=match[0]['SHA'],existing_producer_manifest=str(manifest),producer_relative=match[0]['relative'],no_model_content_read_for_Git=True,not_new_local_fullSHA_claim=True)
     break
   if found:rows.append(found)
   else:unmapped.append(dict(path=str(model),bytes=st.st_size,SHA=None,unknown_preserved=True,no_model_read_for_Git=True))
 put('ALL_NEW86_LOCAL_MODEL_COPIES_EXISTING_MANIFEST_PRODUCER_INDEX_ACTUAL.json',dict(epoch=time.time(),entries=rows,unmapped=unmapped,no_binary_read_hash_or_GPU=True))
 # Compile root wrapper/transport source only. The actual once entries remain UNUSED.
 paths=[N/'close_actual_three86B_original_cost_fixed_paths_unused_once.py',N/'review_actual_three86B_typed_fullstate_fixed_paths_CPU_unused_once.py',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v178.py']
 for p in paths:ast.parse(p.read_bytes(),filename=str(p))
 put('ROOT86B_PREARCHIVE_SOURCE_AND_BINARY_METADATA_ONLY_ACTUAL.json',dict(epoch=time.time(),compiled_source_paths=list(map(str,paths)),mapped_model_copies=len(rows),unknown_model_copies=len(unmapped),closing_and_reviewer_not_executed=True,old_monitor_saved_as_history=True,no_remote_or_model_content_read=True))
 print(json.dumps(dict(passed=True,mapped_model_copies=len(rows),unknown_model_copies=len(unmapped))))
if __name__=='__main__':main()
