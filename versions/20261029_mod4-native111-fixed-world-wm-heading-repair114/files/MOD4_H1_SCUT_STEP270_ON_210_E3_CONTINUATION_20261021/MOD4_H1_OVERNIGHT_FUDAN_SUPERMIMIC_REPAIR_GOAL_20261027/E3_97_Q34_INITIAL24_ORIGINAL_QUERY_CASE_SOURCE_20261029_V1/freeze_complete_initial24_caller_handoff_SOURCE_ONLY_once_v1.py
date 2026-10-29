"""Freeze only saved text/source, never existing binary inputs."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,x):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False)
def main():
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes());proof=json.loads((B/'ACTUAL_SELECTED_INITIAL24_COMPLETE_CALLER_SOURCE_CPU_PROOF.json').read_bytes());assert proof['passed']
 for row in m['files']:
  p=Path(row['local_path'])
  if p.parent==B:assert p.stat().st_size==row['bytes'] and H(p.read_bytes())==row['SHA'],row['relative']
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),str(p))
 (B/'reports').mkdir(exist_ok=True)
 entry='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v4_exactEntryReceipt.py'
 worker='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
 first='read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py';terminal='collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py'
 put('FUTURE_TASK_FIELDS_PENDING_ACTUAL_TARGET_ADMISSION.json',dict(status='SOURCE_ONLY_NOT_AN_ACTUAL_TASK_OR_GRANT',target_root=m['target_root'],num_envs=20000,controls=24,warmup_controls=24,maximum_worker_seconds=1680,source_SHA=m['model_SHA'],original_Adam=866060,original_LR=.0002562890625000001,initial_diagnostic_only=True,maximum_selected_IDs_per_recipe=2,query_observer_SHA=H((B/'e3_declared_fall_existing_query_observer_v1.py').read_bytes()),future_actual_fields_not_fabricated=['actual_CPU_report_SHA','actual_CPU_waited_proof_SHA','known72_readonly_authority','actual_private_parent_identity','actual_private_GPU_EX_held_by_parent'],no_GO_or_writer=True))
 text=f'''E3 initial24 original-query diagnostic — FROZEN / SOURCE ONLY / UNUSED

Selected entry: {entry}
Entry SHA: {H((B/entry).read_bytes())}
Future target: {m['target_root']}
Manifest: {mf.name} / {H(mf.read_bytes())} / {len(m['files'])} rows.
Selected worker: {worker} / {H((B/worker).read_bytes())}

Purpose is the ORIGINAL E3 20k fullrestore sequence: original74JSON-bank/qerr0, independent original nearest NPZ pose-index34 placement, original write requests, original queue.apply results, ORIGINAL control-end closure_errors cached pos/quaternion/result. 2 IDs/13recipe, first16 queue ticks and original queries<=192, <=256rows/16MiB. Exactly24 mean-action controls(.48s) /192physics/48feedback; original5-control spawn grace retained. This narrow window does NOT cover original3s request or.5s stable recovery, skill acceptance or complete WM data. Full20k domain chosen to preserve D1-D7; noN1/4096 projection or normalization/optimizer updates.

Source/model1cd99995…7c84b8 /17Adam866060 /LR.0002562890625000001 /RSL43090 /400N EACH /2.5ms TGS32/4 /50Hzx8 unchanged. True entry runtime/isaac/mod4/train_E3_fullstate_v1.py SHA9799d348…1260. Original learning hook rescue_training.learn binds work before original ns.main(), no productionlearner. Hookb7cf6da…c48 copied exactly from frozen priorpackage; install BEFORE ns.main()/original resume. Original get_dof_limits read supplies bind_limits without an extra query. Original actor/vec.step loop AST exact except range600->24; inverse bytes restores old worker.432 original runtime/model/asset manifest rows equal. No NPZ/model/raw/USD stat/hash/content read in this source preparation; numeric q34 qualification alreadycompleted separately(oneNPZ), not repeated.

Existing actual same210 V4 CPU and originalwait bytes preserved/pinned, not relabelled newload. New target metadata validates real installed SDK/RSL/math, source/asset/allpostcopySHA and selected freshCPU API fixture; PTdecode0. Freshsynthetic originalplace/closure/queue fixture tested locally Torch2.14CPU (NOT target2.10).6 negatives reject missing/extra observer calls, wrongwindow and learner/optimizer/train calls. Two LOCAL test-only mistakes (same-line AST order / selecting wrong for-loop) and fullerrors/source retained; finalselected proof PASS. Originalfrozenpackages/false untouched.

Runtime requested joint/root pose is NOT actual backend postwrite FK/manifold. Original closure query is at control end, NOT pre-firstphysics/every2.5ms. Missing postwrite/substep state remains UNKNOWN; no sole-cause inference. Original2mm per-env termination, cooking/asset/DR/seed/RNG/physics/actions unchanged. The hook onlyoriginalgetter/write/apply passthrough; normal original errors propagate, diagnostic errors explicit invalid; all methods restored before Appclose. Actual target diagnostic invalid/retention reported separately, not fake success.

Future caller (ROOT must review/coordinate seriallease/freshLOCALCIM first):
 python -u -B "{B/entry}" [--known72-binding-json <exact-current-known-owner-binding.json>]
 Omit binding only for a genuinely actual CNone boundary; never insert historical CNone or fabricate active binding. Existing strict-memory 72readonly→close→210 original pinned route; control route.PY alias mapped exactly to canonical workerpython3.12. Fresh mountEF3105C85DD986BD/rw, user-light free>15669MiB/util<=30, privateEX/RAM32GiB/disk25GiB unchanged. Onlyown newcache/config paths, other processes/cache untouched. No Cwrite/GO/writer.

FIRST: {first} --actual-startup-json <newactualstartup.json> --actual-startup-SHA <actualSHA>
 Single360s wait; requires fullrestore/native24 plus final query receipt or originalerror/terminal; explicit source-SHA file loader/PurePosixPath, no Windowsimplicit import. First primary success does NOT imply wholeplant/skill.
NORMAL: {terminal} same args; original sup1800 remaining<=900 local+remote and850wait unchanged. Worker1680 unchanged. Fullown UTF8+SHA/stat-integrity, exactknown identities/out/originalwait/private release, largeNPZ/gz statmetadataonly. Source/caller original errors preserve rc0-vs-result semantics. A24-control healthy process can finish early; normalcollector gate is not bypassed. No repeated old once.

Current actual target admission/CUDAfullrestore/native24/querydiagnostic all PENDING. Reports directory exists; selected unused entry/first/normal not executed. Root ordinaryGitpending, no child trial/tag. After handoff child returns to requested E0V2 saved-text review, no automatic remote execution.
'''
 with (B/'HANDOFF_FROZEN_COMPLETE_E3_INITIAL24_ORIGINAL_QUERY_SOURCE.md').open('x',encoding='utf8',newline='\n') as f:f.write(text)
 rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  assert p.suffix in ('.py','.json','.md','.txt','.log'),str(p)
  raw=p.read_bytes();rows.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw),archival_status='ordinaryGit_PENDING_root'))
 index=dict(status='FROZEN_SOURCE_ONLY_UNUSED_TARGET_ADMISSION_PENDING',scope='one20k_initial24_original_query_diagnostic_no_learning',target_root=m['target_root'],manifest_SHA=H(mf.read_bytes()),selected_entry=entry,selected_worker=worker,selected_first=first,selected_normal=terminal,local_source_SHAs={p.name:H(p.read_bytes()) for p in B.iterdir() if p.is_file() and p.suffix=='.py'},saved_files=rows,files_excluding_index=len(rows),no_remote_model_NPZ_raw_or_GPU_calls=True,all_actual_target_qualification_pending=True)
 name='FROZEN_E3_Q34_INITIAL24_COMPLETE_SOURCE_INDEX_V1.json';put(name,index)
 print(json.dumps(dict(index=name,index_SHA=H((B/name).read_bytes()),files=len(rows)+1,selected_entry=entry,entry_SHA=H((B/entry).read_bytes()),worker_SHA=H((B/worker).read_bytes()),manifest_SHA=H(mf.read_bytes()))))
if __name__=='__main__':main()
