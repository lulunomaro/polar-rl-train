"""Reuse only actual same-source/backend/GPU completed fullstate native and its original CPU proof."""
from pathlib import Path
import json,hashlib,psutil,os
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate_declaration(proof,spec,manifest):
 assert proof['key']==spec['key']==manifest['key'] and proof['source_SHA']==spec['source_SHA']==manifest['source_SHA'];assert proof['GPU_UUID']==spec['GPU_UUID'] and proof['execution_backend']==spec['execution_backend'];assert proof['Adam']==manifest['source_Adamstep'] and proof['controls']==spec['native_controls'];assert proof['callbacks']==4*proof['controls'];assert proof['original_native_runtime_assets_digest']==manifest['native_runtime_assets_digest'];assert proof['CPU_report_SHA'] and proof['native_PT']['SHA'] and proof['actual_native_worker_EXIT0'] and proof['actual_CPU_waited_EXIT0'];assert proof['old_native_branch_same_or_whole_worker_exact'];return True
def load(spec,B):
 m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());proof=json.loads((B/'ADMITTED_NATIVE_REUSE_PROVENANCE.json').read_bytes());validate_declaration(proof,spec,m);old=Path(proof['root']);e=json.loads((old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['all_actual_own_GPU_children_waited'] and e['private_GPU_fcntl_released_if_acquired'] and e['passed_native_CPU'] and not e['original_error'];parent=json.loads((old/'NATIVE_ONLY_FINAL_ACTUAL.json').read_bytes());assert parent['passed_native_GPU_and_full_CPU'] and parent['actual_GPU_worker_EXIT0'];cpu=old/'job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json';assert H(cpu)==proof['CPU_report_SHA'];v=json.loads(cpu.read_bytes());assert v['passed'] and v['source_SHA']==spec['source_SHA'] and v['controls']==proof['controls'] and v['callbacks']==proof['callbacks'];assert v[{'e2':'source_actor9_critic8_STD17Adam_literal_bytes_exact','recovery':'all_original_core_tensor_bytes_exact'}[spec['key']]]
 pt=Path(proof['native_PT']['path']);assert pt.is_file() and pt.stat().st_size==proof['native_PT']['bytes'];assert H(old/proof['old_worker_filename'])==proof['old_worker_SHA']
 for row in m['files']:
  if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
   p=old/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative']
 if spec['execution_backend']!='source210':assert str(proof['GPU_UUID']) in (old/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').read_text()
 own=[]
 for p in psutil.process_iter(['pid','cmdline']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
  except psutil.Error:pass
 assert not own;assert v==json.loads((B/'REUSED_ORIGINAL_NATIVE_ALL_ROWS_CPU_REPORT.json').read_bytes());return dict(value=v,path=str(cpu),SHA=H(cpu),actual_CPU_waited_EXIT0=True,strict_same_source_backend_GPU_original_native_reused=True,no_native_raw_or_PT_rehashed_or_replayed_for_qualification=True)
