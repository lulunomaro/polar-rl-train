from pathlib import Path
import ast,copy,hashlib,json,time,sys,torch
from types import SimpleNamespace
B=Path(__file__).resolve().parent;P=B/'H1_step270_candidate_uninstalled';source=P/'reference_source/jump_takeoff.py'
tree=ast.parse(source.read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='JumpTakeoffStateMachine');node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_get_ballistic_reference')
header='''# Copyright (c) 2026 SCUTRobotLab, SPDX-License-Identifier: MIT.
# Original ballistic reference body copied without AST changes from fixed commit
# b8ff79f3df855faf9dc92f4a282bd80c42649466. MOD4 wrapper and target mapping
# are separate below. CPU candidate only; no force/torque assistance or air reset.
import torch
from types import SimpleNamespace
'''
wrapper='''
def reference(*,elapsed,peak_height,push_start_height,release_height,control_dt=.01,
              timing_mode='dynamic_push_time',fixed_tuck_time_s=.14):
    if not all(torch.isfinite(v).all() for v in (elapsed,peak_height)):
        raise ValueError('nonfinite trajectory input')
    if not (peak_height>release_height).all() or not release_height>push_start_height:
        raise ValueError('Require peak>actual release>actual push-start height')
    if timing_mode not in ('dynamic_push_time','fixed_tuck_time') or control_dt!=.01:
        raise ValueError('Unqualified H1 timing mode or 100Hz control clock')
    env=SimpleNamespace(jump_takeoff_ref_target_height=peak_height,
                        jump_takeoff_phase_time=elapsed,step_dt=control_dt)
    cfg={'trajectory':dict(gravity=9.81,push_start_height=push_start_height,
         release_height=release_height,tuck_timing_mode=timing_mode,
         fixed_tuck_time_s=fixed_tuck_time_s,max_release_height=release_height)}
    return _get_ballistic_reference(None,env,cfg)

def peak_body_height_from_actual_wheel_geometry(*,body_world_z,wheel_bottom_world_z,
                                               reference_ground_world_z,
                                               platform_top_world_z,margin_m):
    if not all(torch.isfinite(v).all() for v in (body_world_z,wheel_bottom_world_z,
             reference_ground_world_z,platform_top_world_z)):
        raise ValueError('nonfinite actual geometry')
    if margin_m<0 or not ((platform_top_world_z-reference_ground_world_z)>=.270).all():
        raise ValueError('Platform below the human 270mm minimum')
    offset=(body_world_z-wheel_bottom_world_z.amin(-1)).clamp_min(0)
    return platform_top_world_z-reference_ground_world_z+offset+margin_m
'''
target=P/'scut_ballistic_reference_uninstalled.py';target.open('x',encoding='utf8').write(header+ast.unparse(node)+'\n'+wrapper)
got=next(n for n in ast.parse(target.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name==node.name)
assert ast.dump(ast.Module(body=node.body,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=got.body,type_ignores=[]),include_attributes=False)
sys.path.insert(0,str(P));from scut_ballistic_reference_uninstalled import reference,peak_body_height_from_actual_wheel_geometry
namespace={'torch':torch};exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(node)],type_ignores=[])),'original_SCUT_ballistic_body','exec'),namespace)
torch.set_num_threads(2);rng=torch.get_rng_state().clone();cases=[]
for timing in ('dynamic_push_time','fixed_tuck_time'):
 t=torch.linspace(0,1,501);h=torch.linspace(.49,.62,501);kw=dict(push_start_height=.205,release_height=.31,control_dt=.01,timing_mode=timing,fixed_tuck_time_s=.14)
 a=reference(elapsed=t,peak_height=h,**kw)
 env=SimpleNamespace(jump_takeoff_ref_target_height=h,jump_takeoff_phase_time=t,step_dt=.01);cfg={'trajectory':dict(gravity=9.81,push_start_height=.205,release_height=.31,tuck_timing_mode=timing,fixed_tuck_time_s=.14,max_release_height=.31)}
 old=namespace[node.name](None,env,cfg)
 assert all(torch.equal(x,y) for x,y in zip(a,old));cases.append(dict(name=timing,rows=501,height_velocity_push_time_literal_exact=True))
mapped=peak_body_height_from_actual_wheel_geometry(body_world_z=torch.tensor([.22]),wheel_bottom_world_z=torch.zeros(1,2),reference_ground_world_z=torch.zeros(1),platform_top_world_z=torch.tensor([.27]),margin_m=.02)
assert torch.allclose(mapped,torch.tensor([.51]),atol=1e-7,rtol=0)
try:peak_body_height_from_actual_wheel_geometry(body_world_z=torch.tensor([.22]),wheel_bottom_world_z=torch.zeros(1,2),reference_ground_world_z=torch.zeros(1),platform_top_world_z=torch.tensor([.269]),margin_m=.02)
except ValueError:pass
else:raise AssertionError('269mm accepted')
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
license=B.parent/'reference_repos/scut_wheeled_legged_RL/LICENSE'
if license.exists():
 dst=P/'reference_source/SCUT_LICENSE';dst.open('xb').write(license.read_bytes())
report=dict(epoch=time.time(),passed_CPU_reference_port=True,original_source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),port_path=str(target),port_SHA=hashlib.sha256(target.read_bytes()).hexdigest(),SCUT_ballistic_function_body_normalized_AST_exact=True,differential_cases=cases,actual_wheel_to_body_geometry_target_mapping_fixture=True,example_fixture=dict(step_top_m=.27,actual_body_to_lowest_wheel_m=.22,margin_m=.02,body_reference_peak_m=.51),example_not_actual_MOD4_qualified_target=True,no_assist_force_or_airreset_or_action_or_GPU=True,not_installed_or_SDK_qualified_or_trained=True,source_step_up_default_max_m=.25,explicit_MOD4_step270_task_required_instead_of_blind_SCUT_step_up_default=True,limits='Reference mathematics and synthetic target mapping only. Actual scene queries, contact IDs, leg geometry trajectory feasibility, full reward weights and runtime adapter still require qualification.')
(B/'reports/H1_STEP270_SCUT_BALLISTIC_REFERENCE_AST_AND_DIFFERENTIAL_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(report,indent=2));print(json.dumps(report))
