"""Source/AST only. Do not import or execute the replay entry or SDK modules."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent.parent;W=T.parent
R=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R2_20261027'
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
paths=dict(entry=R/'native86_frozen_single_sdk_entry_v1.py',driver=R/'driver.py',worker=B/'h1_unisupermimic_step270_worker_v1.py',
 bridge=B/'source/h1_supermimic_bridge_v1.py',learner=B/'source/supermimic_vendor_v2/learner.py',policy=B/'source/supermimic_vendor_v2/networks.py',
 factory=B/'job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py',cfg=B/'job0/runtime/isaac/mod4/mod4_task.py',
 queue=B/'job0/runtime/isaac/mod4/action_delay_physics_queue.py',
 wrapper_reference=W/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018/actual_installed_RSL72_sources/isaaclab_rl/rsl_rl/vecenv_wrapper.py')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path in paths.values():ast.parse(path.read_text('utf8'),filename=str(path))
value=dict(schema='mod4.native.full_replay.entry_static_review.v1',epoch=time.time(),frozen=True,
 confirmed_required_fix='Add str(B) to sys.path before root-level environment modules import',
 additional_deterministic_wiring_error_confirmed=False,
 confirmed_correct=['factory globals/scut configure pattern','RslVec initial reset, no second explicit reset',
 'queue reset does not overwrite control_us','H1Bridge current/pack do not need runner.alg',
 'native Policy constructor and saved normalizer strict load','cfg.sim.physics and spawn.articulation_props source paths'],
 pending_runtime=['N1 actual SDK/component/profile support','fresh reset and shape/contact readbacks','closure/mimic and reference contract readbacks'],
 source_files=[dict(role=k,path=str(p),bytes=p.stat().st_size,SHA=H(p)) for k,p in paths.items()],
 reader_errors=[dict(kind='guessed mod4_env_cfg.py path missing',correction='Mod4EnvCfg is in mod4_task.py'),
 dict(kind='guessed local site-packages isaaclab_rl path missing',correction='inspected saved actual_installed_RSL72_sources wrapper'),
 dict(kind='rg literal Windows wildcard rejected',correction='searched directory with -g *.py')],
 no_PT_model_actor_SDK_GPU_SSH_ledger_Git=True,old_directories_unchanged=True,archive_status='pending root ordinary supplement')
report=D/'reports/REPLAY_R2_ENTRY_STATIC_REVIEW_ACTUAL.json'
with report.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False)
files=[dict(relative=p.relative_to(D).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file()]
index=D/'FROZEN_STATIC_REPLAY_ENTRY_REVIEW_INDEX.json'
with index.open('x',encoding='utf8') as stream:json.dump(dict(schema='mod4.native.replay.static_review.index.v1',frozen=True,files=files,excludes_only_self=True),stream,indent=2)
print(json.dumps(dict(frozen=True,index=str(index),index_SHA=H(index),files=len(files),additional_confirmed_error=False)))
