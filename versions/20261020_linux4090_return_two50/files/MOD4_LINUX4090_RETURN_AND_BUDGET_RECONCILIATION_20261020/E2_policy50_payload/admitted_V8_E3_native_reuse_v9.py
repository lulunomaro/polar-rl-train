from pathlib import Path
import os,json,time,hashlib,shutil,psutil
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def admitted_native(cfg):
 import three_expert_helpers_v2 as b
 B=Path(__file__).resolve().parent;A=Path(cfg['admitted_native_root']);assert A.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2').resolve()) and H(A/'CONTINUATION_COMPLETE_MANIFEST_V2.json')==cfg['admitted_manifest_SHA'];m=json.loads((A/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());assert m['source_SHA']==cfg['source_SHA'] and m['GPU_UUID']==cfg['GPU_UUID']
 for r in m['files']:
  if r['relative'].startswith(('job0/runtime/','job0/source/','job0/assets/','lib/')) or r['relative'] in ('recovery_worker.py','native_CPU.py'):
   p=B/r['relative'];assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 for p in psutil.process_iter(['pid','cmdline']):
  try:assert not any(str(A)+'/' in a for a in p.info['cmdline'] or [])
  except psutil.Error:pass
 assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['validation_fcntl_released'];old=json.loads((A/'NODE_ORIGINAL_ERROR.json').read_bytes());assert "Source finite stop before new learning" in old['error']
 for name in ('native_WAITED_EXIT_ACTUAL.json','native_CPU_WAITED_EXIT_ACTUAL.json'):assert json.loads((A/'job0'/name).read_bytes())['returncode']==0
 own=json.loads((B/'OWN_GPU_SPECIFIC_FCNTL_AND_GLOBAL_FREE_ACTUAL.json').read_bytes());assert own['pid']==os.getpid() and own['GPU_UUID']==cfg['GPU_UUID'] and own['actual_private_GPU_fcntl_held'];O=A/'job0/native';p=O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json';v=json.loads(p.read_bytes());c=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert H(p)==cfg['admitted_CPU_SHA'] and v['passed'] and v['source_SHA']==cfg['source_SHA'] and v['controls']==336 and v['callbacks']==1344 and v['all_original_core_tensor_bytes_exact'];assert c['optimizer_updates']==0 and c['Adam_step']==640240 and H(O/'own_native336.pt')==c['SHA']==v['native_checkpoint_SHA'];target=B/'job0/native';assert not target.exists();target.mkdir()
 for name in ('own_native336.pt','own_startup0.pt','NATIVE336_COMPLETE.json','NATIVE_ALL_ROWS_CPU_ADMITTED.json','FINAL.json','GEOMETRY_AND_RESET_ACTUAL.json','VALID_PREFIX_INDEX.json','SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json'):shutil.copy2(O/name,target/name)
 b.put(B/'V8_COMPLETE_NATIVE_ACTUAL_REUSED_NO_GPU_REPLAY.json',dict(epoch=time.time(),original_root=str(A),source_SHA=cfg['source_SHA'],original_complete_native_SHA=c['SHA'],original_CPU_SHA=cfg['admitted_CPU_SHA'],original_worker_and_CPU_EXIT0=True,old_scheduler_stop_error_retained=True,current_parent_holds_same_GPU_fcntl_after_old_actual_exit=True,runtime_assets_source_LIB_worker_nativeCPU_byteexact=True,no_GPU_native_or_raw_replay=True))
 return dict(value=v,path=str(p),SHA=H(p),actual_CPU_waited_EXIT0=True)
