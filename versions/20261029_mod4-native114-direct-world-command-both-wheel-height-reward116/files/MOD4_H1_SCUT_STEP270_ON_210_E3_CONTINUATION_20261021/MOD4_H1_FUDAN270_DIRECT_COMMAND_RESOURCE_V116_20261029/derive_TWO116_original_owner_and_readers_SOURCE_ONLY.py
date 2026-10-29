"""Exact source derivation of original116 finite controller; no GPU/GO execution."""
from pathlib import Path
import ast,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
old=T/'MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029/prepare_TWO114_actual_CPU_bound_original_owner_and_all_readers_SOURCE_ONLY_once.py'
s=old.read_text(encoding='utf8')
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
rep("A=L/'TWO111_FUDAN270_COHERENT_REWARD_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V2';OLDQ=L/'TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3'","A=L/'TWO114_WM_HEADING_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';OLDQ=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'")
rep("B=L/'TWO114_WM_HEADING_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'","B=L/'TWO116_DIRECT_COMMAND_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'")
rep("'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json' if seed==27 else 'NEW114_SEED28_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json'","'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json' if seed==27 else 'NEW116_SEED28_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json'")
rep("'NEW114_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json' if seed==27 else 'NEW114_SEED28_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json'","'NEW116_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json' if seed==27 else 'NEW116_SEED28_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json'")
rep("A/'reports/TWO111_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json'","A/'reports/TWO114_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json'")
rep("'TWO114_FUDAN270_WM_HEADING_'","'TWO116_DIRECT_COMMAND_WHEEL_HEIGHT_'")
s=s.replace('MOD4_TWO114_FUDAN270_WM_HEADING_2610v114','MOD4_TWO116_DIRECT_COMMAND_2610v116')
oldguard=" require(v.get('WM114_actual_installed_input_norm_readback',{}).get('passed') is True and v['WM114_actual_installed_input_norm_readback']['rows']==133 and v['WM114_actual_installed_input_norm_readback']['other165_columns_literal_unchanged'] and v['WM114_actual_installed_input_norm_readback']['normalizer_buffers_literal_unchanged'],'actual installed newWM input/norm proof')"
newguard=" require(v.get('reward116_actual_installed_readback',{}).get('passed') is True and v['reward116_actual_installed_readback']['actual_own_bank_poses']==133 and v['reward116_actual_installed_readback']['stationary_height_bonus_exact_zero'] and v['reward116_actual_installed_readback']['actual_selected_sum_literal'],'actual installed direct wheel-height116 reward readback')"
rep(oldguard,newguard)
rep("(A/'activate_TWO111_fudan270_20s_original_single_writer_UNUSED_once.py').read_text(encoding='utf8').replace('TWO111','TWO114')","(A/'activate_TWO114_fudan270_WM_heading_original_single_writer_UNUSED_once.py').read_text(encoding='utf8').replace('TWO114','TWO116')")
rep("B/'activate_TWO114_fudan270_WM_heading_original_single_writer_UNUSED_once.py'","B/'activate_TWO116_direct_command_original_single_writer_UNUSED_once.py'")
rep("B/'reports/TWO114_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json'","B/'reports/TWO116_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json'")
rep("('native88C_to_flat_migration_v1','native114_WM_heading_pins_v1')","('native88C_to_flat_migration_v1','native116_command_reward_pins_v1')")
needle="  checked.append(k)"
extra="""  for field in ('target_each_wheel_bottom_m','reward_API_SHA','command_core_SHA','source_CPU_SHA','quiet_speed_sigma_m_s','max_step_reward'):
   bad=copy.deepcopy(spec);bad['fudan_step_task']['command_reward116'][field]=None
   try:p.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([k,'command116.'+field])
   else:raise AssertionError('bad116command '+field)
  checked.append(k)"""
rep(needle,extra)
rep(".replace('MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029',N.name)",".replace('MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029',N.name)")
rep("s=s.replace('TWO111','TWO114').replace('NATIVE111','NATIVE114').replace('NEW111','NEW114').replace('closed111','closed114').replace('input_native107','input_native111').replace('continue_qualified107_coherent_world_task_reward111','continue_qualified111_fixed_world_WM_heading114').replace('mod4.native107_to_fudan270.target111.coherent_reward.v1','mod4.native111_to_fudan270.target114.WM_heading.v1')",
    "s=s.replace('TWO114','TWO116').replace('NATIVE114','NATIVE116').replace('NEW114','NEW116').replace('closed114','closed116').replace('input_native111','input_native114').replace('continue_qualified111_fixed_world_WM_heading114','continue_qualified114_direct_world_command_both_wheel_height116').replace('mod4.native111_to_fudan270.target114.WM_heading.v1','mod4.native114_to_fudan270.target116.direct_command_wheel_height.v1')")
# Existing114 observer already has its corrected N87 and WM114 readback. Add116
# checks to that same actual source location, rather than rerunning old observers.
begin=s.index("   code=rep(code,")
end=s.index("   s=assign(s,'NATIVE',code)",begin)
replacement="""   needle=\"  wm114=read(out/'WM114_ACTUAL_GPU_LOADED_NORM_AND_INPUT_READBACK_BEFORE_CONTROL.json')\"
   insertion=\"  reward116=read(out/'REWARD116_ACTUAL_GPU_RESET_POSE_AND_SELECTED_TERMS_BEFORE_CONTROL.json');assert reward116['passed'] and reward116['actual_phase_or_physics_not_mutated']\\n  assert positive['producer']['command_reward116']==spec['fudan_step_task']['command_reward116'] and positive['producer']['reward_source_SHA']==spec['fudan_step_task']['command_reward116']['reward_API_SHA']\\n\"
   code=rep(code,needle,insertion+needle)
"""
s=s[:begin]+replacement+s[end:]
rep("p.name.replace('TWO111','TWO114').replace('NEW111','NEW114')","p.name.replace('TWO114','TWO116').replace('NEW114','NEW116')")
s=s.replace('TWO114_GENERATED_GO_CLOSURE_AND_NEGATIVE_SPEC_CPU_ACTUAL.json','TWO116_GENERATED_GO_CLOSURE_AND_NEGATIVE_SPEC_CPU_ACTUAL.json').replace('FROZEN_UNUSED_TWO114_ORIGINAL_WRITER_INDEX_V1.json','FROZEN_UNUSED_TWO116_ORIGINAL_WRITER_INDEX_V1.json').replace('FROZEN_UNUSED_TWO114_FIRST_CLOSING_CPU_INDEX_V1.json','FROZEN_UNUSED_TWO116_FIRST_CLOSING_CPU_INDEX_V1.json').replace('TWO114_ACTUAL_TWO_CPU_BOUND_SOURCE_AND_ALL_READERS_FROZEN_ACTUAL.json','TWO116_ACTUAL_TWO_CPU_BOUND_SOURCE_AND_ALL_READERS_FROZEN_ACTUAL.json').replace('PREPARE114_CONTROLLER_ORIGINAL_ERROR_','PREPARE116_CONTROLLER_ORIGINAL_ERROR_')
ast.parse(s)
target=N/'prepare_TWO116_actual_CPU_bound_original_owner_and_all_readers_SOURCE_ONLY.py';assert not target.exists();target.write_text(s,encoding='utf8',newline='\n')
print('116 controller/readers preparation source derived, not executed')
