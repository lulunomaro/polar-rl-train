"""After allthree actualcleanPass seal raw/source/errors, no extraPT/binary I/O."""
from pathlib import Path
import hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;C=T/'E1_three_variants_CPU_actual_v1';NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc'}

def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 progress=json.loads((B/'SEQUENTIAL_VARIANT_PROGRESS_V1.json').read_bytes());assert progress['rows'][-1]['status']=='ALL_THREE_ACTUAL_PROTOCOL_PASS_NOT_SKILL';rows=[];files={};binaries=[]
 def add(p):
  if p.suffix.lower() in NO:return
  raw=p.read_bytes();files[str(p)]=dict(path=str(p),bytes=len(raw),SHA=H(raw))
 for folder in [B,C]:
  for p in folder.rglob('*'):
   if p.suffix.lower() in NO:continue
   if p.is_file():add(p)
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  p=T/(name+'_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_HANDOFF_V1.json');r=json.loads(p.read_bytes());add(p);rows.append(dict(variant=name,handoff=str(p),SHA=H(p.read_bytes()),original_source_SHA=r['original_source_SHA'],typed=r['new_typed_source'],core_treeSHA=r['core_before_after_treeSHA'],source_counts=r['source_counts'],extra_actual=r['extra_actual_resume_receipt'],actual_GPU_UUID=r['actual_GPU_UUID'],closewaitrelease=r['closewait_originalEX_finiteSH_release'],not_skill_graduation=True))
  assert r['closewait_originalEX_finiteSH_release']['all_partialleases_released'] and not r['closewait_originalEX_finiteSH_release']['errors'];binaries.append(dict(variant=name,kind='TYPED_PT_METADATA_NO_REREAD',**r['new_typed_source']))
  # Exact case rawJSON/log directories from actualhandoff; no unrelatedreports.
  for col in [r['fresh_collection'],r['native_collection']]:
   for p in Path(col).parent.rglob('*'):
    if p.suffix.lower() in NO:continue
    if p.is_file():add(p)
  # Allown dispatch/watch/CPUtransport reports for thisexplicitvariant.
  for p in (T/'reports').glob(name+'_*'):
   if p.suffix.lower() in NO:continue
   if p.is_file():
    add(p)
    if p.name.startswith(name+'_GPU1_fresh80_dispatch_'):
     st=json.loads(p.read_bytes());binaries.append(dict(variant=name,kind='ACTUAL_NONPT_ZIP_METADATA',**st['archive']))
     for row in st.get('files',[]):
      if Path(row['relative']).suffix.lower() in NO:binaries.append(dict(variant=name,kind='ACTUAL_ORIGINAL_NPZ_OR_NEWASSET_METADATA',path=row['local_dependency_path'],relative=row['relative'],bytes=row['bytes'],SHA=row['sha256']))
 summary=T/'THREE_EXPLICIT_E1_VARIANTS_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_HANDOFF_V1.json'
 with summary.open('x',encoding='utf-8') as f:json.dump(dict(kind='THREE_EXPLICIT_VARIANTS_ACTUAL_PROTOCOL_PASS_NOT_FULL_HISTORY_OR_SKILL',rows=rows,protected878_scope='ONLYoriginalrank0 complete20kshard; historicalworld3/60k contract preserved, noNCCL/merge/fork/all60kclaim',indCURB113='G3sibling not878continuation; savedreset_direction originalwriter actual',indSlope50='Ownfullramp/bothsupports storedaxis actual',all_source_physical_byte_SHA_decodes_one_per_newpurpose=True,CPU_fourleaf_inverse_and_roundtrip_exact=True,SDK_cache_alreadytyped_migration_calls_zero=True,all_Core_STD17Adam_LRiteration_beforeafter_exact=True,all_8original_plus_OWNextra_load_and_one_reset_verified=True,all_24ctrl192phys48feedback_passed=True,all_original_GPU1_EX_finiteSH_closewait_released=True,no_GPU0_or_foreignstudent_or_W35_scope_touched=True,no_canonical_or_productionGO_PPO_or_newbudget=True,birthinertia_fullhardwareDR_skill_or_fullhistory_graduation=False,original7b_network_asset_still_pending=True,all_sourceonly_seals_and_originalerrors_preserved=True,parent_Gitpending=True,child_commit_push=False),f,indent=2)
 add(summary)
 index=T/'THREE_EXPLICIT_E1_VARIANTS_ACTUAL_ALL_SOURCE_RAW_ERRORS_ARCHIVE_PENDING_V1.json'
 with index.open('x',encoding='utf-8') as f:json.dump(dict(kind='COMPLETE_THREE_EXPLICIT_VARIANT_CPU_GPU_ACTUAL_ALL_RAW_ERRORS_SOURCE_ARCHIVE_PENDING',files=list(files.values()),binary_paths_bytes_SHA_only_no_extra_reads=binaries,sourceonly_V1partial_V2final_archive_index=str(T/'THREE_FROZEN_E1_VARIANTS_SOURCEONLY_ALL_V1_ERRORS_V2_SOURCEFINALS_ARCHIVE_PENDING_v1.json'),sourceonly_index_SHA='5f933cae819471f4b3736e55860a6f792954c30c7302f72587f5b5f3fe5228b5',actual_CPU_archive_index=str(T/'THREE_FROZEN_VARIANTS_ACTUAL_CPU_ALL_ERRORS_ARCHIVE_PENDING_V1.json'),actual_CPU_index_SHA='f80151d797d490b2c56bf63de4483303f9cccc17a29c42b1680a686779f792a2',all_six_actualcases_cleanclosewait_resourceleases_released=True,all_original_lookup_and_readererrors_preserved=True,current_binary_or_sourcePT_stat_hash_read_decode_for_archive=0,parent_appendonly_Gitpending=True,child_commit_push=False),f,indent=2)
 print(json.dumps(dict(handoff=str(summary),handoff_SHA=H(summary.read_bytes()),archive_index=str(index),archive_index_SHA=H(index.read_bytes()),text_source_raw_error_files=len(files),actual_variants=3,all_own_SDK_closed=True),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('ALL_ACTUAL_SEAL_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
