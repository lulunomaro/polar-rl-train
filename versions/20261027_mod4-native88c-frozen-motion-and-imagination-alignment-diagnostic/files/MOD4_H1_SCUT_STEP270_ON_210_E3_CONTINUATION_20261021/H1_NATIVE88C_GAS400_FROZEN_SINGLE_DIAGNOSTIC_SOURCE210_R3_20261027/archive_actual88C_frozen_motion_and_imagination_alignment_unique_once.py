"""One genuine diagnostic phase; preserve all refusals and reference findings."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';R=S/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
base=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/archive_native88_nominal400_own_step_actual_stage_unique_once.py'
sp=importlib.util.spec_from_file_location('previous_archive_definitions_only_NOT_old_once',base);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
ID='mod4-native88c-frozen-motion-and-imagination-alignment-diagnostic'
patch("'fudan':'mod4-native88-gas400-own-wheel-objective-continuation'", "'fudan':'"+ID+"'")
patch("nr=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027'/'reports'", "nr=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'/'reports'")
patch("'.patch','.ini','.cfg'", "'.patch','.ini','.cfg','.xml','.ps1'")
patch("('actual72' in p.parts or 'missing_actual72' in p.parts)", "('actual72' in p.parts or 'missing_actual72' in p.parts or 'actual210' in p.parts)")
ns={'__name__':'new88C_actual_diagnostic_archive_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='606e96457a22863b3934008d99a7d1392ecbde85' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1461
 assert git('rev-parse','trial-20261027-mod4-native88-gas400-own-wheel-objective-continuation')=='f64656b2a31d6f3c4e4ced50262950ce8cbbd796'
 actual=json.loads((R/'FROZEN_NATIVE88C_SOURCE210_SINGLE_FINITE_RETURNED_ACTUAL.json').read_bytes())
 assert actual['actual_finite_transport_returned'] and actual['all_own_children_actual_out'] and actual['canonical_bytes_unchanged'] and actual['parent_original_error'] is None
 old=G/'versions/20261027_mod4-native88-gas400-own-wheel-objective-continuation'
 for p in old.rglob('*CAPTURE_INDEX.json'):ns['prior'](p)
 for r in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(r['SHA'],r)
 frozen=[L/name for name in ('native88C_frozen_single_attempt_source_preparation_v1','native88C_upstream_native_algorithm_and_training_ratio_source_audit_v1','native88C_actual_single_prejump_termination_alignment_source_v1','native88C_imagined_termination_boundary_alignment_candidate_v1','fudan_original_vs_MOD4_reference_visual_provenance_v1','fudan_original_vs_MOD4_reference_visual_source_identity_addendum_v1','native88C_historical_expert_WM_data_reuse_inventory_v1')]
 assert all(p.is_dir() and list(p.glob('INDEX*.json')) for p in frozen)
 A=L/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
 # The helper remains active on W35: only this explicit immutable checkpoint,
 # E0 frozen runtime, and individually indexed files can be captured now.
 checkpoint=A/'IMMUTABLE_REPORTS_CHECKPOINT_A_PENDING_GIT_v1.json'
 cp=json.loads(checkpoint.read_bytes())
 extras=[W/'AGENTS.md',T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/prepare_qualified88C_fixed400_frozen_single_binding_once.py',checkpoint]
 def gather(x):
  if isinstance(x,dict):
   p=x.get('path') or x.get('fullpath') or x.get('local_path');h=x.get('SHA') or x.get('SHA256') or x.get('sha256')
   if isinstance(p,str) and isinstance(h,str) and len(h)==64 and Path(p).is_file():
    f=Path(p);assert f.suffix.lower() not in ('.pt','.npz','.usd'), 'checkpoint must list immutable text only'
    assert hashlib.sha256(f.read_bytes()).hexdigest()==h;extras.append(f)
   for v in x.values():gather(v)
  elif isinstance(x,list):
   for v in x:gather(v)
 gather(cp)
 for name in ('E0_FROZEN_MINIMUM_ADMISSION_INDEX_v1.json','E0_FROZEN_MINIMUM_ADMISSION_HANDOFF_v1.md','E0_PPO50_gas400_finite_worker_v1.py','E0_target_source_SDK_CPU_admission_v1.py','E0_original_run_manifest_frozen_v1.json'):
  extras.append(A/name)
 extras += [T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(223,230)]
 assert all(p.is_file() for p in extras)
 put('GIT_CAPTURE_IMMUTABLE_CHECKPOINT_AND_W35_PENDING_ACTUAL.json',dict(epoch=time.time(),active_helper_folder=str(A),captured_frozen_E0_runtime=str(A/'E0_runtime50_gas400_candidate_v1'),captured_individual_immutable_texts=[str(p) for p in extras if p.is_relative_to(A)],remaining_mutable_W35_and_future_reports_explicit_pending_ordinary=True,no_mutable_directory_claimed_frozen=True))
 q=json.loads((S/'BINDING_ACTUAL72_GUARD_BOUND.json').read_bytes());model=q['source_model']
 put('REMOTE_QUALIFIED_MODEL_AND_USER_VIDEO_METADATA_ONLY_FOR_GIT_ACTUAL.json',dict(source_model={k:model[k] for k in ('path','bytes','SHA')},private_frozen_copy=dict(path=q['eval_root']+'/'+q['model_eval_relative'],bytes=model['bytes'],SHA=model['SHA'],source='existing actual R3 admission and producer source binding'),input_video=dict(path='C:/Users/lulu/Downloads/42168288822-1-192 (1).mp4',bytes=11455996,SHA=None,reason='user original full SHA not previously recorded; no read for Git'),no_binary_or_host_read_for_Git=True))
 roots=[S,T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_20261027',T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R2_20261027',T/'MOD4_FUDAN_USER_UPSTEP_VIDEO_NATIVE_VISUAL_20261027',*frozen,A/'E0_runtime50_gas400_candidate_v1']
 note='''Diagnose qualified native88C actual frozen motion, align real/imagined termination, and inspect the user-provided real Fudan upstep reference. No270mm success.

One actual fixed N1 mean-policy episode, seed20260928, nominal400N and qualified source a9bf6dca..., completed61controls/244physicscallbacks=.61s. It terminated at original bad_orientation=.75rad before public jump request, with43.0133degree tilt, bothwheelbottom peak1.2924mm and nearestbothfrontgap236.119mm; all actual step events0. Pi and normalizers literalunchanged, original72readonlyguardian held authority locks, Cbytes unchanged, own children waitedout. No learner/WM/optimizer/account mutation. S1 c27 occupied pre-App refusal and S2 root reserved code-field error before guardian/source210 are preserved; S3 exact new field fixed transport and produced this one episode. No retry or cherry-pick of physical cases. Full100Hz/400Hz raw indexed with existing producer SHA, derived arrays/videos preserved but only metadata archived.

Actual source diagnostic: realhardtilt42.9718degree versus imagined50percentfailure72.5424degree. At the same actual terminal pose old imagined continuation=.9998545096. This is a concrete termination-model mismatch, not zero-autograd or wrong-quaternion and not sole whole-training cause. A frozen source-only candidate changes only the tilt boundary to cos(.75), with exact config and actual resolved-angle admission. No candidate deployed/trained. Current UTD/batch ratios, retained native BPTT AST, contact signed-worldZ/metadata-magnitude mislabel, all failed local anchors/CPU readers retained in full. No models reread for Git.

User rejects current retarget. Provenance confirms selected oldFudan teacher was command0 standing jump, not real step ascent. Existing retarget removed90percent limb excursion and current9223 own forward/landing IK are synthesized. The new user video shows real approach, extension, airborne wheel tuck/crossing and platform recovery around38.4-39.0s in the preferred sideview;6-7s is auxiliary. All original extracted frames/PTS/producers, native visual contact sheets and slow GIF retained/indexed; no video-derived 3D joints/torques/height270 claim. Original saved Fudan body-pose visual and current own FK visual are source-aware, not new policy/physics. Correct actual MJCF/script identity differs stale local copies; original mismatches preserved.

User requests historical expert data for WM. Frozen inventory retains original domains, known72 relocations and old producer TLS/HMAC/SHA acknowledgments. First small adapter proof uses only existing derived61 real400N failed-episode transitions, pack127/next/xi31/actualclip6/all4appliedactions/done, interrow boundary pack difference0. This is no WM training and no successful jump data. Old700/400N,50/100Hz, MuJoCo/IsaacLab, DR/queue/reset domains require explicit alignment, not blind raw mixing or foreign-dynamics truth.

User authorizes one gpt6.1sol xhigh helper for E0 thenW35 PPO adaptation50Hz and400N on free REMOTE4090; no localGPU. Original frozen qualifications preserved, typed core/Adam/STD/LR/D1-D7 state preserved in separate forks. Immutable E0 runtime/worker/targetCPU source/index and14 report checkpoint captured; active W35 remains explicitly pending ordinary supplementation after freeze. No actual E0 sourceSDK admission, CUDA restore, PPO GO or training is claimed here. Original E0 run_manifest actually read once from exact known210 path,44247B/SHA1dbde597..., no oldweight read for that purpose. Earlier remote3060 read-only resource lease returned7.6s: GPUfree but Ddisk8.63GiB and worker.lockexists, no admission. Local actual5070TiLaptop busy, never used. Latest user directs expert training to4090 only. Fresh18:19GPU-only resource reader found all3remote4090 empty at snapshot; no unknownPID identity query. Preserve thirdparty work if present at future launch.

Sole72 finite authority remains generationMOD4_SINGLE_WRITER72_20261026, closed562175.5721518993 snapshot, originalGO-terminal independent sumonce3900/3600/300 and strict86412.86069250107 reserve. Old210 account permanently retired. No ledgercopy/newwriter/grant/refund/rounding/clamp/idlefee/cleanup. Physical2.5ms/TGS32/4, true270dualwheelcross/fullfootprint/topcontact/12landingcallbacks/200stablecallbacks=.5s success unchanged. No added FP64/bitwise/triangle gate; reuse old native160k and scoped tolerances. Existing hourly mod4-10 updated, Goal remains absent. Full source/errors/reports/failed classifications and immutable source checkpoints captured UTF8/orderedparts; original large files only realpath/size/existingproducerSHA. Protect1461old objects/peels; one new diagnostic trial only, pushfailure resumes existing objects. Later supplements ordinary, postGit verification conversation only.
'''
 ns['run_stage']('fudan',roots,list(set(extras)),note,'Diagnose native88C early fall, reference distortion and imagination termination mismatch')
if __name__=='__main__':
 try:main()
 except BaseException:
  put('NATIVE88C_DIAGNOSTIC_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),never_repeat_record_or_tag_resume_existing_objects=True));raise
