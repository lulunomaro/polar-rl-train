"""R5 two-active source contract; no network/process/model operations on import."""
from pathlib import PurePosixPath
import native87_install_activate_support_v1 as original
from native87_available_two_schedule_v1 import ACTIVE,DEFERRED,BOUNDARY_NAME,validate_boundary
KEYS=ACTIVE
ROOTS=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87r5/h1',
 recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87r5/recovery')
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87r5/owner'
OWNER_SCRIPT='three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py'
REMOTE_OWNER_CREATE=original.REMOTE_OWNER_CREATE.replace(
 "tasks/H1step270_own_fudan_native_2610v87').resolve()",
 "tasks/H1step270_own_fudan_native_2610v87r5').resolve()")
assert REMOTE_OWNER_CREATE!=original.REMOTE_OWNER_CREATE
def validate_prepared(q,protocol,boundary,boundary_SHA):
 assert q['passed'] is True
 assert set(q['specs'])==set(q['payloads'])==set(q['sources'])==set(q['roots'])==set(KEYS)
 assert q['roots']==ROOTS and q['owner_root']==OWNER and q['owner_script']==OWNER_SCRIPT
 assert q['controllers_relative']=='controllers_r5'
 assert q['deferred_experts']==list(DEFERRED) and q['resource_boundary_SHA']==boundary_SHA
 assert validate_boundary(boundary)
 for key in KEYS:
  spec=q['specs'][key]
  assert spec['key']==key and protocol.validate_spec(spec)
  assert q['sources'][key]['SHA']==original.SOURCE_SHA and q['sources'][key]['bytes']>0
  assert not spec.get('preinstalled_CPU_proof_SHA'),'prepared input precedes actual CPU admission'
 return True
def validate_CPU(cpu,q,protocol,prepared_SHA):
 assert cpu['passed'] is True and cpu['actual_finite_returned'] is True
 assert cpu['prepared_source_report_SHA']==prepared_SHA
 assert set(cpu['results'])==set(cpu['specs_with_preinstalled_CPU_proof'])==set(KEYS)
 for key in KEYS:
  r=cpu['results'][key];spec=cpu['specs_with_preinstalled_CPU_proof'][key]
  assert {k:v for k,v in spec.items() if k!='preinstalled_CPU_proof_SHA'}==q['specs'][key]
  assert protocol.sha(spec.get('preinstalled_CPU_proof_SHA')) and spec['preinstalled_CPU_proof_SHA']==r['preinstalled_CPU_proof_SHA']
  envelope=r['ready_envelope']
  assert r['passed'] is True and not r.get('original_error') and envelope['actual_CPU_waited_EXIT0'] is True
  value=envelope['value'];api=value['actual_observation_manager_source_CPU']
  assert value['actual_observation_manager_API_source_CPU_passed'] is True and value['expected_actual_SDK_observation_manager_SHA']==EXPECTED_OBSERVATION_MANAGER_SHA
  assert api['passed'] is True and api['actual_installed_observation_manager_source_SHA']==EXPECTED_OBSERVATION_MANAGER_SHA and api['actual_source_API_fragments_checked'] is True
  assert api['fixture_only'] is True and api['actual_scene_or_runtime_encoder_resolution'] is False
  ingress=value['actual_SDK_tensor_ingress_CPU'];assert value['actual_SDK_tensor_ingress_CPU_passed'] is True and ingress['passed'] is True
  assert value['expected_actual_SDK_base_articulation_data_SHA']==q['specs'][key]['expected_actual_SDK_base_articulation_data_SHA']
  assert value['expected_actual_SDK_physx_articulation_data_SHA']==q['specs'][key]['expected_actual_SDK_physx_articulation_data_SHA']
  assert PurePosixPath(envelope['path'])==PurePosixPath(ROOTS[key])/'job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json'
  assert protocol.native87_valid_ready(dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,original_error=False),spec)
 return True

LAUNCH_REMAINING_SNAPSHOT=576771.2963469028
PREVIOUS_R4_REPORT='CURRENT_ACTUAL87R4_GO_BUT_PRECONTROL_PROXYARRAY_FAILURE_CLOSED_ORIGINAL_COST_WORK_ORDER.json'
EXPECTED_OBSERVATION_MANAGER_SHA='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8'
assert original.REMOTE_ACCOUNT.count('577055.9868602753')==1
REMOTE_ACCOUNT=original.REMOTE_ACCOUNT.replace('577055.9868602753','576771.2963469028')
def validate_launch_closed_receipt(q,previous,previous_SHA):
 assert q['launch_remaining_snapshot']==LAUNCH_REMAINING_SNAPSHOT
 assert q['previousR4costreportSHA']==previous_SHA
 assert previous['actual_state']=='R4_two_actualGO_both_pre_first_control_SDK_ProxyArray_torque_ingress_failure_closed_noFINAL_noPi'
 assert previous['root_interface_assumption_error_acknowledged'] is True and previous['worker_rc0_not_success'] is True
 assert previous['actual_completed_native_controls']==0 and previous['actual_new_policy_updates']==0 and previous['native_FINAL_present'] is False
 assert previous['owner_nodes_children_out_and_original_fee_settled'] is True and previous['canonical_active_segment'] is None
 assert previous['closing_remaining_snapshot']==LAUNCH_REMAINING_SNAPSHOT
 assert previous['original_independent_fees']==dict(h1=50.581077575683594,recovery=94.65810489654541)
 assert previous['normal_duration_flags']==dict(h1=True,recovery=True)
 assert sum(previous['original_independent_fees'].values())==previous['sum_once']==145.239182472229
 return True
