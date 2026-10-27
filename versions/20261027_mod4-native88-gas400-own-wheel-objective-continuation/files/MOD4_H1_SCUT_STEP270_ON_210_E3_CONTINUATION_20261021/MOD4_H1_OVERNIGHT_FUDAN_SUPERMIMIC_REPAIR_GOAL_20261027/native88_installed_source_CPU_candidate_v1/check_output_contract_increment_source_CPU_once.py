"""Output-declaration increment; no previous fixture, model or SDK execution."""
from pathlib import Path
import sys,json,copy,ast,traceback
D=Path(__file__).resolve().parent;sys.path[:0]=[str(D),str(D.parent/'native88_two_available_H1_runtime_protocol_source_v1')]
from native88_source_guard_v1 import validate_output_native_contract,H
def main():
    v=dict(original_physics_and_success_unchanged=False,changed_plant700_to_nominal400=True,native_objective_changed=True,original_clock_solver_geometry_physical_V8_reward_command_success_unchanged=True,native_all_models_norms_threeopts_global_counters_restored=True,fresh_physics_replay_history=True,fresh_control_warmup=64,new_window_world_only_iterations=64,minimum_new_WM_steps_before_first_newPi=640)
    assert validate_output_native_contract(v);rows=[dict(name='honest changed-plant/objective output',passed=True)]
    for key,value in [('original_physics_and_success_unchanged',True),('native_objective_changed',False),('original_clock_solver_geometry_reward_command_success_unchanged',True),('minimum_new_WM_steps_before_first_newPi',0)]:
        bad=dict(v,**{key:value})
        try:validate_output_native_contract(bad)
        except ValueError as e:rows.append(dict(name=key,passed=True,rejected=str(e)))
        else:raise AssertionError('accepted bad output '+key)
    for f in D.glob('*.py'):ast.parse(f.read_bytes())
    value=dict(passed=True,count=len(rows),scope='new output contract metadata + final source AST only',checks=rows,models_read=0,actual_SDK_GPU=False,
        final_payload_source_pins={name:H(D/name) for name in ('native88_source_guard_v1.py','target_native88_source_sdk_cpu_v1.py','native88_installed_cpu_helpers_v1.py')})
    with (D/'OUTPUT_CONTRACT_INCREMENT_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(passed=True,count=len(rows))))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (D/'OUTPUT_CONTRACT_INCREMENT_SOURCE_CPU_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc()),f,indent=2)
        raise
