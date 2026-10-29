"""Freeze source and saved/fresh-synthetic reports only; no host or old binary IO."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
mf=B/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes())
selected=[r for r in m['files'] if Path(r['local_path']).parent==B]
for r in selected:
 p=B/r['relative'];assert H(p)==r['SHA'] and p.stat().st_size==r['bytes']
proof=json.loads((B/'reports/LOCAL_SELECTED_SOURCE_AST_CONSTRUCTOR_INSTANCE_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['old_PT_raw_USD_NPZ_reads']==0
# Actual target metadata witness checks are executed against saved JSON, without target imports.
cpu=ast.parse((B/'E0_new86_target_source_SDK_metadata_admission_v1.py').read_bytes());main=next(n for n in cpu.body if isinstance(n,ast.FunctionDef) and n.name=='main')
start=next(i for i,n in enumerate(main.body) if isinstance(n,ast.Assert) and isinstance(n.test,ast.BoolOp) and "w['passed']" in ast.unparse(n))
end=next(i for i,n in enumerate(main.body) if isinstance(n,ast.Import) and any(x.name=='torch' for x in n.names))
w=json.loads(Path(next(r['local_path'] for r in m['files'] if r['relative']=='E0_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json')).read_bytes());scope=dict(w=w,MODEL_SHA=m['typed_source_SHA'])
exec(compile(ast.Module(body=main.body[start:end],type_ignores=[]),'<selected-target-E0-actual-witness-asserts>','exec'),scope)
bad=[]
for name,value in [('Adam_step',641201),('stored_RSL_iteration',17),('final_adaptive_optimizer_LR',.0001)]:
 x=json.loads(json.dumps(w));x['review'][name]=value
 try:exec(compile(ast.Module(body=main.body[start:end],type_ignores=[]),'<negative-E0-witness>','exec'),dict(w=x,MODEL_SHA=m['typed_source_SHA']))
 except AssertionError:bad.append(name)
 else:raise AssertionError('Bad saved E0 witness accepted')
put('reports/SELECTED_TARGET_CPU_WITNESS_SCHEMA_ACTUAL_SAVED_JSON_POSITIVE_NEGATIVE.json',dict(passed=True,scope='actual selected target-CPU witness assert AST on existing saved small JSON, no target/model read',passed_actual_E0_nested_review_schema=True,negative_cases=bad,no_extra_PT_or_GPU_or_SDK=True))
clone=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json'
sdk=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json'
entry='upload_admit_detach_NEW86_E0_final82_long_command_secure_stdin_UNUSED_once_v1.py';worker='evaluate_E0_adapted82_new86_frozen1000_once_v1.py'
readnames=('E0_frozen_actual_receipts_readonly_CODE_v1.py','run_E0_new86_readonly_secure_stdin_v1.py','read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py','collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py')
all_source={r['relative']:r['SHA'] for r in selected if r['relative'].endswith('.py')}
stage='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0'
text=f'''Selected E0 source-only handoff (UNUSED, 2026-10-29)

Entry: {entry}
SHA256: {H(B/entry)}
Target: {stage}
Input manifest: {mf.name}, SHA256 {H(mf)}, {len(m['files'])} files / {sum(r['bytes'] for r in m['files'])} bytes.
Source: E0 adapted89D final82, {m['typed_source_SHA']},14,031,973B; existing wholeCPU1364e84c…; 17 Adam states step641200, RSL iteration31984, final LR .00038443359375000017.

Run root secure noecho stdin only after fresh seriallease/resource/authority review:
  python -u -B <thisdir>/{entry} [--known72-binding-json <fresh actual owner/run/go JSON>]
Only stdin JSON host/username/password. Original72 read-only CNone or exact current-known-owner binding, close72, then pinned86. No new writer/GO/Cwrite. Target existing directory refused; all HOME/XDG/TMP/cache/state/log/checkpoints project-owned; proven clone direct glibc loader; no pip/global writes.

Design: original N20k strict D1-D7 and source4096 projection REJECTED; 1000controls/20s (100warm,900steady), original20s physical episodes, original12..16s command resampling. Worker1680/supervisor1800 unchanged. Saved E2V4 throughput linear estimate1012.703s; not guarantee, W35 prior906/1680 partial retained. Both 4096/40s and20k40s are NOT_SELECTED; no checkpoint population migration.

True original entry runtime/isaac/mod4/train_chassis_pd_resume_ppo.py/f7ab426f…; CLI/real entry learner import INSIDE main/worker rescue_training.learn patch before main/static dependency closure checked. Frozen mean actor only; no optimizer/norm update. Original STD/model/norm/17Adam fingerprints before and literal equality after; original D1-D7 restore chain/CUDA RNG/queue/reset contracts unchanged.

E0 original domain: body-frame straight vx[-1.5,1.5], actual-zero standing source flag .1, pure .3 (within-pure transition1/3), moving .2 with signed yaw ABS1..2 rad/s (NOT E2 ±4); pure abs1..4pi; moving world-direction reference .5m/s via body cos projection. Original12s ramp/hold/brake/stop/reverse schedule; source-bound rate/transition proof. Authored flat root-height original API/fallback, no injected ground, no E2/native-H1 capture attribute required. Original task runtime terms/params retained: orientation .75rad, floor chassis contact50N, closure2mm per-env, mimic .05rad, low_base -1 disabled, timeout20s; these are environment terms, no invented MAE skill thresholds.

Telemetry: per original profile/whole,warm,steady population-control denominators, unique exposed/terminated/truncated envs, per-reason events. Moving measured same-command/episode signed2pi sampled window displacement/time vs integrated command reference is separate from instantaneous body-v errors/cos^2. Transition per-bin error sums and denominators. NEW observed command instances: initial start UNKNOWN/left-censored; hooks passthrough actual resample/reset once; known resample→resample counts separate from reset/window-end incomplete and sampled2pi windows, per-env/uid/episode records and complete-instance error denominators. Zero complete commands or missing phase exposure remains PENDING;20s cannot promise complete12..16s instance coverage for every env. Instance record cap80k (4×20k), explicit retention flag; selected domain trace256MiB cap; not full WM data. No extra actor/RNG/SDK/raycast/physics calls.

Local actual selected constructor physical/begin/requested/terminal/after+real original CPU queue lifecycle, reset/resample observer, positive/negative source call guard, actual writer→sup→first/normal receipt graph and E0 saved witness assert AST PASS. Local Torch2.14CPU/TD0.15.1 differ from target2.10cu128/TD0.14.1; TARGET API/wholeCPU-witness metadata admission and actual CUDA fullrestore/native24 remain UNEXECUTED. Existing full-model witness reused without PT CPUreload. All source preparatory errors and outputs retained.

First: {readnames[2]} --actual-startup-json <actual report> --actual-startup-SHA <actual SHA>; one360s remote wait/420s channel; require actual24controls/192physics/48feedback, legs192+wheels192 queueapply, trace1..24, RewardManager24×dt.02 plus source/core/17Adam/LR.
Normal: {readnames[3]} same actual startup arguments; local+remote supervisor+1800 remaining<=900, original850s wait, exact known creation/exe/argv/cwd, waited/out/private released/full UTF8 and binary stat-only metadata. rc0 alone not success; partial/error no promotion, no repeatfirst/launch. Actual startup identity/SHA unknown until root executes; none fabricated.

No remote/GPU/SDK/old PT/raw/NPZ/USD content reads in this source preparation. Skill qualification and complete WM dataset remain false. Root ordinary Git supplement pending; no new trial/tag. After handoff source stays immutable and child idles until a distinct parent task.
'''
(B/'HANDOFF_FROZEN_E0_N20K_LONG_COMMAND_NEW86_V1.md').write_text(text,encoding='utf8')
(B/'EXPLICIT_PENDING_SOURCE_ONLY.json').write_text(json.dumps(dict(status='FROZEN_SOURCE_ONLY_UNUSED',runtime_admission='PENDING',Git='PENDING_ROOT_ORDINARY_SUPPLEMENT',remote_GPU_model_reads=0,num_envs=20000,controls=1000,whole_seconds=20,skill_graduation=False,complete_WM_dataset=False),indent=2),encoding='utf8')
files=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  assert p.suffix.lower() not in ('.pt','.usd','.npz','.zip')
  files.append(dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),kind='fresh_synthetic_only_large_metadata' if p.suffix=='.gz' else 'complete_source_or_saved_text_report'))
index=dict(kind='FROZEN_E0_82_NEW86_N20K1000_SOURCE_ONLY_UNUSED_V1',frozen=True,epoch=time.time(),entry_filename=entry,entry_SHA=H(B/entry),target_stage=stage,source_model_SHA=m['typed_source_SHA'],manifest_local_filename=mf.name,manifest_SHA=H(mf),clone_receipt_SHA=H(clone),actual_clone_CUDA_SDK_receipt_SHA=H(sdk),executable_source_SHAs=all_source,readonly_source_SHAs={n:H(B/n) for n in readnames},local_source_fixture_passed=True,actual_target_admission_or_GPU_proof=False,old_model_read_this_preparation=0,num_envs=20000,controls=1000,worker1680_supervisor1800=True,files=files,source_errors_preserved=True,Git_status='PENDING_ROOT_ORDINARY_SUPPLEMENT',skill_graduation=False,complete_WM_dataset=False)
put('FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json',index)
print(json.dumps(dict(frozen=True,index_SHA=H(B/'FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json'),entry=entry,entry_SHA=H(B/entry),manifest_SHA=H(mf),files=len(files))))
