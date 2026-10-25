from pathlib import Path
import json,time,hashlib,os,fcntl
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def admitted_native(cfg):
 import three_expert_helpers_v2 as b
 import psutil,shutil
 B=Path(__file__).resolve().parent;A=Path(cfg['admitted_native_root']);assert A.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2'));assert H(A/'CONTINUATION_COMPLETE_MANIFEST_V2.json')==cfg['admitted_base_manifest_SHA'];m=json.loads((A/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes())
 for r in m['files']:
  if r['relative'].startswith(('job0/runtime/','job0/source/','job0/assets/','lib/')) or r['relative'] in ('recovery_worker.py','native_CPU.py'):
   p=B/r['relative'];assert p.is_file() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 started=time.time()
 while not (A/'PARENT_EXIT_ACTUAL.json').exists():
  assert time.time()-started<1800;b.send(cfg,dict(key=cfg['key'],phase='waiting_admitted_own_native',original_native_root=str(A),manifest_SHA=cfg['manifest_SHA']));time.sleep(3)
 final=json.loads((A/'PARENT_FINAL.json').read_bytes());assert not final['passed_native_CPU'] and final['PPO_updates']==0;correction=json.loads((A/'CORRECTED_REFERENCES_V6_CPU_COMMAND_ACTUAL.json').read_bytes());assert correction['returncode']==0;identity=json.loads((A/'PARENT_IDENTITY.json').read_bytes());process=None
 try:process=psutil.Process(identity['pid'])
 except psutil.Error:pass
 waited=time.time()
 while process is not None and psutil.pid_exists(identity['pid']) and abs(process.create_time()-identity['creation'])<=.1:
  assert time.time()-waited<30;b.send(cfg,dict(key=cfg['key'],phase='waiting_native_parent_actual_exit',manifest_SHA=cfg['manifest_SHA']));time.sleep(.2)
  try:process=psutil.Process(identity['pid'])
  except psutil.Error:process=None
 assert json.loads((A/'WORKER_EXIT_ACTUAL.json').read_bytes())['returncode']==0;assert json.loads((A/'CPU_ACTUAL_EXIT.json').read_bytes())['returncode']==1
 oldlock=Path('/home/lc01/Zonglin Li/zonglin2/state/recovery_schema_v3_gpu1.lock')
 with oldlock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 O=A/'job0/native';native=json.loads((O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json').read_bytes());assert H(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json')==cfg['corrected_CPU_report_SHA'] and native['original_GPU_observer_and_fixed_raw_absolute_checks_still_rejected'] and native['corrected_CPU_observer_admission'] and native['no_physical_query_COM_mimic_closure_threshold_changed'];complete=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert native['passed'] and native['source_SHA']==cfg['source_SHA'] and native['controls']==336 and native['callbacks']==1344;assert H(Path(complete['path']))==complete['SHA']==native['native_checkpoint_SHA'];target=B/'job0/native';assert not target.exists();target.mkdir()
 for name in ('own_native336.pt','own_startup0.pt','NATIVE336_COMPLETE.json','FINAL.json','GEOMETRY_AND_RESET_ACTUAL.json','VALID_PREFIX_INDEX.json','SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json'):shutil.copy2(O/name,target/name)
 shutil.copy2(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json',target/'NATIVE_ALL_ROWS_CPU_ADMITTED.json')
 assert H(target/'own_native336.pt')==native['native_checkpoint_SHA'];b.put(B/'ADMITTED_NATIVE_REUSE_ACTUAL.json',dict(epoch=time.time(),original_root=str(A),original_native_CPU_SHA=H(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json'),saved_complete_SHA=native['native_checkpoint_SHA'],runtime_assets_source_LIB_bytes_exact=True,actual_original_parent_child_and_CPU_out=True,old_parent_and_CPU_failure_retained=True,independent_corrected_CPU_command_EXIT0=True,numerical_enclosure_not_GPU_bitexact=True,actual_original_gpu1_fcntl_free=True,no_native_GPU_or_raw_replay=True,raw_indexes_keep_actual_original_paths=True))
 return dict(value=native,path=str(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json'),SHA=H(O/'NATIVE_ALL_ROWS_CPU_CORRECTED_REFERENCES_V6.json'),actual_CPU_waited_EXIT0=True)
