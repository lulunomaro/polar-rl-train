"""Prepare new386 readers without starting or changing training."""
from second50_io import *

assert not (D/'read_second50_actual.py').exists()
text=(PRIOR/'read_wave50_actual.py').read_text(encoding='utf8')
text=text.replace('from wave50_io import *','from second50_io import *').replace('import supervise_wave50_independent_scope_once as own','import supervise_wave50_second_bounded_once as wrapper\nown=wrapper.prior').replace("'WAVE50_ACTUAL_'","'SECOND50_ACTUAL_'")
(D/'read_second50_actual.py').write_text(text,encoding='utf8')
text=(PRIOR/'verify_formal_startup_save_cpu_actual.py').read_text(encoding='utf8')
changes={
'from wave50_io import *':'from second50_io import *',
'import supervise_wave50_independent_scope_once as own':'import supervise_wave50_second_bounded_once as wrapper\nown=wrapper.prior',
'*e1_WAVE50_independent_observation_*':'*e1_WAVE50_second_bounded_observation_*',
'own.SOURCE_SHA':'wrapper.INIT_SHA',
'len(freeze)==384':'len(freeze)==386',
'actual_source_count=384':'actual_source_count=386',
"assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition']":"assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition']",
"and c['explicitly_new_command_scope']":"and not c['explicitly_new_command_scope']",
'actual_initial35_to50_CUDA_fullstate_roundtrip_and_episode_plus_one':'actual_same50_CUDA_fullstate_roundtrip_and_episode_plus_one',
"'WAVE50_OWN_STARTUP_CPU_ACTUAL_'":"'SECOND50_OWN_STARTUP_CPU_ACTUAL_'",
}
for before,after in changes.items():
 assert before in text,before
 text=text.replace(before,after)
(D/'verify_second50_startup_save_cpu_actual.py').write_text(text,encoding='utf8')
for name in ('read_second50_actual.py','verify_second50_startup_save_cpu_actual.py'):
 compile((D/name).read_text(encoding='utf8'),str(D/name),'exec')
save('READONLY_READERS_PREPARED.json',dict(epoch=time.time(),source386=True,strict_same50_not_initial_transition=True,source_checkpoint_SHA=SOURCE_SHA,future_missing_manifest_or_save_is_legal_pending=True,no_GPU_or_controller_or_budget_mutation=True))
print('Prepared readonly386 actual and saved-startup readers')
