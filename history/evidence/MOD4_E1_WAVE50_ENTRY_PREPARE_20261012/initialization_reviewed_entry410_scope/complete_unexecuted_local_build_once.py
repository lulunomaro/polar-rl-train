"""Continue the missing local components after a strict anchor mismatch; no old stage replay."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent;R=D/'reports'
error=dict(epoch=time.time(),original_builder='build_entry_scope_once.py',failure="AssertionError: ('xy = env.scene.env_origins[ids,:2].clone()', 0)",before_target_CPU_or_GPU=True,
 local_read_lookup_errors=['train_wave50_independent_resume_ppo.py absent; actual train_wave50_full_resume_ppo.py','native_wave50_sdk_reviewed_probe.py absent; actual native_e1_wave50_scope_probe.py','stage_wave50_fullscope_cpu_once.py absent; actual stage_gpu_scope_once.py','WAVE50_147_COMPLETE_SCOPE_DECISION.json absent; actual WAVE50_147_COMPLETE_OBSERVED_SCOPE_DECISION.json'],
 all_partial_prepared_sources_retained=True,no_physical_failure_or_replay=True)
with (R/'LOCAL_BUILDER_ANCHOR_REJECTION.json').open('x') as f:json.dump(error,f,indent=2)
s=(D/'build_entry_scope_once.py').read_text();pre=s[:s.index('R.mkdir(exist_ok=True);')]
tail=s[s.index('oldreset='):]
start=tail.index('newreset=');end=tail.index('\nput(',start)
tail=tail[:start]+'''newreset=replace(oldreset,'    xy = env.scene.env_origins[ids, :2].clone()',"    from wave50_entry_runtime import reset_entry_xy\\n    xy = reset_entry_xy(env,ids)")'''+tail[end:]
tail=tail.replace("root=z['root_before_physics'];cmd=z['command'];fam=z['family']", "rows=z['rows'];root=rows[:,:,:3];cmd=rows[:,:,7:10];fam=rows[:,:,10]")
ns={'__file__':str(D/'build_entry_scope_once.py')};exec(compile(pre+tail,'<independent-unexecuted-local-components>','exec'),ns)
