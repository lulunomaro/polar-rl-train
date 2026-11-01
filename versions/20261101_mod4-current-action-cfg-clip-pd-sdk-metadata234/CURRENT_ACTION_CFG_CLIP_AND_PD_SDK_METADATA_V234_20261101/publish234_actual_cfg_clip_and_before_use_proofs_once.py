from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
a=read(R/'ROOT234V3_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json');assert a['passed_execution']
r=a['original_parent']['result'];free=read(R/'ROOT234V3_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json');assert free['global_serial_control_client_lease']=='FREE'
assert r['NN_constructors']==r['model_byte_reads']==r['model_decodes']==r['controls']==r['new_action_step_calls']==r['constructor_contact_tick']==0
assert r['legs']['cfg_clip_actual']is None and r['legs']['members']['_scale']==.5
src={Path(x['path']).name:x for x in r['current_unique_source_files']}
joint=src['joint_actions.py']['UTF8'];pd=src['actuator_pd.py']['UTF8']
assert 'self.cfg.clip is not None'in joint and 'set_joint_position_target'in joint and '_clip_effort'in pd
out=dict(epoch=time.time(),kind='ACTUAL234V3_CURRENT_ACTION_CFG_AND_SDK_SOURCES_0NN',passed_execution=True,
 selected_actual=r,original_worker_wait=a['original_parent']['wait'],all_ROOT_SSH_closed=free,
 resolved_summary=dict(legs_cfg_clip=None,leg_policy_order=r['legs']['joint_names'],scale=.5,offsets=r['legs']['members']['_offset'],CAD_difference_min=-1.0843,CAD_difference_max=.85,
  leg_inherited_apply=r['legs']['methods']['apply_actions']['closure_callables'],current_actuator_class={k:x['class_name']for k,x in r['actuators'].items()},leg_resolved_actuator_cfg=r['actuators']['legs']['resolved_cfg']),
 interpretation='CurrentE0JUMP210packageon72 hascfg.clip=None;resolvedinheritedactionprocess conditionalclip is disabled,customprojection changescrankrelativehip,then delayedapplysetsjointpositiontarget. StaticCADjointlimits are not the softwaretargetclip observed here. OriginalPD/DC/DR and physicaljointlimits remain;no action executed means no measuredactualtorque/saturation or unique failurecause proof.',
 source_path_label_scope='ActualruntimeMROsourcefilesareunderIsaacLab-3.0.0-beta2.patch1 checkout path;thisisprovenresolvedcodepath,not an inferred installedpackageversion change.',
 actual_counts=dict(unique_PY_source_byte_reads=9,additional_get_dof_limits=1,own_constructor_reset_NPZ_purpose=1,controls=0,neural_forwards_constructs=0,model_reads=0,optimizer_or_budget=0),
 original_failures_preserved=['Original234workerpreSDKselfSHA LF-vsCRLF refused,SDK/model0;exactbytehashboundinnewsource','234V2 localROOT234V2V2_SOURCE pathrefusal beforeCIM/network','234V3 newnamespace actualPASS,originalworkerbytesunchanged'],
 frozen_E0_and_225_or_policies_rewards_physics_unchanged=True,source_only_inference_not_measured_control=True,no_hip_clamp_or_distribution_repair_selected=True)
p=R/'CURRENT_ACTUAL234V3_CFG_CLIP_NONE_AND_CURRENT_SDK_ACTION_CHAIN_WORK_ORDER.json';assert not p.exists();p.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
# Build the newE2 generator's explicitly scoped232 projection from saved actual
# receipts. Keep the original post-App reader false unchanged.
E=T/'E2_READER_ORDER_REPAIR_AND_FULL_WORLD_CASE_V232_20261101';rp=E/'reports/ROOT232_ACTUAL_E2_METADATA_AND_ORIGINAL_MEAN_CASE_RETURNED.json';b=rp.read_bytes();whole=json.loads(b)
rows={Path(x['path']).name:json.loads(x['UTF8'])for x in whole['full_UTF8']if x['path'].endswith('.json')}
restore=rows['ACTUAL_E2_93_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json'];native=rows['ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json'];close=rows['ACTUAL232_ALL_WAITED_PRIVATE_SHARED_RELEASED.json'];command=rows['E2_COMMAND_RESUME_STARTUP_VERIFIED.json']
assert restore['passed']and native['passed']and close['all_own_children_waited']and close['all_owned_locks_released']and command['source_has_E2_command_state']
scope=dict(kind='ROOT232_SCOPED_E2_FULLRESTORE_NATIVE24_ACTUAL_PROJECTION',source_SHA=restore['source_SHA'],num_envs=20000,original232_parent_passed_execution=False,missing_post_Appclose_readcounts_preserved=True,fullrestore_passed=True,core_fingerprints_matched=restore['current_core_tensor_fingerprints_matched'],Adam17=restore['Adam_step'],iteration=restore['stored_RSL_iteration'],LR=restore['actual_constructor_algorithm_optimizer_LR'],source_has_E2_command_state=True,original_D0_D7_then_one_new_episode=True,native24_passed=True,controls=24,physics=192,feedback=48,original_worker_wait_RC=close['original_wait']['returncode'],all_own_children_waited=True,private_EX_released=True,closed_epoch=close['epoch'],original_report_ref=dict(path=str(rp),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()),scope_only_not_E2_skill_pass=True)
pkg=T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101';import sys;sys.path.insert(0,str(pkg));from e2_solo_contract import scoped232;scoped232(scope)
p=R/'ROOT232_SCOPED_ACTUAL_E2_FULLRESTORE_NATIVE24_FOR_NEXT_PPO.json';assert not p.exists();p.write_text(json.dumps(scope,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(passed=True,cfg_clip=None,actual_sources=9,model_reads=0,E2scoped_projection=str(p))))
