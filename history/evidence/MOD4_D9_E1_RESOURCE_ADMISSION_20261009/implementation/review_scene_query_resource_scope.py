"""Reuse precise SDK checks, independently compare unchanged surfaces/route samples."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
s=(D/'review_interface_scope.py').read_text(encoding='utf8')
s=s.replace('E1_TRANSPORT_CURRENT_ACTUAL.json','E1_SCENE_QUERY_RESOURCE_CURRENT_ACTUAL.json').replace('actual_transport_interface','actual_scene_query_resource')
s=s.replace('6acb9e8ca302667a0b0f965a1a006e132d4ee06dbd42f4ca8de47e4289a339d8','5e08ac5ea955667d40e640f0372e96940e09535811cb6596bef9ed0559ee0717')
s=s.replace('s3-e1-gentle-grid-fullD7-interface-frozen.zip','s3-e1-scene-query-resource-interface-frozen.zip').replace('E1_ACTUAL_GROUND_INTERFACE_SCOPE_REVIEW.json','E1_RESOURCE_INTERFACE_BASE_CHECKS.json')
exec(compile(s,str(D/'review_interface_scope.py')+'[new-setting-base-contract]','exec'),{'__file__':str(D/'review_interface_scope.py'),'__name__':'__main__'})
old=read(R/'actual_transport_interface/probe.json');new=read(R/'actual_scene_query_resource/probe.json');proof=read(R/'E1_RESOURCE_INTERFACE_BASE_CHECKS.json')
assert new['recipe']['resource_candidate']['unused_PhysX_scene_query_support'] is False
assert new['recipe']['resource_candidate']['actual_authored_Warp_ground_query_retained'] and new['recipe']['resource_candidate']['collision_geometry_and_contact_solving_unchanged']
checks={name:old[name]==new[name] for name in ('actual_mesh','exact_collision_partition','initial','phase_readbacks','final_parameters','ordinary_task_events','max_closure_m','max_mimic_rad','actual_contact_callbacks','actual_action_group_callbacks','action_recipe','sensor_recipe','feedback_recipe','spring_recipe','gas_recipe','chassis_PD_recipe')}
assert all(checks.values()),checks
proof.update(epoch=time.time(),actual_resource_setting_SDK_scope_accepted=True,exact_baseline111_reused=True,original_geometry_all_faces_winding_D0_D7_parameter_conditions_preserved=True,initial_and12_sampled_fullroot30q_groundnormal_commands_exact=True,comparison_fields_exact=checks,not_full_dynamic_bitexact_or20k_resource_acceptance=True,do_not_launch_while_old_native_process_or_authority_alive=True,native20k_and_real_PPO_still_required=True)
(R/'E1_SCENE_QUERY_RESOURCE_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(dict(resource_interface_accepted=True,sampled_plant_exact=True,geometry_exact=True,original_20k_failure_retained=True,no20k_or_PPO_pass_claimed=True)))
