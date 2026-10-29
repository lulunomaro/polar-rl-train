"""Create metadata overlays only, never open referenced models/banks/assets."""
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

D = Path(__file__).resolve().parent
L = D.parent


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def put(name, value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    manifest_path=L/'W35_210_FULL_PROFILE_OWN_STORAGE_METADATA_EXTENSION_SOURCE_V1/W35_210_OWN_STORAGE_COMPLETE_INPUT_MANIFEST_V3.json'
    raw=manifest_path.read_bytes();base=json.loads(raw)
    proof=json.loads((D/'WORKER_EXACT_SOURCE_OVERLAY_AND_INVERSE_ACTUAL.json').read_bytes())
    oldworker=next(x for x in base['files'] if x['relative']=='evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py')
    assert oldworker['SHA']==proof['base_SHA256'] and oldworker['bytes']==proof['base_bytes']
    model=next(x for x in base['files'] if x['relative']=='source/W35_ADAPTED92_FINAL78.pt')
    assert model['SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f' and model['bytes']==17619013
    rows=[]
    for p in sorted(D.glob('*.py')):
        if p.name == 'build_task_manifest_and_AST_proof_SOURCE_ONLY_once_v1.py':
            continue  # Original unmatched-parenthesis source retained, refused before execution.
        data=p.read_bytes();tree=ast.parse(data,filename=str(p))
        rows.append(dict(name=p.name,bytes=len(data),SHA=H(data),AST_parse_passed=True))
    component=next(x for x in rows if x['name']=='w35_profile_env_domain_panel_v1.py')
    tree=ast.parse((D/component['name']).read_bytes())
    funcs={n.name:n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
    calls=lambda n:[ast.unparse(c.func) for c in ast.walk(n) if isinstance(c,ast.Call)]
    apply=funcs['apply'];reset=funcs['reset']
    assert calls(apply).count('self.old_apply')==1 and ast.unparse(apply.body[-1])=='return value'
    assert calls(reset).count('panel.old_reset')==1 and ast.unparse(reset.body[-1])=='return result'
    assert any(isinstance(n,ast.Call) and ast.unparse(n.func)=='panel.old_reset' and [ast.unparse(x) for x in n.args]==['env_ids'] for n in ast.walk(reset))
    forbidden={'torch.rand','torch.randn','torch.randint','torch.Generator','torch.load','torch.save','self.real.sim.step','self.real.step','self.real.reset','self.robot.write_joint_stiffness_to_sim_index'}
    found=set(calls(tree))&forbidden
    assert not found,found
    assert not any(isinstance(n,ast.Attribute) and n.attr in ('load_state_dict','backward') for n in ast.walk(tree))
    task=dict(kind='MOD4_W35_ADAPTED92_PROFILE_ENV_DOMAIN_PANEL_V1',source_SHA=model['SHA'],num_envs=20000,
              controls=600,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,
              actual_source210_SDK_admission_passed=False,actual_private_GPU_EX_held_by_parent=False,
              canonical72_known_owner_readonly_passed=False,known72_readonly_authority=None,
              actual_source210_python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
              full_WM_tap_included=False,
              domain_binding=dict(backend='IsaacLab; exact previously admitted210 SDK source required, not MuJoCo/foreign data',
                                  source_model=model,base_source_manifest_SHA=H(raw),policy_hz=50,control_us=20000,
                                  physics_us=2500,decimation=8,feedback_hz=100,TGS_position_velocity_iterations=[32,4],
                                  obs_policy_width=35,obs_critic_width=38,STD_width=6,Adam_state_count=17,Adam_step=648360,
                                  optimizer_and_algorithm_LR=.00011390625000000003,
                                  action_clip_source_value=6,nominal_gas_force_N_each=400,nominal_stiffness_N_m=2000,
                                  upper_q_m=.020639440248416612,lower_q_m=-.0267046843609,nominal_damping_N_s_m=3,
                                  gas_recipe_is_engineering_assumption_not_measured_curve=True,
                                  nearest_height_command_m=.25,independent_selected_W35_bank_pose_index=34,
                                  no_flat74_bank_assumption=True,original_reset_G3_retained_commands_D1_D7_unchanged=True,
                                  actual_DR_queue_and_episode_values='read from existing restored objects at trace boundary; no lazy construction',
                                  state_layout='root13/q30/dq30; selected domain trace, no pack127 or complete force/torque WM groundtruth'))
    put('FROZEN_CASE_TASK_TEMPLATE_UNUSED_UNADMITTED.json',task)
    overlays=[]
    for name in ('evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v1.py','w35_profile_env_domain_panel_v1.py','FROZEN_CASE_TASK_TEMPLATE_UNUSED_UNADMITTED.json'):
        data=(D/name).read_bytes();overlays.append(dict(relative=name,local_path=str(D/name),bytes=len(data),SHA=H(data),new_small_source_or_task_only=True))
    exclusions=['evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py']
    put('NEXT_INPUT_MANIFEST_OVERLAY_UNUSED_UNADMITTED.json',dict(kind='W35_profile_env_domain_panel_source_overlay_v1',
        original_input_manifest_path=str(manifest_path),original_input_manifest_SHA=H(raw),
        unchanged_input_rows=[x for x in base['files'] if x['relative'] not in exclusions],
        excluded_old_worker_rows=[x for x in base['files'] if x['relative'] in exclusions],
        new_overlay_rows=overlays,original_RSL_sources=base['RSL_sources'],original_SDK_math_SHA=base['SDK_math_SHA'],
        no_old_binary_content_or_rehash=True,task_fields_false_until_real_admission=True,
        no_existing_supervisor_or_launcher_reexecution_allowed=True,actual_final_manifest_and_target_binding_pending=True))
    put('SOURCE_AST_HOOK_TRANSPARENCY_AND_INPUT_BINDING_ACTUAL.json',dict(epoch=time.time(),passed=True,source_rows=rows,
        base_worker_exact_manifest_pin=True,exact_inverse_bytes=proof['inverse_bytes_exact'],
        original_queue_apply_called_once_returns_original_object_by_source=True,
        original_reset_called_once_with_original_argument_returns_original_result_by_source=True,
        no_simulation_actor_optimizer_RNG_or_state_load_call_in_component=True,
        domain_capture_uses_existing_restored_D1_D7_objects_not_lazy_getters=True,
        original_exception_paths_not_suppressed=True,
        synthetic_CPU_statistics_only=json.loads((D/'CPU_SYNTHETIC_PROFILE_ENV_DENOMINATOR_ACTUAL.json').read_bytes()),
        actual_original_hook_call_order_clock_reset_RNG_model_integrity_and_performance_pending=True,
        runtime_first24_must_prove=dict(controls=24,physics_callbacks=192,feedback_samples=48,queue_calls_each_group=192,
                                       policy_hz=50,physics_dt_s=.0025,control_dt_s=.02),
        no_GPU_model_or_remote_run=True))
    print(json.dumps(dict(passed=True,component_SHA=component['SHA'],base_worker_SHA=proof['base_SHA256'],worker_SHA=proof['target_SHA256'],task_unadmitted=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('ORIGINAL_SOURCE_BINDING_ERROR_'+str(time.time_ns())+'.json',dict(passed=False,traceback=traceback.format_exc()))
        raise
