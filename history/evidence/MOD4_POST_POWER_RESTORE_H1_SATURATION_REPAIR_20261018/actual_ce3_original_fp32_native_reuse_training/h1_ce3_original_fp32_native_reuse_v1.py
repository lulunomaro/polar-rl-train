"""Reuse completed ce3 native under original FP32 audit; retain old FP64 refusal."""
from pathlib import Path
import json,hashlib,os,time,psutil,subprocess
SOURCE='ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
def fixed(m):
 return {r['relative']:r['SHA'] for r in m['files'] if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/')) or r['relative']=='job0/original_run_manifest.json'}
def validate(spec,bind,oldm,newm,core,exitrow,gpuwait,formal):
 assert spec['key']==oldm['key']==newm['key']=='h1' and spec['execution_backend']=='target72'
 assert spec['GPU_UUID']==bind['GPU_UUID']==GPU
 assert spec['source_SHA']==bind['source_SHA']==oldm['source_SHA']==newm['source_SHA']==SOURCE
 assert spec['source_Adamstep']==oldm['source_Adamstep']==newm['source_Adamstep']==646100 and spec['native_controls']==180
 assert core['passed_two_complete_models_source_core_only'] and core['Adam646100_unchanged']
 assert len(core['models'])==2 and all(r['twohost_complete_SHA'] and r['counts']==[199,105] and r['all_model_runtime_finite'] and r['source_actor9_STD_critic8_17Adam_literal_exact'] for r in core['models'])
 assert exitrow['actual_all_own_children_waited'] and exitrow['validation_fcntl_released_if_acquired'] and exitrow['terminal_received_by_source']
 assert gpuwait['returncode']==0 and gpuwait['actual_waited'] and gpuwait['pid']==16513
 v=formal['original_FP32_formal_allrow_CPU'];n=formal['CPU_report']
 assert formal['CPU_pid']==18051 and formal['no_GPU_or_GO_or_canonical_write'] and formal['dual_FP64_admission_false_unchanged'] and formal['old_owner_node_failure_not_relabelled_pass']
 assert n['SHA']==bind['native_CPU_SHA']==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
 assert v['passed'] and v['source_SHA']==SOURCE and v['controls']==180 and v['callbacks']==720 and v['all_policy_rows']==3600000 and v['all_physical_rows']==14400000
 assert v['all_saved_actor_CPUmean_maxabs']<=1e-4 and v['all17Adam_step646100'] and v['sourceactor9critic8STD17Adam_literal_exact'] and v['complete_original20k_typed_source_restore_actual']
 assert v['physical_positive_z_impulse_maxabs']<=1e-6 and v['actual_loaded_Plane_reference_query_maxabs']<=1e-6 and v['geometry_8witness_all720callbacks_independent_numpy_maxabs']<=1e-6
 assert fixed(oldm)==fixed(newm) and fixed(oldm)
 assert oldm['expected_actual_RSL_sources']==newm['expected_actual_RSL_sources'] and oldm['expected_actual_SDK_math_SHA']==newm['expected_actual_SDK_math_SHA']
 return dict(value=v,path=n['path'],SHA=n['SHA'],actual_CPU_waited_EXIT0=True,strict_same_source_backend_reuse=True,reference_protocol='original_formal_H1_FP32_absolute1e-4',old_FP64_refusal_retained=True)
def no_own_processes(root):
 alive=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(root)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
  except psutil.Error:pass
 assert not alive,alive
def reuse_H1_native(spec,b,B):
 m=b.read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');bind=m['H1_same_source_backend_native_reuse'];old=Path(bind['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
 assert old.resolve().is_relative_to(owned.resolve()) and B.resolve().is_relative_to(owned.resolve()) and old!=B
 assert b.H(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==bind['manifest_SHA'];oldm=b.read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 core=b.read(B/'REUSED_NATIVE_COMPLETE_MODELS_CORE_PROOF.json');formal=b.read(B/'REUSED_NATIVE_ORIGINAL_FP32_FORMAL_CPU_PROOF.json')
 oldexit=b.read(old/'NODE_EXIT_ACTUAL.json');gpuwait=b.read(old/'job0/native_WAITED_EXIT_ACTUAL.json')
 native=validate(spec,bind,oldm,m,core,oldexit,gpuwait,formal)
 terminal=b.read(old/'NODE_TERMINAL_ACTUAL.json')['row'];assert terminal['original_error'] and terminal['terminal_all_own_children_waited'] and terminal['phase']=='native'
 assert not (old/'GO_PRODUCTION.json').exists() and not (old/'job0/production').exists()
 assert (old/'NODE_ORIGINAL_ERROR.json').exists() and not (old/'job0/native/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json').exists()
 identity=b.read(old/'NODE_IDENTITY.json')
 if psutil.pid_exists(identity['pid']):
  p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
 if psutil.pid_exists(formal['CPU_pid']):
  p=psutil.Process(formal['CPU_pid']);assert abs(p.create_time()-formal['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
 no_own_processes(old)
 for rel,sha in fixed(oldm).items():assert b.H(old/rel)==b.H(B/rel)==sha
 assert b.H(B/'job0/source/H1_ce3_public4_closed24.pt')==spec['source_SHA']
 q=Path(native['path']);assert q.resolve().is_relative_to(old.resolve()) and b.H(q)==native['SHA']
 # Native PT/raw were already two-host verified. Check existence/size, no repeated raw/PT hash or download.
 for row in core['models']:
  p=Path(row['path']);assert p.resolve().is_relative_to(old.resolve()) and p.stat().st_size==row['bytes']
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(GPU in x for x in compute.splitlines()),compute
 b.put(B/'STRICT_CE3_ORIGINAL_FP32_NATIVE_REUSE_ACTUAL.json',dict(epoch=time.time(),source_SHA=SOURCE,Adam646100=True,GPU_UUID=GPU,native_CPU_SHA=native['SHA'],old_failed_node_and_children_out=True,old_FP64_false_not_overwritten=True,original_FP32_allrows_reused=True,no_native_GPU_replay_or_old_PT_raw_hash=True,source_runtime_assets_installed_manifest_exact=True,not_frozen_jump_skill_or_PPO_pass=True))
 return native
