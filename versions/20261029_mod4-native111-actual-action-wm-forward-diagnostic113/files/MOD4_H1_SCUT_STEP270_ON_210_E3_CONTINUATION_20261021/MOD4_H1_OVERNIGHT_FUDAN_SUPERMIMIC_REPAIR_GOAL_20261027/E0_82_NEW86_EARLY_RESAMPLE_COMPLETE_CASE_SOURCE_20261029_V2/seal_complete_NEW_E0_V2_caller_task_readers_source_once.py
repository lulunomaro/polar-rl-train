"""Freeze complete SOURCE ONLY package. No model/raw/SDK/host inspection."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1';EARLY=L/'E0_EARLY_ORIGINAL_RESAMPLE_LIFECYCLE_SOURCE_20261029_V1'
ENTRY='upload_admit_detach_NEW86_E0_final82_early_command_secure_stdin_UNUSED_once_v2.py';WORKER='evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py'
INDEX='FROZEN_E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V2.json';MANIFEST='E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json'
JOB='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_EARLY_RESAMPLE_20261029v2/e0'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
m=json.loads((B/MANIFEST).read_bytes());proof=json.loads((B/'reports/COMPLETE_SELECTED_E0_V2_SOURCE_TASK_CONSTRUCTOR_METHODS_READERS_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['old_and_new_mean_numerical_For_AST_exact']
for r in m['files']:
 if Path(r['local_path']).parent==B:assert H(B/r['relative'])==r['SHA'] and (B/r['relative']).stat().st_size==r['bytes'],r['relative']
# Inverse bytes of selected worker observer-only additions against exact V1 source.
new=(B/WORKER).read_text(encoding='utf8');inverse=new
block=""" import torch,rescue_training
 import directional_spin_runtime,sensor_resume_contract
 from e0_early_original_resample_passthrough_observer_v1 import EarlyResampleObserver
 early=EarlyResampleObserver(torch,OUT/'early_original_resample',expected_n=20000)
 early.install(directional_spin_runtime.DirectionalSpinCommand,sensor_resume_contract)
"""
assert block in inverse;inverse=inverse.replace(block,' import torch,rescue_training\n')
head="  panel=E0Panel(real,torch,OUT,task)\n  early_adopted=";start=inverse.index(head);end=inverse.index('  oldterm=',start)
inverse=inverse[:start]+'  panel=E0Panel(real,torch,OUT,task);oldterm='+inverse[end+len('  oldterm='):]
line=" assert H(job/'e0_early_original_resample_passthrough_observer_v1.py')==task['early_observer_SHA']\n";assert line in inverse;inverse=inverse.replace(line,'')
block=""" finally:
  try:early.finish()
  except BaseException:put('FROZEN_E0_EARLY_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),original_error_receipts_not_replaced=True))
  put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()"""
assert block in inverse;inverse=inverse.replace(block," finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()")
baseline=(OLD/'evaluate_E0_adapted82_new86_frozen1000_once_v1.py').read_text(encoding='utf8');baseline=baseline.replace('MOD4_E0_ADAPTED82_NEW86_FROZEN_PROFILE_DOMAIN_V1','MOD4_E0_ADAPTED82_NEW86_EARLY_RESAMPLE_FROZEN_PROFILE_DOMAIN_V2')
assert inverse==baseline,'Unexpected selected worker drift outside observer/task schema'
put('reports/SELECTED_WORKER_OBSERVER_ONLY_INVERSE_UTF8_AND_NUMERIC_AST_EXACT.json',dict(passed=True,comparison='UTF8 LF source text; original raw byte SHAs retained separately',old_original_raw_SHA=H(OLD/'evaluate_E0_adapted82_new86_frozen1000_once_v1.py'),new_original_raw_SHA=H(B/WORKER),inverse_UTF8_LF_SHA=hashlib.sha256(inverse.encode()).hexdigest(),mapped_V1_UTF8_LF_SHA=hashlib.sha256(baseline.encode()).hexdigest(),inverse_bytes_equal_after_exact_declared_observer_and_task_kind_changes=True,numerical_For_AST_exact=True,allowed=['early install before ns.main','actual first-control observer adoption and small evidence','observer helper SHA task check','observer finally output/restoration','new typed Task kind'],no_model_physics_PD_DR_RNG_actor_or_loop_change=True))
readnames=('E0_frozen_actual_receipts_readonly_CODE_v2_early.py','run_E0_new86_readonly_secure_stdin_v2_early.py','read_E0_new86_FIRST_native24_early_queue_secure_stdin_UNUSED_once_v2.py','collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v2.py')
selected={r['relative']:r['SHA'] for r in m['files'] if Path(r['local_path']).parent==B and r['relative'].endswith('.py')}
clone=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';sdk=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json'
text=f'''FROZEN NEW E0 V2 complete early-resample case SOURCE ONLY

Entry {ENTRY}
SHA {H(B/ENTRY)}
Target {JOB}
Manifest {MANIFEST} SHA {H(B/MANIFEST)}; {len(m['files'])} declared inputs, {sum(bool(r['reuse_prior_samehost']) for r in m['files'])} identical sourceSHA/bytes rows eligible SAME86 V1 copy.
Worker {WORKER} SHA {H(B/WORKER)}

No execution during source preparation. New caller remainsUNUSED. Rootreview/freshLOCALCIM/globalseriallease then optional:
 python -u -B <thisdir>/{ENTRY} [--known72-binding-json <actualcurrentowner/run/go>]
One secure noecho stdin host/username/password only. First72 current originalfinite authority CNone or exactknownactive binding, strictreserve/mode/generation/budget read-only, close72; then pinned86. No newwriter/GO/Cwrite. Actual86 oldV1 terminal/full1000 proof must match knownlocal witness and oldmanifestSHA before anynewcopy. Newroot mustnotexist. Copy ONLY declared identical inputs; never oldTask/GO/log/output. Changednewsource uploaded. All486 NEWtarget inputs fullSHA aftercopy beforeCPU; zero PTdecode CPU. Clone/directglibcloader/projectHOME/XDG/TMP/cache only. Prior originalsource fullstateCPU and SAMEHOSTE0V1 actual20k1000 qualification referenced explicitly, not described as newmodelCPUload.

Exact retained numerical design: model a92c9e8d…/final82/17Adam641200/RSL31984/LR.00038443359375000017, originalSTD/norm/optimizer, originalN20k1000/20s(100warm900steady), 1680worker/1800sup plus originalownreap caps. Original2.5ms/TGS32/4/50Hzx8/100Hzfeedback, gas400/slidelimits, D1-D7/RNG/PD/meanactor/actionclip6/termination/12..16s sampler/20s physicalepisode. Actualselected For AST identical toV1; inverseUTF8bytes after only declaredobserver/Taskkind additions equalsmappedV1. No newphysical or skill thresholds. Source original originalruntime files unchanged.

Observer: installed before original ns.main/envbuild. Actualsource sensorresume restores private+globalRNG then originalenv.reset; hook only passthrough records realcommandreset/_resample. Atfirstwork, adopt only matching actualunchanged postrestore allIDs/0physics/phase0/timer/counter/modelSHA proof. Late/missing/changedtimer retainsleftcensor, no extraresample/clockchange. Actual small EARLY_POSTRESTORE receipt is published BEFORE meanactor; no policy improvement claim. New acted_instances/0-control/complete/initial-leftcensored/resetend/windowend and uniqueacted vs uniqueclosed exact denominators. Complete is observed lifetime, not invented skill success.

TARGET metadata MUST read ACTUAL cloned SDK managers/command_manager.py and envs/mdp/commands/velocity_command.py, validate requiredreset/_resample/compute AST and run selected actualmethods+E0constructor lifecycle with freshCPU buffers BEFORE App. Included210 reference methodAST is not86 proof. Actualtargetmethodreceipt/helperSHA/newTask/manifest allbound. No modeldecode CPU. Newactual GPUfullrestore/native24(24controls/192physics/48feedback,bothqueue192/trace1..24/RewardManager24*.02) stillMANDATORY; priorV1actual doesnot substitute.

First entry {readnames[2]}
Normal entry {readnames[3]}
Both --actual-startup-json <NEWactualreturnedreport> --actual-startup-SHA <actualSHA>; placeholders never fabricated. Explicit file/SHA loader, no Windowsimplicit imports. Firstone360s wait/channel420: originalrestore+native24+earlysmallreceipt or originalerror/terminal. It separately reports nativeproof and actualearlyadoption, allowinginitialunknown without fakecredit. Normal originalLOCAL+remote sup+1800remaining<=900, wait850/channel900, knowncreation/exe/argv/cwd, waited/out/privateEXreleased/fulltexts. RC0 alone notpass; partial/observererrors retained. Producer indexes JSON arefullsmalltexts; JSONL bytesstat+originalstreamSHA/index metadata only, no JSONLcontent open/hash/transfer byreader. Explicit producer path/bytes/SHA/rows/cap covers both actualinitialsampledcommands and per-instance records. NPZ/gz remainstat-only, no fullWMclaim.

LOCAL freshCPU/source testsPASS: actualselected telemetryconstructor lifecycle andrealqueueAPI, actualSDKreference methods/E0class baseline-vs-hook global/privateRNG/timer/commands/returns literal; firststartadopt/late/changedtimer negatives; newacted10/zero5/complete5/reset3/window2 accumulator; actualselectedJSONL collector reads2producerindexes/41syntheticrows and NEVERJSONLcontents; originalentryexists/CLI/learnhook/dependencies andwriter→sup→first/normal includingearlyreceipt graph; realremoteTaskguardpositive andwrongN/controls/Adam/LR rejection; numericFor AST exact. CPUfixture localTorch2.14differs target2.10; actualtargetAPI/GPUproofstillpending. One pre-execution source-builder quotingSyntaxError preserved with originalbytes, before sourcewiring; no actualruntimefault this scope.

AllpreviousV1 source/once/errors/leftcensor0complete unchanged. No old model/PT/raw/NPZ/USD/gzip or SDKenvironment/host reads during sourceprep. No newtrial/tag; rootordinarypending. Afterhandoff allselectedbytes frozen and childidle untilrootfollowup. Actualnewcase needsrootresource/authority review; thishandoff doesnot authorize childremote.
'''
(B/'HANDOFF_FROZEN_COMPLETE_E0_V2_EARLY_RESAMPLE_CALLER_TASK_READERS.md').write_text(text,encoding='utf8')
(B/'EXPLICIT_PENDING_SOURCE_V2.json').write_text(json.dumps(dict(status='FROZEN_SOURCE_ONLY_UNUSED',actual_target_SDK_method_and_GPU_case='PENDING',Git='PENDING_ROOT_ORDINARY_SUPPLEMENT',no_source_model_raw_SDK_host_reads=True),indent=2),encoding='utf8')
files=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  assert p.suffix not in ('.pt','.npz','.usd','.zip','.gz')
  files.append(dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),classification='fresh_CPU_synthetic_JSONL_not_actualpolicy' if p.suffix=='.jsonl' else 'complete_source_saved_text_or_original_error'))
index=dict(kind='FROZEN_COMPLETE_E0_V2_EARLY_ORIGINAL_RESAMPLE_CALLER_TASK_READERS_SOURCE_ONLY',frozen=True,epoch=time.time(),entry_filename=ENTRY,entry_SHA=H(B/ENTRY),target_stage=JOB,source_model_SHA=m['typed_source_SHA'],manifest_local_filename=MANIFEST,manifest_SHA=H(B/MANIFEST),old_input_manifest_SHA=H(OLD/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json'),samehost_V1_witness_SHA=H(B/'E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json'),clone_receipt_SHA=H(clone),actual_clone_CUDA_SDK_receipt_SHA=H(sdk),executable_source_SHAs=selected,readonly_source_SHAs={n:H(B/n) for n in readnames},original_model_num_envs=20000,num_envs=20000,controls=1000,worker1680_supervisor1800=True,selected_constructor_and_source_methods_CPU_passed=True,actual_target_method_AST_or_GPU_execution=False,model_decode_count_during_source_prep=0,files=files,Git_status='PENDING_ROOT_ORDINARY_SUPPLEMENT',skill_graduation=False,complete_WM_dataset=False)
put(INDEX,index)
print(json.dumps(dict(frozen=True,index_SHA=H(B/INDEX),entry_SHA=H(B/ENTRY),worker_SHA=H(B/WORKER),manifest_SHA=H(B/MANIFEST),inputs=len(m['files']),files=len(files))))
