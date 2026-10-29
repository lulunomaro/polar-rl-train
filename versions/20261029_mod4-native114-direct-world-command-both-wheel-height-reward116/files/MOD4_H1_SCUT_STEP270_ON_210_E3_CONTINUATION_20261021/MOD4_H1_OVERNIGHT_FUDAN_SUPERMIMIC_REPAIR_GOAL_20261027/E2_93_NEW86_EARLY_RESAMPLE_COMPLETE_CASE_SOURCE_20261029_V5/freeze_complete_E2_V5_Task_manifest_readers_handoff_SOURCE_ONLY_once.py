"""Freeze saved source/reports; existing binary inputs remain metadata only."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;OLD=B.parent/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4'
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 mf=B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes());proof=json.loads((B/'ACTUAL_E2_V5_COMPLETE_SELECTED_SOURCE_CPU_AND_PRODUCER_CONTRACT_PROOF.json').read_bytes());assert proof['passed']
 for r in m['files']:
  p=Path(r['local_path'])
  if p.parent==B:assert p.stat().st_size==r['bytes'] and H(p.read_bytes())==r['SHA'],r['relative']
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),str(p))
 (B/'reports').mkdir(exist_ok=True)
 entry='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v4_originalHeight.py';worker='evaluate_E2_adapted93_new86_frozen900_once_v1.py';helper='e2_early_original_resample_observer_v2_complete.py';instances='e2_observed_command_instances_v1.py';first='read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py';normal='collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py'
 put('FUTURE_E2_V5_TASK_SCHEMA_SOURCE_ONLY_ACTUAL_FIELDS_PENDING.json',dict(status='SOURCE_ONLY_NOT_AN_ACTUAL_TASK_OR_GO',kind='MOD4_E2_ADAPTED93_NEW86_EARLY_RESAMPLE_COMMAND_INSTANCES_V5',target_backend='new86',target_root=m['target_root'],source_SHA=m['model_SHA'],num_envs=20000,controls=900,warmup_controls=100,steady_controls=800,simulated_seconds=18,maximum_worker_seconds=1680,maximum_supervisor_seconds=1800,original_Adam=859300,original_LR=.00022500000000000002,domain_kind='E2_WORLD_MOVING_SIGNED4',worker_SHA=H((B/worker).read_bytes()),early_observer_SHA=H((B/helper).read_bytes()),command_instances_SHA=H((B/instances).read_bytes()),first360_normal_remaining900_wait850=True,no_optimizer_steps=True,command_instance_producer_metadata_only=True,full_WM_tap_included=False,future_actual_fields_not_fabricated=['actual_CPU_report_SHA','actual_CPU_waited_proof_SHA','known72_readonly_authority','actual_private_GPU_EX_held_by_parent','actual_private_parent_identity'],declared_source_manifest_SHA=H(mf.read_bytes())))
 put('SOURCE_LOOKUP_NAME_ERRORS_PRESERVED.json',dict(original_GetContent_error='e0_profile_domain_telemetry_v1.py path does not exist',actual_manifest_resolved_name='e0_long_command_domain_telemetry_v1.py',unused_optional_second_guess_error_not_executed=True,original_missing_readonly_CODE_assembly_trace='LOCAL_READER_SOURCE_BINDING_ORIGINAL_ERROR_*.json retained',missing_only_source_reconciliation='bind_exact_E2_reader_producer_and_case_source_SOURCE_ONLY_once_v5b_missing_CODE.py',no_SDK_model_host_or_GPU=True))
 text=f'''E2_93 NEW86 early-resample COMPLETE case — FROZEN SOURCE / UNUSED

Selected local source entry: {entry}
Entry SHA {H((B/entry).read_bytes())}
NEW target root {m['target_root']}
Input manifest {mf.name}: {len(m['files'])} files /SHA {H(mf.read_bytes())}
Worker {worker} /SHA {H((B/worker).read_bytes())}
Early helper {helper} /SHA {H((B/helper).read_bytes())}
Instance component {instances} /SHA {H((B/instances).read_bytes())}

This is the complete SOURCE caller, Task/manifest, targetmetadata/finite supervisor, first and normal readers for a new observation purpose. It is NOT actual target admission/GPU execution. Old E2V4 was real complete900; its original initial-unknown phase labels/absent command-instance metric remain unchanged. Frozen earlycomponent d23e9036… supplied exact E2-specific reset/resample/write+sensor/E2resume passthrough; no E0sampler/amplitude transplanted. Actual E2 moving yaw remains±4, world-progress.5, pure1..4pi, original12s transition,12..16 timer/global+private RNG/sampler unchanged.

Retained source/model b3ae94df…56ea1e1 /RSL42822 /17Adam859300 /LR literal.00022500000000000002 /STD/norms/D1-D7,20k900controls18s/100warm800steady,400N EACH/50Hzx8/2.5ms TGS32/4/PD/DR/meanactor clip6 and originalterm conditions. Original419 runtime/model/asset manifest rows unchanged. Worker inverse bytes returns old E2V4 source exactly, and entire original900 numerical actor/vec.step loop AST identical. No added actor/learner/RNG/reset/resample/physics. No per-env4096projection/normalizer migration, no extra precision/health gates.

Earliest hook installed before ns.main/build_env/postrestore. Actual CommandTerm.reset/_resample/compute plus E2 sampler/checkpoint/sensor source must be read from CURRENT clone at targetmetadata; no old210reference masquerades as a new target read. Actual existing same86 E2V4 full900 proof +qualified wholemodel CPU witness reused,0PTdecode in this NEWmetadata purpose. New metadata additionally checks original trueentry train_E2_full_resume_v1.py/e002234d…3812, CLI parser/actual SDK inheritedflags, rescue_training.learn patch inside main ordering, dependency closure and worker→supervisor→first/normal native24 receipt graph. TargetSDK/RSL/math/USD/bank74/fullpostcopySHA/TD.14.1/selected constructor and actual method freshCPU lifecycle remain mandatory. Local proof Torch2.14CPU/TD.15.1 does not equal target2.10cu128/TD.14.1 proof.

Only real E2 resume→sensor newreset→one20000-ID resample/write at physics0/counter1/phase0/timer12..16 with valid original E2saved private-state receipt can be adopted. Changedtimer/commands, latehook, missingE2source remain leftcensored. Observation records actual write phase; adopts only observer buffers after panel construction before firstactor. Newbook opens original initial boundary at control0; resample closes original instance BEFORE original sampler then opens next only after actual return; reset closes previous and increments OBSERVER episode before original reset's nestedresample. Original env reset itself still once/unmodified. No cross-reset completion credit.

Command-instance fields separate sampled boundary control from first/last ACTUALLY acted controls.0control records have first/last=-1 and never count complete. Resample-to-resample requires observed start +positivecontrols; reset/windowend incomplete. Perprofile events/uniqueenv/acted/zero/leftcensor/reset/windowend/full12 transition counts and errors retain true E2labels; sampled2pi moving world-cycle progress is separately measured, never substituted for complete command lifetime/body-v MAE. Newbook reuses generic bookkeeping arithmetic but imports E2catalog and raw E2observed signedyaw4. No numerical skill pass tolerances invented; no fullskill graduation or completeWMdataset.

Streaming JSONL producer paths (no unlimited retention):
 frozen_regression/E2_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl
 frozen_regression/early_original_resample/E2_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl
 Each .PRODUCER_INDEX_ACTUAL.json records exactpath/bytes/rows/sourceSHA/fullstreamSHA while writing; max256MiB, instance records<=4N, retention explicit. Default normalreader fetches JSON index +JSONL stat ONLY, no contents/hash/download. Both expected indexes and missing/partial status are explicit. Selected original fulltext remains fullUTF8/stat/SHA; NPZ/gz/PT only producer/statmetadata. Actualaction/queue/DR snippets do NOT make a complete127-state WMdataset.

Source CPU PASS: real saved E2 methods with260 synthetic buffers/825 originalcompute steps/RNG+return identity;7early negatives, actual selected E2Panel constructor/physical/begin/requested/terminal/after with original flatheight API; source CLI/dependency/receipt closure;6wrongworker/learner negatives; fresh instance lifecycle15closed=10acted+5zero/5complete/3actedreset/2actedwindow,2transition complete pre12bins; actual JSONL index reader tested with ALL JSONL content reads blocked. One metadata label in the method fixture was corrected after proof by exactsingle-keyword inverse extension (originalsource retained); no numerical change/modelreload/rerun. Local assembly missing declared CODE file error +missing-only repair/source and lookup name error allretained. Full446 input rows need actual postcopy check; none of old binaries were read/stat/hashed for source/Git preparation.

Future root execution ONLY after source review/freshLOCALCIM/globalseriallease/currentauthority/resources:
 python -u -B "{B/entry}" [--known72-binding-json <current-exact-owner-binding.json>]
 root sends single noecho stdin JSON with host/user/password to existing reviewed entry; secret memoryonly, neverargv/file/output. Original72 readonly→close→one pinned86SSH8adc87…c788b, no overlapping SSH. ActualcurrentCNone or exactknownactiveowner allowed, no historicalCNone. Project-only HOME/TMP/XDG/cache under NEWtarget; direct proven clone glibc loader unchanged; no pip/globalenv changes. Fresh GPU90a66…6d3 free>15669MiB/util<=30 (userlight policy), privateEX/RAM32GiB/disk25GiB, original1680worker/1800supervisor/ownwait/out/release unchanged. No ledger/accountwrite/GO/secondwriter.

First: {first} --actual-startup-json <NEWactualreport> --actual-startup-SHA <actualSHA>
 One360s wait for originalCUDA fullrestore/native24(24/192/48+legs/wheels192 trace1..24) AND earlyadoption receipt, or originalerror/terminal; physical24 and actualearly status separately reported. No current continuous-alive/skill inference from snapshot.
Normal: {normal} sameargs. Original supervisor1800 remaining<=900 LOCAL+remote,850wait; no early900 bypass or repeatedfirst. All originalpartial/rc/error kept (rc0 alone notpass), exactknownPID/create/exe/argv/root only/no unknownprocess/GPUquery inreader. Manifest-bound explicit imports avoid Winlongpath; POSIX remote identity paths remaincorrect. Reportsdirectory exists. Entry/first/normal allUNUSED; targetmetadata/fullrestore/first/900coverage and producercontents remainPENDING. Root ordinaryGitpending; no childtrial/tag. After handoff idle, no automatic remote/GPU action.
'''
 with (B/'HANDOFF_FROZEN_COMPLETE_E2_V5_EARLY_RESAMPLE_COMMAND_INSTANCE_CALLER.md').open('x',encoding='utf8',newline='\n') as f:f.write(text)
 # Generated fresh CPU artifacts: preserve producer SHA metadata, never rehash raw forGit.
 producers={}
 for p in B.rglob('*.PRODUCER_INDEX_ACTUAL.json'):
  d=json.loads(p.read_bytes());producers[str(Path(d['path']).resolve())]=d
 fresh=proof['actual_selected_constructor_API']['fresh_synthetic_output'];producers[str(Path(fresh['path']).resolve())]=fresh
 saved=[];artifacts=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  if p.suffix in ('.jsonl','.gz','.npz','.pt','.usd','.zip'):
   d=producers.get(str(p.resolve()));assert d is not None,'Missing existing fresh producer metadata, do not rehash '+str(p)
   artifacts.append(dict(path=str(p),bytes=d['bytes'],SHA=d['SHA'],scope='fresh_CPU_synthetic_producer_metadata_only',not_reopened_or_rehashed_for_archive=True));continue
  assert p.suffix in ('.py','.json','.md','.txt','.log');raw=p.read_bytes();saved.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw),archive_status='ordinaryGit_PENDING_root'))
 baseidx=json.loads((OLD/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V4.json').read_bytes())
 index=dict(status='FROZEN_SOURCE_ONLY_COMPLETE_CALLER_UNUSED_ACTUAL_TARGET_PENDING',target_stage=m['target_root'],manifest_local_filename=mf.name,manifest_SHA=H(mf.read_bytes()),source_model_SHA=m['model_SHA'],clone_receipt_SHA=baseidx['clone_receipt_SHA'],actual_clone_CUDA_SDK_receipt_SHA=baseidx['actual_clone_CUDA_SDK_receipt_SHA'],selected_entry=entry,selected_first=first,selected_normal=normal,executable_source_SHAs={p.name:H(p.read_bytes()) for p in B.iterdir() if p.is_file() and p.suffix=='.py'},readonly_source_SHAs={n:H((B/n).read_bytes()) for n in ('E2_frozen_actual_receipts_readonly_CODE_v4.py','run_E2_new86_readonly_secure_stdin_v4.py',first,normal)},saved_files=saved,fresh_synthetic_artifacts_metadata_only=artifacts,files_excluding_index=len(saved),no_original_binary_model_NPZ_raw_SDK_host_GPU_read=True,original419_runtime_model_asset_rows_unchanged=True,new_actual_target_and_GPU_admission_pending=True,original_oldcases_once_and_false_unchanged=True)
 name='FROZEN_E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V5.json';put(name,index)
 print(json.dumps(dict(index=name,index_SHA=H((B/name).read_bytes()),textfiles=len(saved)+1,fresh_artifacts_metadata_only=len(artifacts),entry=entry,entry_SHA=H((B/entry).read_bytes()),manifest_SHA=H(mf.read_bytes()),inputs=len(m['files']),worker_SHA=H((B/worker).read_bytes()))))
if __name__=='__main__':main()
