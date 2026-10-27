"""Freeze this E0 source once; never re-read old models/normalizers for Git."""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, shutil, time

HERE=Path(__file__).resolve().parent;W=HERE.parents[2]
RUNTIME=HERE/'E0_runtime50_gas400_candidate_v1'
ORIGINAL_MANIFEST=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027/E0_ACTUAL_ORIGINAL_RUN_MANIFEST_UTF8.json'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def row(path,relative=None):
 path=Path(path);return dict(path=str(path.resolve()),relative=relative,bytes=path.stat().st_size,SHA=H(path))
def put(path,data):
 with Path(path).open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
def main():
 index=HERE/'E0_FROZEN_MINIMUM_ADMISSION_INDEX_v1.json';assert not index.exists()
 # The evaluation package did not include the training-only reports freeze.
 # This missing dependency was found before target installation/GO and is
 # explicitly appended, never hidden behind the earlier457-file source report.
 freeze=RUNTIME/'reports/SOURCE_FREEZE.json';assert not freeze.exists();freeze.parent.mkdir(exist_ok=True)
 source_map={p.relative_to(RUNTIME).as_posix():H(p) for p in RUNTIME.rglob('*') if p.is_file()}
 put(freeze,dict(schema='mod4.E0.PPO50_gas400.runtime_source_freeze.v1',sha256=source_map,
                 source_report=str(HERE/'reports/E0_RUNTIME50_GAS400_OVERLAY_CPU_ACTUAL_V1.json'),
                 source_report_SHA=H(HERE/'reports/E0_RUNTIME50_GAS400_OVERLAY_CPU_ACTUAL_V1.json')))
 put(HERE/'reports/E0_TRAINING_SOURCE_FREEZE_MISSING_DEPENDENCY_FIXED_BEFORE_ADMISSION_V1.json',
     dict(epoch=time.time(),finding='Closed evaluation runtime omitted reports/SOURCE_FREEZE.json, required by original training entry at manifest assembly.',
          original457_file_overlay_report_preserved=True,actual_remote_or_GPU_failure=False,source_prequalification_fix=True,
          added_sourcefreeze=row(freeze),original_runtime_unchanged=True,Git_status='pending_root_ordinary_supplement'))
 manifest=HERE/'E0_original_run_manifest_frozen_v1.json'
 assert H(ORIGINAL_MANIFEST)=='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1'
 shutil.copy2(ORIGINAL_MANIFEST,manifest)
 # Pure source/controller-binding fixture. All resource/GO objects here are
 # synthetic and are never usable as real admission or billing receipts.
 worker=HERE/'E0_PPO50_gas400_finite_worker_v1.py'
 spec=importlib.util.spec_from_file_location('frozen_E0_guard_CPU',worker);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 start=time.time();task=dict(role='E0',source_SHA=module.SOURCE_SHA,original_source_SHA=module.ORIGINAL_SHA,
  original_run_manifest_SHA=module.MANIFEST_SHA,num_envs=20000,source_qualification_kind=module.KIND,
  canonical_authority_path=module.AUTHORITY,authority_generation=module.GENERATION,source_CPU_SHA='0'*64,
  GPU_UUID='GPU-SYNTHETIC-CPU-FIXTURE-NOT-AN-ADMISSION',actual_resource_admission=dict(compute_UUID_only_rows=0,GPU_UUID='GPU-SYNTHETIC-CPU-FIXTURE-NOT-AN-ADMISSION',GPU_name='NVIDIA GeForce RTX 4090'),
  actual_USD_gas400_composition_passed=True,run_id='SYNTHETIC_CPU_FIXTURE_ONLY')
 go=dict(source_qualification_kind=module.KIND,source_SHA=module.SOURCE_SHA,max_parent_seconds=3900,exit_headroom_seconds=300,
  original_owner_pid=1,source_CPU_SHA='0'*64,save_deadline=start+3600,learning_started_epoch=start,nominal_end_epoch=start+3900,
  GPU_UUID=task['GPU_UUID'],authority_generation=module.GENERATION,run_id=task['run_id'])
 module.guard_task_go(task,go);negatives=[]
 for field,bad in [('source_SHA','1'*64),('num_envs',256),('original_run_manifest_SHA','2'*64),('authority_generation','WRONG_GENERATION')]:
  t=copy.deepcopy(task);t[field]=bad
  try:module.guard_task_go(t,go)
  except AssertionError:negatives.append('TASK.'+field)
  else:raise AssertionError(field+' unexpectedly admitted')
 for field,bad in [('max_parent_seconds',4000),('exit_headroom_seconds',0),('original_owner_pid',0),('source_CPU_SHA','3'*64)]:
  g=copy.deepcopy(go);g[field]=bad
  try:module.guard_task_go(task,g)
  except AssertionError:negatives.append('GO.'+field)
  else:raise AssertionError(field+' unexpectedly admitted')
 t=copy.deepcopy(task);t['actual_resource_admission']['compute_UUID_only_rows']=1
 try:module.guard_task_go(t,go)
 except AssertionError:negatives.append('TASK.selected_GPU_compute_UUID_rows')
 else:raise AssertionError('compute GPU admitted')
 put(HERE/'reports/E0_WORKER_TYPED_GUARD_SOURCE_CPU_FIXTURE_V1.json',dict(epoch=time.time(),CPU_source_fixture_only=True,
  synthetic_resource_and_GO_never_real=True,passed_valid_binding=True,rejected_cases=negatives,worker_SHA=H(worker),no_GPU_remote_or_budget=True))
 runtime_rows=[];absolute_refs=[]
 for p in sorted(RUNTIME.rglob('*')):
  if not p.is_file():continue
  relative=p.relative_to(RUNTIME).as_posix();runtime_rows.append(row(p,relative))
  if p.suffix=='.py':ast.parse(p.read_bytes())
  if p.suffix in ('.py','.json','.txt','.md'):
   for number,line in enumerate(p.read_text('utf8').splitlines(),1):
    if any(token in line for token in ('/home/egde','/mnt/mod4','10.24.4.210','10.24.5.27')):
     absolute_refs.append(dict(relative=relative,line=number,text=line))
 original_bundle=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/SOURCE_BUNDLE_V2_MANIFEST.json'
 original_rows=json.loads(original_bundle.read_bytes())['file_rows'];binary=[]
 for rel,target_rel,required in [('runtime/assets/robot.usd','runtime/assets/source_700N/robot.usd',True),('runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz','runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz',False)]:
  producer=next(x for x in original_rows if x['relative']==rel)
  local=original_bundle.parent/rel
  assert local.is_file() and local.stat().st_size==producer['bytes']
  binary.append(dict(local_path=str(local),installed_relative=target_rel,bytes=producer['bytes'],SHA=producer['sha256'],
                     source_of_SHA='existing_original_bundle_manifest_not_rehashed',producer_manifest=row(original_bundle),
                     required_for_E0=required,needed_for_W35_later=not required))
 sources=json.loads((HERE/'reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json').read_bytes())
 model=sources['sources']['E0']['new_source'];p=Path(model['path']);assert p.stat().st_size==model['bytes']
 handoff=HERE/'E0_FROZEN_MINIMUM_ADMISSION_HANDOFF_v1.md'
 handoff.write_text('''# E0 frozen minimum source, target admission pending

Only remote4090 is authorized for this adaptation. No3060/laptop training. This is a new E0 50Hz/nominal400N fork; original frozen source and graduation label stay unchanged. No actual target admission, CUDA restore, PPO progress or new skill qualification is claimed.

Install all runtime rows with their relative paths, the typed E0 model as `source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt`, the frozen original manifest as `original_run_manifest.json`, and the two root Python entry files. The tiny runtime/assets/robot.usd layer requires the original700N USD at runtime/assets/source_700N/robot.usd. The binary path/size/SHA below comes from the original bundle receipt; no model/USD/NPZ was re-read for this freeze. The32MB collision NPZ is indexed explicitly but is W35-only and does not block E0.

CPU admission: `CUDA_VISIBLE_DEVICES='' <actual_remote_python> -u -B E0_target_source_SDK_CPU_admission_v1.py --job-root <new_unused_root>`. It loads only the new typed CPU checkpoint, validates the actual installed USD composition, and creates E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json. Its SHA becomes TASK/GO source_CPU_SHA. No simulator scene or GO occurs in this step.

One real72 slot: register one E0 node only. Root binds fresh actual GPU UUID with zero selected compute rows, actual resource evidence, installed source/SDK receipt, worker SHA, source SHA, new run_id and original72 generation/path. The sole original72 writer signs GO_PRODUCTION.json before the worker imports SDK. Retain original562175.5721518993 balance as snapshot only, strict remaining reserve and existing historical/pending charges; no second ledger, refund, extension or clear-active.

Worker: `CUDA_VISIBLE_DEVICES=<actual_remote4090_UUID> <actual_remote_python> -u -B E0_PPO50_gas400_finite_worker_v1.py --job-root <new_root>`. TASK/GO fields are listed in guard_task_go. The worker restores original actor35/critic38/STD/17Adam639560/LR, all D1-D7/private/global RNG, then the original one fresh reset. Its first24 controls observe192 physics callbacks,48 feedback samples,24 actual RewardManager calls at.02s, and original gas preload/backend readback before same-process PPO. Finite3900s wall cap includes load, training, save, SDK close and parent wait; save deadline3600s/exit headroom300s. Parent owns complete GO→terminal sum-once cost; this worker never writes canonical budget.

Source changes:2.5ms×8/TGS32/4,100Hz sensor feedback,20ms action queue; gamma.99² and lambda.95² preserve temporal exponents. Reward/PD/clip6/seconds-based commands and per-env2mm termination remain original. Exact same contractcbcd→517c authorizes only two gas stiffness and two upper limits. The old133-pose bank/74 selected poses is source-validated through the exact approved400 compatibility hook. No new precision or graduation threshold is introduced.

The source map omitted by the original frozen evaluation package was added before admission; the earlier457-file report and this correction are both preserved. Old210 path literals remain in inactive historical support scripts/metadata as enumerated in the JSON index; the actual E0 entry/rescue/task files have no hardcoded210 host paths. The worker obtains the original manifest RM_* values and explicitly replaces the asset and finite-stop paths. No remote connection code is called by the E0 entry.

This index freezes all E0 bytes. Further fixes must use a new candidate/version and preserve this one. W35 follows independently. Target CPU and actualCUDA readback remain necessary; reusable historical native160k evidence is not rerun. All reports are pending root Git ordinary supplementation, no new tag for this source-only preparation.
''',encoding='utf8')
 value=dict(schema='mod4.E0.frozen_minimum_admission.v1',epoch=time.time(),frozen=True,source_only=True,
  runtime=runtime_rows,worker=row(worker),SDK_CPU_admission=row(HERE/'E0_target_source_SDK_CPU_admission_v1.py'),
  original_run_manifest=row(manifest),typed_source_model=dict(model,read_for_freeze=False,producer=sources['sources']['E0']['original']['producer_path'],
   producer_SHA=sources['sources']['E0']['original']['producer_SHA'],source_qualification_report=row(HERE/'reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json')),
  binary_dependencies=binary,old210_absolute_path_literals=absolute_refs,
  active_E0_entry_task_rescue_no_hardcoded210_host_paths=True,entry='runtime/isaac/mod4/train_chassis_pd_resume_ppo.py',
  actual_target_CPU_or_CUDA_or_PPO=False,not_skill_qualified=True,original_frozen_labels_unchanged=True,
  handoff=row(handoff),freeze_producer=row(__file__),Git_status='pending_root_ordinary_supplement')
 put(index,value);print(json.dumps(dict(index=str(index),SHA=H(index),runtime_files=len(runtime_rows),worker_SHA=H(worker),binary_dependencies=binary,old_absolute_literal_count=len(absolute_refs))))
if __name__=='__main__':main()
