"""S3 supported domains and S4 preparation: no graduation or live authority writes."""
from pathlib import Path
import json,time,hashlib,shutil
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports';J=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):p=Path(p);return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p))

def main():
 collection=sorted(R.glob('ORIGINAL_PLAN_REGISTRY_CANONICAL_ACTUAL_COLLECTION_*.json'))[-1];c=J(collection)
 pick=lambda n:Path(next(x['local_path'] for x in c['local_collected_files'] if Path(x['path']).name==n))
 approval=J(pick('PLAN_APPROVAL.json'));rev4=J(pick('MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json'));a4=J(pick('MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json'))
 assert approval['approved'] and 'S4' in approval['allowed_stages'] and a4['approved']
 assert H(pick('MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json'))==a4['approved_revision_json_sha256']
 assert H(pick('MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.md'))==a4['approved_revision_md_sha256']
 wave=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011/reports/WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json';curb=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/reports/CURB141_COMPLETE_OBSERVED_SCOPE_DECISION.json'
 wavej=J(wave);curbj=J(curb);assert wavej['observed35mm_complete_ten_wave_scope_accepted_and_frozen'] and curbj['accepted_observed_CURB20_mirrored_scope']
 snapshots=A/'accepted_scope_decision_originals';snapshots.mkdir(exist_ok=True)
 for p in (wave,curb):
  q=snapshots/p.name;assert not q.exists();shutil.copy2(p,q);assert H(q)==H(p)
 s=J(sorted(R.glob('EXPERT_SCOPE_DECISIONS_ACTUAL_COLLECTION_*.json'))[-1]);decisions={Path(r['path']).name:Path(r['local_path']) for r in s['local_collected_files']}
 slope=J(decisions['E1_SLOPE10_138_COMPLETE_SCOPE_DECISION.json']);assert slope['scoped10deg_mirrored_frozen_behavior_accepted'] and slope['accepted_observed_frozen_slope_angles_deg']==[5,8,10]
 e0=J(decisions['D9_RETENTION18_ACTUAL_REVIEW.json']);assert e0['complete_model_task_data_contracts_pass']
 frozen=J(sorted(R.glob('FROZEN_E0_WAVE35_CPU_INPUTS_ACTUAL_*.json'))[-1]);interface=R/'S4_E0_WAVE35_ACTUAL_SOURCE_CPU_INTERFACE_AND_GRADIENT_ISOLATION.json';i=J(interface);assert i['passed_CPU_interface_isolation_only'] and i['optimizer_updates']==0 and not i['S4_GPU_or_PPO_admitted']
 orientation=R/'WAVE50_WHOLE20K_BIRTH_BODYFRAME_LOGICAL_CPU_PREPARED_ACTUAL.json';o=J(orientation);assert o['passed_logical_CPU_proposal'] and o['newproduction_worker_exists'] is False
 cost=R/'S3_E1_CANONICAL_COST_AND_005_105H_PLANNING_ACTUAL_CPU_REVIEW.json';costj=J(cost);assert costj['passed_read_only_accounting_audit']
 current=J(pick('MOE_PLAN_EXECUTION_CURRENT.json'))
 experts=[dict(id='E0',source_SHA=e0['source_sha256'],evidence=ref(decisions['D9_RETENTION18_ACTUAL_REVIEW.json']),role='Frozen previously reviewed flat stand/run, pure spin and original world domain; development2seeds x3D0profiles withD1-D7 retained',actual_original_world_complete=sum(x['passed'] for x in e0['world']),actual_original_world_count=sum(x['count'] for x in e0['world']),old_strict_flags_and_residuals_preserved=True,full_hardware_or_RM_qualified=False),
  dict(id='E1_WAVE35',source_SHA=wavej['own_checkpoint']['sha256'],evidence=ref(snapshots/wave.name),role='Observed mirrored35mm continuous10wave±.3 yaw0 and standing, seed20260928 white3/80env15s',observed_forward=27,observed_reverse=27,pure_spin_old_skill_decline_preserved=True,not_all_WAVE_RM70_or_MoE=True),
  dict(id='E1_CURB20',source_SHA=curbj['checkpoint']['sha256'],evidence=ref(snapshots/curb.name),role='Observed20mm vertical150mm strip, mirroredup/down±.3/yaw0,.4approach and200mmafter',observed_up=27,observed_down=27,pure_spin_and_world_declines_preserved=True,not_full_CURB_RM_or_STAIR_or_MoE=True),
  dict(id='E1_SLOPE',source_SHA=slope['source_checkpoint']['sha256'],evidence=ref(decisions['E1_SLOPE10_138_COMPLETE_SCOPE_DECISION.json']),role='Frozen observed5/8/10degree mirrored ramps, own5deg source with8/10newfrozen behavior',scope_angles_deg=[5,8,10],not_real_RM10_5_or_full_SLOPE_or_MoE=True),
  dict(id='E1_WAVE50_CURRENT',source_SHA='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c',role='Current repaircandidate originalprotocol24/27forward26/27reverse; framefactor27/25 is differentbirthcondition and unchangedweight',remaining_forward=[6,15,69],remaining_reverse=[67],not_qualified50_or70=True,first_gate_source_adopted=False),
  dict(id='E1_STAIR',source_SHA=None,role='Future independently audited realstep geometry; disabled without own source and scope')]
 registry=dict(epoch=time.time(),status='CPU_PREPARATION_REGISTRY_NOT_LIVE_ROUTER_OR_GPU_ADMISSION',master_approval=ref(pick('PLAN_APPROVAL.json')),approved_revision004=ref(pick('MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')),approved_revision005=ref(pick('MOD4_BUDGET_RETRAIN_100H_REVISION_005.json')),experts=experts,
  first_S4_CPU_pair=['E0','E1_WAVE35'],other_experts_disabled_in_first_pair=True,current50mm_perfect_score_not_required_for_S4_CPU_preparation=True,
  no_arbitrary27of27_or_percent_gate=True,old_E1_pure_spin_failures_not_global_veto_for_E1_traversal_role=True,
  deployment_inputs35_normal_proprio_and_commands_only=True,no_terrain_envID_futurecontact_truth_in_actor_or_gate=True,
  expert_critic_and_optimizer_freeze_independent=True,one_whole6action_hardtop1_no_blend=True,
  GPU_admitted=False,gate_trained=False,whole_MoE_qualified=False,hardware_calibrated=False)
 rp=R/'LIMITED_EXPERT_DOMAINS_AND_FIRST_S4_CPU_PAIR_REGISTRY_ACTUAL.json';assert not rp.exists();rp.write_bytes(json.dumps(registry,ensure_ascii=False,indent=2).encode())
 report=dict(epoch=time.time(),passed_scope_cost_and_CPU_preparation_review=True,current_main_stage='S3/E1_WAVE/G1 derived50mm repair',parallel_S4_status='CPU preparing only, actual frozen source interface/isolation verified; no GPU or gate updates',
  approved105h_terrain_planning_not_only_original30h=True,original_canonical_E1_hours=costj['S3_E1_canonical_hours'],pending_complete_local_Windows_hours=costj['pending_known_complete_hours'],pending_interrupted512tail_unknown=True,
  complete_Wave35_CURB20_SLOPE_observed_domains_preserved=True,limited_domain_does_not_equal_full_RM_or_MoE=True,
  current_central_legacy_pause_flag=current.get('human_training_pause_active'),legacy_pause_snapshot_superseded_by_explicit_human_Linux_training_and3060_resume_in_current_chat=True,original_central_metadata_bytes_not_hotpatched=True,
  registry_discovery=dict(root=s['registry_search_root'],depth=s['registry_search_max_depth'],found=s['bounded_registry_candidates'],not_hostwide_absence_claim=True),
  actual_CPU_interface=dict(source_pair=['E0_b109','E1_WAVE35_b026'],shared35view=True,whole6action_hardtop1=True,expert_all9_weights_std_frozen=True,gate_only_gradient_test=True,optimizer_updates=0),
  actual_new_orientation_axis=dict(old_source_whole20k107float99perenv_kept=True,logical_CPU_component_passed=True,new_entry_pose_and_BODYdirection_disclosed=True,deterministic_birthcounts_minus=[710,710],deterministic_birthcounts_plus=[700,700],selectedreset_isolation=True,negative_cases=14,new_linux_reset_worker_not_implemented=True),
  S4_GPU_entry_gaps=['Own immutable2expert source manifest and limited traversal scope; no upgrading observed records to all-RM qualification','Live routing adapter must deliver one samecached35 feedback view toboth experts andgate, using lastactuallyapplied6action and correct reset histories','Original robot/clock/DR/hardware/query/contactCOM and sharedslot/resource guards on actual chosen backend; no crossbackendexact borrowing','Rule-router baseline and supervised gate initialization per approved plan; training labels may be privileged only in training, never inference terrainIDs','Independent actual switch/hysteresis/torquejump/latency/route-boundary fullraw tests and newgate/critic/optimizer/fullsave-resume contracts; no currentGPUpass','Then at most original first45min bounded gate trial from approvedscope with originalunique canonical and guardian, not before actualadmission'],
  next_repair_axis_gaps=o['remaining'],next_actions=['Continue native-reset/fullstate integration for one explicitly declared body-orientation exposure axis from wholee3, no third duration-only sameleftaxis','Prepare firstS4 realadapter/rulebaseline using frozenE0+observed35mmWave, separately from50mmrepair; acceptedotherterrainbranches stayfrozen','Finish pendinglocalWindows originalcanonical UID reconciliation as evidence, no inventedduration/recharge/secondbudget'],
  references=dict(cost=ref(cost),registry=ref(rp),interface=ref(interface),orientation=ref(orientation)),no_GPU_PPO_RNGsignal_or_budgetwrite=True,no_new_human_permission_generated=True,Git_pending=True)
 p=R/'S3_SCOPE_COST_AND_S4_READINESS_GAPS_ACTUAL_CPU_REVIEW.json';assert not p.exists();p.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode())
 q=A/'NEXT_S3_BODYFRAME_REPAIR_AND_FIRST_S4_CPU_ADAPTER_WORK_ORDER.json';assert not q.exists();q.write_bytes(json.dumps(report,ensure_ascii=False,indent=2).encode())
 print(json.dumps(dict(S3_scope_reviewed=True,approved_terrain_planning_hours=105,E1_canonical_hours=costj['S3_E1_canonical_hours'],pending_known_hours=costj['pending_known_complete_hours'],S4_actual_CPU_pair=['E0','E1_WAVE35'],S4_GPU_or_learning=False,new_bodyframe_logical_CPU=True)))

if __name__=='__main__':main()
