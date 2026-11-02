"""Full exact localtext/raw metadata phase7 index; GPU/PT now paused. No SSH/Git."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;R=T/'reports';files={}
NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc'}
def add(p):
 if p.suffix.lower() in NO:return
 raw=p.read_bytes();files[str(p)]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
for p in B.rglob('*'):
 if p.suffix.lower() in NO:continue
 if p.is_file():add(p)
for name in ['E1_exact_sources_stat_locator_20261102_052800.json','E1_exact_sources_metadata_v2_20261102_053143.json','SLOPE135_transport_CPU_actual_20261102_053246_1793568766422620900.json','SLOPE135_fresh80_stage_dispatch_20261102_053913_1793569153385376500.json','SLOPE135_gpu1_waiter_gpu0_permission_metadata_20261102_054215.json','SLOPE135_GPU0_fresh80_newcase_v2_20261102_054329_1793569409621031000.json','SLOPE135_GPU0_N20K_dispatch_20261102_054609_1793569569538362900.json','CURB141_exact_original_metadata_retry_v3_20261102_054948.json','CURB141_same_project72_tunnel_stat_v4_20261102_055111.json','SLOPE135_own_terminal_watch_20261102_054715.json']:add(R/name)
for name in ['SLOPE135_actual_case_collect_20261102_054419','SLOPE135_actual_case_collect_20261102_054541','SLOPE135_actual_case_collect_20261102_055450']:
 for p in (R/name).rglob('*'):
  if p.suffix.lower() in NO:continue
  if p.is_file():add(p)
for name in ['SLOPE135_ACTUAL_PROTOCOL_PASS_CURB141_NETWORK_PENDING_HANDOFF_v1.json','E1_ACTUAL_CPU_SLOPE_PROTOCOL_AND_ALL_ERRORS_ARCHIVE_PENDING_v1.json']:add(T/name)
cpu=json.loads((B/'SLOPE135_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').read_bytes());stage=json.loads((R/'SLOPE135_fresh80_stage_dispatch_20261102_053913_1793569153385376500.json').read_bytes());binaries=[dict(kind='OriginalsourceCPUcopy_evidence_only',**cpu['original_source']),dict(kind='Newtypedcomplete20k_evidence_only',**cpu['new_typed_source']),dict(kind='NonPTstageZIP_evidence_only',**stage['archive'])]
for x in stage['files']:
 if Path(x['relative']).suffix.lower() in NO:binaries.append(dict(kind='ActualNonPTdependencySHA_evidence_only',path=x['local_dependency_path'],relative=x['relative'],bytes=x['bytes'],SHA=x['sha256']))
p=T/'E1_ACTUAL_CPU_SLOPE_PROTOCOL_AND_ALL_ERRORS_ARCHIVE_PENDING_v2.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(kind='COMPLETE_PHASE7_ACTUAL_E1_ALL_RAW_ERRORS_AND_SOURCE_ARCHIVE_PENDING',files=list(files.values()),binary_evidence_paths_bytes_SHA_only=binaries,PT_binary_extra_stat_hash_read_decode_in_index=0,all_SLOPE_CPU_fresh_native_completed_no_SDK_replay=True,CURB141_network_and_savedmirror_condition_pending_not_missing=True,oldGPU1_zeroSDK_waiter_cancelled_ownPID_only=True,all_CPU_metadata_reader_failures_including_V1seal_SyntaxError_preserved=True,all_own_children_waited_originalleases_released=True,GPU_PT_SSH_actual_permissions_paused_again=True,no_new_878_113_50_actual_permissions=True,parent_phase6_known_commit='2236f9d9',parent_phase7_append_archive_pending=True,child_Gitcommit_push=False),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(index=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),text_raw_source_files=len(files),binary_evidence_entries=len(binaries),all_own_SDK_closed=True),indent=2))
