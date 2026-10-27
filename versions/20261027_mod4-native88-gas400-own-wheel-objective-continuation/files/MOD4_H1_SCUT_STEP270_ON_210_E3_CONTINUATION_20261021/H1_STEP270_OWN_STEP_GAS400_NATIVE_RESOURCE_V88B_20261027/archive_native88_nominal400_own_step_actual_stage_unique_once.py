"""Unique actual88 trial; preserve88A preGO failure and88B fixes/actuals. No models read."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/archive_R5_closed_and_fixed_old700_diagnostic_unique_once.py'
sp=importlib.util.spec_from_file_location('archive_fixed_diag_definitions_only_for_new88',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("'fudan':'mod4-native87r5-old700-fixed-three-policy-diagnostic'","'fudan':'mod4-native88-gas400-own-wheel-objective-continuation'")
patch("nr=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'/'reports'","nr=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027'/'reports'")
ns={'__name__':'new88_unique_stage_archive_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='ad249159f687c75caeb4f084fb79f81ef086f2ec' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1460
 assert git('rev-parse','trial-20261027-mod4-native87r5-old700-fixed-three-policy-diagnostic')=='af036c5956cb72cc73dbe5900a71c55b4de5ef5d'
 assert json.loads((R/'NATIVE88B_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json').read_bytes())['actual_owner_signed_GO_read'] is True
 prior=G/'versions/20261027_mod4-native87r5-old700-fixed-three-policy-diagnostic/COMPLETE_FILE_CAPTURE_INDEX.json';ns['prior'](prior)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 active=L/'native88_first_policy_closure_review_source_v1';frozen=active/'INDEX_SHA256_ACTUAL.json';excluded=[]
 if active.is_dir() and not frozen.is_file():excluded=[active]
 bank_active=L/'native88_gas400_reset_bank_exact_compatibility_source_v1'
 # This helper was explicitly still authoring at this capture boundary. Its
 # later complete frozen handoff is an ordinary supplement, never a new trial.
 if bank_active.is_dir():excluded.append(bank_active)
 with (R/'SOURCE_CAPTURE_BOUNDARY_ACTIVE_HELPER_PENDING_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pending_ordinary_after_freeze=[str(p) for p in excluded],no_mutable_source_claimed_frozen=True),f,indent=2)
 roots=[T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88_20261027',N]+[p for p in L.iterdir() if p.is_dir() and p.name!='__pycache__' and p not in excluded]
 extras=[p for p in L.iterdir() if p.is_file()]+[W/'AGENTS.md']+[p for p in (T/'H1_STEP270_REWARD_PATH_V1_20261022').glob('same_authorized_session_compressed_transport_v*.py') if int(p.stem.rsplit('_v',1)[1])>=208]
 note='''Actual native88 changed nominal400N plant and own-wheel task objective continuation. Goal remains ACTIVE, no270mm skill success claimed.

Human authorizes H1 repair through SuperMimic/Fudan conversion on two available4090s, preserves occupied16828. Both slots h1/source210 GPU937 and recovery/target72 GPUc27 are H1 native; no E3/E2/T2z training. One sequential6.1Sol helper, no nested/parallel. Luna removed and not used.

Qualified R5 method sources remain h1ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9 iteration3317/WM33170/Pi3253 and recovery870e63b6ef41f870109fc1c3b6d9d67fe2f472ca8436145755db5d74a7b8e404 iteration1409/14090/1345. Each formal256224393bytes. Separate normal86 source0c1edb.../17Adam832460 is frozen RSL witness only. All native modules/norms/threeoptimizers/global counters restored; new400N environment/replay/history is fresh, not exactPhysX resume. New64physicalwarmup+64windowworldonly,640minimum NEW WM before NEW Pi; old global positivePi not new progress. Source48CPU+optional firstpublication metadata and initialtarget strictrestore evidence retained. No reread oldmodels for Git.

Evidence motivating repair: actual R5 three fixed frozen mean episodes only9-13mm bothwheelbottom and24-26cm shortofedge, no task event. Original six additive tracking reward scored these failures~81-83percent, so direct own-wheel clearance/footprint/sidewall/landing/stability objective gap was confirmed, not sole rootcause proof. New45CPU qualified OwnStepDifferentiableMdpV2 uses task-dominant cost with bounded-positive.06/(1+cost), original source actions/architecture/sampler/physicalV8/hard success preserved. Old V1 negative reward and phase/braking mismatch rejected, original files retained. Differentiable authored-wheel FK agrees with new derived actual body motion; source geometry errors are diagnostic, not new physics gates. Same failed standing states score~.052 after200 vsold.834, geometricalgoal~.99977 normalized; this is source math, not training gain.

Hardware human selection400N per spring/extended eye200mm/stroke60. Old3500N/m plant nominal700N at200; new engineering k2000 with conservative200mm upperbound and original lowerbound preserves unmeasured damping/progression assumptions, does not claim a measured forcecurve. Actual72 USD CPU composed a new tiny layer, only two stiffness and two upperlimit values changed; all other prim/geometry/collider properties and original8.7MBbase exact. New private base/sublayer preserved, no original modified. Actual PhysX parameter/newpopulation/preload readback remains a mandatory precontrol/firstNEWPi condition.

All original attempts preserved.88A actualH1source/SDK/RSL/fullnative/assetCPU reached objective metadata check, then rejected tuple legname versus canonicalJSON list despite exact values/order. Noowner/node/GO/fee; bounded missing-only textreader proved CPU waitedout. Local case-insensitive Windows capture collided uppercase/lowercase STARTED names; complete original returnedJSON preserved then case-safe files reconstructed locally without remote repeat.88B only canonicalJSON roundtrip for recomputed metadata, all value/source/order/gradient tests exact; new namespace both actualinstalledSDK/fullsource/native+normalwitness strictCPU passed, no synthetic substitute.88B first activation localsys.path selected candidate rather than boundcontroller resource receipt, failed before network/owner/GO. New unused V2 changes only local import priority, same admitted runtimebytes. Two actual signedGO then passed; firstNEWPi/GPU400N proof and full ending qualification are separate artifacts when present, never inferred fromGO.

Originalsole72finitewriter/account schema/chargefunction preserved, old210 account permanently retired. Lastclosed569553.363275528; strict86412.86069250107 reserves, actualGO-terminal independent sumonce3900/3600/300. No refund/grant/rounding/clamp/idlefee/ledgercopy/clearactive/secondwriter. Original private/shared/H1lease, selected emptyGPU15669/RAM32/postcopydisk25 and expandedNTFS UUID/rw checkedfresh. New active resource/observer code uses exact knownownPID/create and selectedGPUUUID, no unknownpeer identity query. Historical inactive resource code globalprocess_iter discrepancy is documented, original bytes retained and not used by newnode. Secrets memory/stdin only; full own exe/argv/create checked.

Physics2.5ms/TGS32/4/100Hz/FP32, clip6/PD/delay/DR, original V8 and true dualwheel270cross/topcontact/12landingcallbacks/200stablecallbacks=.5s remain; single-env2mm reset and scoped1um native160k reuse, no new FP64/bitwise/triangle gate. Fullsource/errors/CPU/original false/GO/monitors captured UTF8/orderedparts; binaries only actualpathbytes/existing producerSHA, unknownSHA remains unknown. Protect all1460oldtagobjects/peels, one new actual88trial only; subsequent supplements ordinary actualHEAD. PostGit verification conversation only.
'''
 failure=R/'NATIVE88B_ACTUAL_EARLY_RESET_FAILURE_ORIGINAL_COST_ALLOUT_QUALIFIED_FOR_NEXT_PREPARATION.json';v=json.loads(failure.read_bytes());assert v['passed_original_cost_allout_only'] and v['both_failed_before_first_control_and_NEW_Pi'] and not v['formal_FINALs']
 note='''LATEST ACTUAL: both88B signedGO workers failed in FIRST env.reset before any native control/NEWPi, at original scut_flat_rescue.consistent_reset reset-bank contract hash mismatch. The gas400 import contract changed but the old unchanged reset-bank still pins the old700 contract. Original reset algorithm and hash guard rejected correctly; root omitted this dependency in source integration. CPU/SDK/model/asset checks passed but did not prove actual reset compatibility. No400N trained model/FINAL/firstPi/skill success exists. Native R5 remains latestqualified. Worker rc0 after SDK close does not override original_errortrue/finalNone.

First observer215 returned actual ownowner/nodes/workers OUT with complete primaryerrors. Its preceding CLI launch failed locally because originaltransport resets argv; new exact-bound wrapper then ran the first realobserver once. Original command also had a localgo-path spelling error; both retained, no remote repeat. One oversized local stdout selection included candidatepins and was truncated; bounded fieldselection then read savedreports only.

Separate bounded216 early-failure forensic reader verified originalCOHORT_FINAL/OWNER_EXIT/canonicalNone/allknownownpid/createout/originalprivate/shared/ownerfcntl free and ORIGINAL independently charged fees, no model/GPU/physics/policy read. This did not run/remove/change the normal900gate FINAL collector. Actual sumonce161.60727643966675, closing569391.7559990883; all normal durationflags true. No refund/rewrite/secondwriter. Failed88B cannot become a modelsource. A new exact gas-only resetbank compatibility candidate is pending one sourceCPU helper; originals must remain untouched, no hotpatch/blindrerun/88C GO. Before next launch independently require qualified R5 MODEL source and failed88B RESOURCE/cost/allout evidence. No permanent limitation or single rootcause claim.

'''+note
 ns['run_stage']('fudan',roots,extras,note,'Record nominal400N H1 objective repair and actual reset-bank admission failure')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NATIVE88_GIT_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(original_error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_never_record_or_tag_twice=True),f,indent=2)
  raise
