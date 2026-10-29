"""Freeze NEW V2 saved text only; no original assets/model/stat/SDK access."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,x):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False)
def main():
 proof=json.loads((B/'ACTUAL_NEW_V2_DEVICE_ROUTE_COMPLETE_SOURCE_CPU_PROOF.json').read_bytes());assert proof['passed'] and proof['actual_CUDA_device_execution_tested'] is False
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes());rows={r['relative']:r for r in m['files']}
 for r in m['files']:
  p=Path(r['local_path'])
  if p.parent==B:assert p.stat().st_size==r['bytes'] and H(p.read_bytes())==r['SHA'],r['relative']
 domains=[
  dict(value='gas_limits original root_view.get_dof_limits return clone',index='selected env IDs',actual_evidence='V1 original RuntimeError proves targetCPU/indexCUDA',new='diagnostic_select routes index to limits.device, preserves long',physical_value_not_moved_or_clamped=True),
  dict(value='q34 cached _q gas slice vs actual selected limits',index='static gas DOF list; not tensor device index',source_evidence='E3ResetBankCache._q as_tensor(device=env.device,float32)',new='q comparison copy only to limits.device, no dtype change; original q/limits untouched'),
  dict(value='cached _quat/_minimum',index='original recipe long tensor',source_evidence='cache _geometry device follows original points/env',new='diagnostic_select uses each cached tensor.device'),
  dict(value='recovery.recipe / recovery.age / episode_length_buf',index='selected IDs',source_evidence='per-env buffers original environment device',new='diagnostic_select even if future cached return device differs'),
  dict(value='scene.env_origins / _rescue_reset_q',index='selected IDs',source_evidence='original cached buffers; no getter added',new='diagnostic_select then static xyz column index'),
  dict(value='original joint q,dq/root state write arguments',index='bool membership mask',source_evidence='original write arguments forwarded byte-for-byte/object identity as before',new='membership reference IDs moved only to ids.device; mask moved to target arg.device preserving bool; original args unmodified'),
  dict(value='original queue.apply return',index='self.ids',source_evidence='existing queue result once, original result object still returned',new='diagnostic_select of returned tensor; no extra apply/receipt call'),
  dict(value='ORIGINAL closure pos/quat cached getter values and residual result tensors',index='self.ids',source_evidence='closure_overlay original getters still once each; no extra SDK/body read',new='each tensor routes index independently to own device; original authored math unchanged'),
  dict(value='ids[isin mask] and ids[mask]',index='same-device bool',source_evidence='isin output device follows ids; both operands aligned to ids before isin',new='intrinsically same target/index domain; retained original selection'),
  dict(value='q[None], limits[:,:,0/1], quaternion static columns',index='static None/slices/python ints',source_evidence='device-independent indexing, no dynamic tensor device',new='unchanged')]
 put('COMPLETE_OBSERVER_TENSOR_INDEX_DEVICE_DOMAIN_AUDIT_V2.json',dict(passed_source_audit=True,diagnostic_dynamic_router_calls=19,domains=domains,original_cache_module_SHA=rows['runtime/isaac/mod4/e3_reset_bank_cache_v1.py']['SHA'],original_cache_dtype_float32_and_env_device=True,original_limit_getter_count_unchanged=True,actual_CUDA_routing_still_needs_NEW_GPU_purpose=True,no_old_NPZ_PT_or_target_read=True))
 (B/'reports').mkdir(exist_ok=True)
 entry='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v4_exactEntryReceipt.py';worker='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
 put('FUTURE_V2_TASK_METADATA_NOT_AN_ACTUAL_TASK.json',dict(status='SOURCE_ONLY_UNUSED_ACTUAL_CPU_AND_GPU_PENDING',target_root=m['target_root'],kind='MOD4_E3_ADAPTED97_SOURCE210_Q34_INITIAL24_DEVICE_ROUTE_V2',source_SHA=m['model_SHA'],num_envs=20000,controls=24,warmup_controls=24,maximum_worker_seconds=1680,supervisor_maximum1800=True,original_Adam=866060,original_LR=.0002562890625000001,worker_SHA=H((B/worker).read_bytes()),query_observer_SHA=proof['hook_SHA'],first360_normal900_wait850=True,pending_actual_fields=['actual_CPU_report_SHA','actual_CPU_waited_proof_SHA','actual_private_parent_identity','canonical72_current_known_readonly_authority'],no_historical_CNone_or_dummySHA=True))
 text=f'''E3 original-query INITIAL24 V2 — FROZEN SOURCE / UNUSED

Selected entry: {entry}
SHA {H((B/entry).read_bytes())}
NEW target: {m['target_root']}
Manifest {len(m['files'])} inputs /SHA {H(mf.read_bytes())}
Selected worker {worker} /SHA {H((B/worker).read_bytes())}
Hook SHA {proof['hook_SHA']}

V1 ACTUAL truth retained: CUDA fullrestore +24 controls/192physics/48feedback +legs192/wheels192 passed; physical worker waited0/allout/privateEXreleased. The query diagnostic was invalid because CPU actual DOF limits were indexed by CUDA selected IDs. Saved original first report has83records and12error strings (reported count from exact saved array; prior chat described13). V1 requested24aggregate flagFalse included the diagnostic gate; it does NOT mean24controls were not executed. No V1 source/once/false altered; original normal900collector remains independent.

Narrow fix:19 diagnostic dynamic selections route index to the TARGET TENSOR.device while retaining index original long/bool dtype (never floating target dtype). The cached q-vs-limits diagnostic comparison copies ONLY q to limits.device; it does not move/clamp/mutate original limits or cached q. The same audit covers recovery/cache/env_origins/resetq/write masks/queue returns/closure cached body/results; static slices/pythonint indexes are device independent. Cached bank._q is original float32/env.device, actual SDK limit returnCPU is proven by primary RuntimeError. No blanket allCUDA assumption.

Exact inverse source proof restores original hook bytes; install_before_resume/closure_overlay/limitclone/snapshot/finish AST unchanged. Original joint/root/apply calls once each and identicalAST. Worker differs only NEWnamespace/typedkind, not original20k mean24 numeric loop/actor/PD/actions/physics/DR/RNG/cooking/2mm-per-env reset.432 original runtime/model/asset metadata rows unchanged. No old PT/NPZ/USD/raw stat/hash/decode for source prep. Original model1cd99995…7c84b8 /RSL43090 /17Adam866060 /LR.0002562890625000001 retained. Original74bank qerr0→q34 requestedwrite→existingcontrol-end closure/query remains the diagnostic domain; no new original getter/physics/callback/forward.20k domain retained, noN1/4096 projection.24steps=.48s is INITIALdiagnostic only, not original3s request/.5s recovery acceptance.

Fresh CPU fixture ran selected original placement/closure/apply lifecycle with realCPU tensors; also device-label proxies explicitly emulate CPU<-CUDA, CUDA<-CPU, different-CUDA routing and preserve bool/long. Three negative SOURCE cases reject targetfloat dtype, direct mixed-domain indexing and missing q comparison route. This is NOT realCUDA execution and not targetAPI/GPUproof. LocalTorch2.14CPU differs target2.10cu128/TD.14.1. One local inverse test initially matched a function declaration as well as a call; saved source/trace retained, fixed test removes added helper definitions first; no runtime numerical code changed for it. Preseal18vs19 source count candidate and traces retained. Final source proof PASS.

Targetmetadata future0PT/NPZdecode retains original same210 V4 actual wholeCPU/wait pins and validates real installed SDK/RSL/math/allinputfullSHA/selected constructor plus new device-route freshCPU fixture. Actual NEW GPU fullrestore/model1/native24/query must still prove V2; no oldfirst reuse. Source-only API pass is not model/skill success. New readers keep original overall diagnostic gate and additionally publish requested24_controls_physically_completed separately, so diagnostic failures do not erase measured physical count; neither field fakes the other.

Root after review/freshLOCALCIM and seriallease only:
 python -u -B "{B/entry}" [--known72-binding-json <current-actual-owner-binding.json>]
 Original strictmemory72readonly→close→210 pinnedcontrolalias/canonicalworkerpython3.12 mapping; onlyNEWownnamespace/cache. ActualcurrentCNone if real, or exactknownactiveowner binding; never historical CNone. No writer/Cwrite/GO. Fresh mountEF3105C85DD986BD/rw, light free>15669/util<=30, privateEX/RAM32GiB/disk25GiB retained. Other tasks/cache untouched.1680worker/1800sup caps unchanged.

FIRST read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py --actual-startup-json <NEWactualstartup.json> --actual-startup-SHA <actualSHA>
 NORMAL collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py sameargs.360singlefirst; normal1800remaining<=900 +850wait local/remote unchanged. Explicit pinned file import/PurePosixPath retained. Fullown UTF8/stat/SHA/originalout/wait/private release, largeartifact metadataonly. Default collector does not read/transmit NPZ/gz/PT. Missing pre-firstphysics/postwriteFK/per-substep remainsUNKNOWN; requestedpose != actualmanifold. Diagnostic retention/error flags preserved, no sole-cause or skill/fullWM claim.

All V2 executable source is UNUSED, reportsdirectory exists. New runtime/sourceSDK/GPUdiagnostic PENDING. Root ordinaryGitpending; no child trial/tag. Completed bounded source task; idle after handoff, no automatic remote.
'''
 with (B/'HANDOFF_FROZEN_E3_INITIAL24_V2_DEVICE_ROUTE_COMPLETE_CASE.md').open('x',encoding='utf8',newline='\n') as f:f.write(text)
 saved=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  assert p.suffix in ('.py','.json','.md','.log','.txt')
  raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw,str(p))
  saved.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw),archive_status='ordinaryGit_PENDING_root'))
 index=dict(status='FROZEN_SOURCE_ONLY_UNUSED_NEW_TARGET_ADMISSION_PENDING',target_root=m['target_root'],manifest_SHA=H(mf.read_bytes()),selected_entry=entry,selected_worker=worker,selected_hook='e3_declared_fall_existing_query_observer_v1.py',local_source_SHAs={p.name:H(p.read_bytes()) for p in B.iterdir() if p.is_file() and p.suffix=='.py'},saved_files=saved,files_excluding_index=len(saved),runtime_model_asset432_rows_unchanged=True,original_V1_false_and_once_untouched=True,no_remote_or_old_model_NPZ_raw_SDK_GPU=True)
 name='FROZEN_E3_Q34_INITIAL24_DEVICE_ROUTE_COMPLETE_SOURCE_INDEX_V2.json';put(name,index)
 print(json.dumps(dict(index=name,index_SHA=H((B/name).read_bytes()),files=len(saved)+1,entry=entry,entry_SHA=H((B/entry).read_bytes()),worker_SHA=H((B/worker).read_bytes()),hook_SHA=proof['hook_SHA'],manifest_SHA=H(mf.read_bytes()))))
if __name__=='__main__':main()
