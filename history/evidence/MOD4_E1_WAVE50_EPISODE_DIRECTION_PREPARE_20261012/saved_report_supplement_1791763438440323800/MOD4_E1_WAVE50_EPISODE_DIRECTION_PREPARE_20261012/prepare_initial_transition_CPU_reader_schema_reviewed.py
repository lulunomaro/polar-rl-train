"""Correct an unexecuted reader's inherited result label; validators stay strict."""
from wave_direction_io import *
import ast
s=(D/'verify_direction_saved_PPO_cpu_actual.py').read_text()
old='actual_same50_CUDA_fullstate_roundtrip_and_episode_plus_one=True'
new='actual_old35_exact_then_new50_entry_direction_CUDA_roundtrip_and_episode_plus_one=True'
assert s.count(old)==1;s=s.replace(old,new);ast.parse(s)
p=D/'verify_direction_initial_transition_saved_PPO_cpu_actual.py';assert not p.exists();p.write_text(s,encoding='utf8',newline='\n')
save('INITIAL_TRANSITION_CPU_READER_SCHEMA_REVIEW.json',dict(epoch=time.time(),original_prepared_reader='verify_direction_saved_PPO_cpu_actual.py',original_never_executed=True,inherited_result_label_same50_was_inapplicable_to_initial35_to50_migration=True,independent_reader=p.name,strict_initial_terrain_entry_newdirection_validators_unchanged=True,no_GPU_or_physics_error_or_replay=True))
print(json.dumps(dict(independent_initial_transition_CPU_reader_prepared=True,original_unexecuted_label_error_retained=True)))
