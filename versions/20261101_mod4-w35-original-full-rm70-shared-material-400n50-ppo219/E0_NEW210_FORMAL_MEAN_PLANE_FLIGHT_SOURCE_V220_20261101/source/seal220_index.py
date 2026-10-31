"""Freeze LOCAL220 source/CPU/index, no actual model or target access."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent.parent;R=N/'reports'


def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 cpu=json.loads((R/'CPU220_SOURCE_EVIDENCE_AND_BINDING_ACTUAL.json').read_bytes())
 assert cpu['passed'] and cpu['group_count']==3 and cpu['expected_refusals']==11
 entries=[N/n for n in ['prepare220_task_from_actual210_SELECTED_authority_UNUSED.py',
  'target220_single_N1_parent_UNUSED.py','evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py']]
 put(R/'ROOT220_CALL_AND_UNCONSUMED_TARGET_PURPOSE.json',dict(epoch=time.time(),
  status='SOURCE_CPU_PASSED_ACTUAL_TARGET_UNUSED_ROOT_REVIEW_REQUIRED',entries=[ref(p) for p in entries],
  purpose_id='NEW220_CLOSED210_E0_MEAN_N1_PLANE_YAW0_FLIGHT_EVIDENCE',
  target='72',num_envs=1,controls_max=1000,physics_max=8000,feedback_max=2000,seconds_max=20.,first_episode_only=True,
  model='DYNAMIC actual210 closing+matching NEW whole CPU:remote final source;not old32066/W35',
  Root_reported_reference_model=dict(SHA='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538',
   bytes=22961801,iteration=32341,Adam17=648340,new_PPO_updates=275,provenance='ROOT message only;builder still verifies actual saved report JSON'),
  current_authority='ROOT-selected launch/state files supplied as parameters;supports successful219V3 or fresh explicitCNone;target reads canonical/owner/go afresh',
  selected_GPU='ROOT actual resource/privateEX selection;168 allowed while219c27active,c27 rejected for same active role',
  source_model_byte_reads=1,source_model_decodes=1,source_model_copies=0,old_CPU_PT_reads=0,
  constructor_binary_scope='Original207 robotUSD/resetNPZ constructor only;childsource reads0',
  geometry_metadata_queries_max=2,USD_stage_open_calls=0,extra_PhysX_getters=0,
  flight_definition='Both XYZ force norms<=1N and both authored collision bottoms>5mm for>=2endpoints;span(n-1)*.02',
  landing='Contact reappearance only;no stable270/population claim',
  unknown_geometry='UNKNOWN with reason;not fake radius/clearance or a training gate',
  artifact='One new own pose NPZ on72,producer path/bytes/SHA/model+worker metadata only;no download/display/GUI',
  worker_seconds=840,parent_initial_wait_seconds=900,no_release_until_original_child_waitout=True,
  readback_required=['passed_execution not justOSRC0','CAPTURE220 result and complete cornercases','original waitRC0',
   'APP220_CLOSED','allownwaited/private+sharedEXreleased','producer metadata,NPZ memberreads0/transfers0'],
  optimizer_steps=0,account_writes=0,GUI=False,child_actual_execution=False,
  CPU_source_proof=ref(R/'CPU220_SOURCE_EVIDENCE_AND_BINDING_ACTUAL.json'),all_files_pending_root_Git=True))
 put(R/'SOURCE220_READER_NOTES_AND_PRESERVED_PRIOR_FAILURES.json',dict(
  source_reader_notes=[dict(id='SOURCE220_194_CONTACT_RG_OUTPUT_CLIPPED',
   result='One broad194contact source rg output clipped at output budget;followed by narrow jump194_sdk and literal_boundary source reads. No model/raw/physical run.')],
  prior219_failures='ROOT preserved unused219 original,independentV2 SFTP mode repair and actual preGO sender whitelist rejection;220 does not modify or relabel those results',
  selected_success_prefix='No hardcoded failed owner prefix;ROOT supplies actual selected launch/state paths',
  all_physical_claims_pending_actual_target_result=True,PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0))
 rows=[]
 for p in sorted(N.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md','.txt') and not p.name.endswith(('.partial','.active'))
  r=ref(p);r['relative']=str(p.relative_to(N)).replace('\\','/')
  r['synthetic_CPU_fixture_only']='SYNTHETIC220_SCHEMA_ONLY' in r['relative'];rows.append(r)
 idx=dict(schema='mod4.220.frozen_new210_E0_plane_flight_source.v1',frozen_epoch=time.time(),files=rows,file_count=len(rows),
  status='WORKER_TASK_PARENT_SOURCE_COMPLETE_CPU_PASS_ACTUAL_TARGET_UNUSED',source_CPU_groups=3,source_CPU_refusals=11,
  target_N1_controls_max=1000,physics_max=8000,original_reward_physics_guards_unchanged=True,
  source_model_dynamic_from_actual210_NEW_CPU=True,current_owner_binding_ROOT_selected_not_failed219_hardcode=True,
  child_PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0,old207_218_fixture_replays=0,
  actual_flight_or_270_or_population_success_claim=False,no_GUI_or_artifact_transfer=True,
  no_active_partial_model_or_raw_in_index=True,Git_status='PENDING_ROOT_UNIFIED_ARCHIVE')
 p=N/'INDEX220_FROZEN.json';put(p,idx)
 print(json.dumps(dict(INDEX=ref(p),files=len(rows),source_CPU_passed=True,actual_target_unused=True,forbidden_calls=0)))


if __name__=='__main__':main()
