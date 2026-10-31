"""LOCAL source/purpose/index only. No actual artifact,SDK or remote access."""
from pathlib import Path
import argparse,hashlib,json,time
N=Path(__file__).resolve().parent.parent;R=N/'reports'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','seal'));a=p.parse_args();R.mkdir(exist_ok=True)
 if a.mode=='freeze':
  files=[N/'diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py',N/'source/check221_synthetic_clamp_order_once.py',Path(__file__).resolve()]
  put(R/'CPU221_SOURCE_PURPOSE_FROZEN.json',dict(purpose_id='NEW221_CLAMP_ORDER_DIAGNOSTIC_SOURCE_AND_ONE_SYNTHETIC_CPU_CASE_V1',
   frozen_epoch=time.time(),groups=2,synthetic_numeric_cases=1,source_files=[ref(x) for x in files],
   scope='Source AST plus ONE4row synthetic clamp/order/runs/root delta case;not the actual artifact',
   PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0,old220_fixture_replays=0,execution='ONCE_NO_REENTRY'))
  print(json.dumps(dict(purpose_frozen=True,groups=2,synthetic_cases=1,actual_artifact_reads=0)));return
 cpu=json.loads((R/'CPU221_SOURCE_AND_ONE_CLAMP_ORDER_CASE_ACTUAL.json').read_bytes());assert cpu['passed']
 entry=N/'diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py'
 put(R/'ROOT221_MINIMAL_UNUSED_CPU_READ_CONTRACT.json',dict(status='SOURCE_FROZEN_CPU_SOURCE_CHECK_PASS_REAL_ARTIFACT_UNUSED',entry=ref(entry),
  CLI='REMOTE_CPU_PYTHON -B diagnose221_ACTUAL220_NPZ_CPU_UNUSED_once.py --out-new NEW_UNUSED_TARGET_REPORT_DIRECTORY',
  ROOT_precondition='Fresh selected219 exactowner/run/GO and sole serialSSH using ROOT existing template;no new caller framework',
  artifact=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_NEW32341_N1_FLIGHT_20261101v220v2/case/actual_capture/ACTUAL220_NEW210_E0_BODY_POSES_AND_FLIGHT.npz',
   bytes=865215,SHA='16b81b77577aefe9eccf3a6aa2d70e68e807ac3d4c974ae112d9966d72e73bd4'),
  counts=dict(physical_file_byte_passes=1,hash_from_same_in_memory_bytes=1,np_load_BytesIO=1,
   selected_member_accesses_each=1,selected_members=['raw_action6','original_reward_motor_actions6','q30','joint_names','authored_wheel_bottom_above_plane_m','root13','commands','original_reward_command4','control'],
   copies_downloads=0,new_GPU_model_SDK_calls=0,learning=0),
  output='Raw6 signed clamp fractions/longest runs;clip6[:,0,1,4,2,3,5] residual vs recorded reward actions;q30 coordinate ranges/changes;common authored bottom peak;pre-reset root displacement/velocity reference;original yaw/height commands',
  no_recomputed_flight_force_mask_or_rollout=True,original220_parent_false_preserved=True,
  no_STD_reward_guard_tuning_or_motor_torque_or_unique_cause_claim=True,
  actual_child_artifact_reads=0,actual_target_execution=False,all_files_pending_root_Git=True))
 put(R/'SOURCE221_READER_AND_SCOPE_NOTES.json',dict(
  superseded_draft='drafts v1 never executed;Root requested a minimal reader instead of added authority framework;preserved source only',
  patcher_error='First combined move+add apply_patch rejected multiple operations for same path before mutation;sequential move then add succeeded;no experiment',
  old220_physical_trace_true_parent_marker_false_not_modified=True,actual_NPZ_PT_or_remote_reads=0))
 rows=[]
 for f in sorted(N.rglob('*')):
  if f.is_file():
   assert f.suffix in ('.py','.json','.md','.txt') and not f.name.endswith(('.partial','.active'))
   row=ref(f);row['relative']=str(f.relative_to(N)).replace('\\','/');row['selected_entry']=f==entry;rows.append(row)
 index=dict(schema='mod4.221.minimal_saved_npz_diagnostic_source.v1',frozen_epoch=time.time(),files=rows,file_count=len(rows),
  status='MINIMAL_READER_SOURCE_CPU_PASS_ACTUAL_NPZ_UNREAD',source_CPU_groups=2,synthetic_cases=1,
  actual_child_PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0,old220_fixture_replays=0,Git_status='PENDING_ROOT_UNIFIED_ARCHIVE')
 path=N/'INDEX221_FROZEN.json';put(path,index);print(json.dumps(dict(INDEX=ref(path),entry=ref(entry),files=len(rows),actual_artifact_reads=0)))
if __name__=='__main__':main()
