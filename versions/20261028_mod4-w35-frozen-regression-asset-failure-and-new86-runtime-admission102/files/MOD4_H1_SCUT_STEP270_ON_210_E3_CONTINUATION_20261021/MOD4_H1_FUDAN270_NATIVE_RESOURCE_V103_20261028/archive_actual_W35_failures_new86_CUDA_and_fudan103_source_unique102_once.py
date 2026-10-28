from pathlib import Path
import runpy,subprocess,json,traceback,time,os
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=runpy.run_path(str(T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/archive_actual100_failure_and101_native20_first_learning_unique_once.py'),run_name='definitions_only');s=old['s'];ID='mod4-w35-frozen-regression-asset-failure-and-new86-runtime-admission102'
for a,b in [("'fudan':'mod4-native-flat20-source99-producer-reference-repair101'","'fudan':'"+ID+"'"),("nr=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028'/'reports'","nr=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028'/'reports'")]:
 assert s.count(a)==1;s=s.replace(a,b)
ns={'__name__':'actual_W35_86_unique102_definitions_only','__file__':old['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns)
def git(*args,input=None):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').rstrip('\r\n')
ns['git']=git
def main():
 assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1471 and not git('tag','--list','trial-20261028-'+ID)
 checkpoint=L/'FROZEN_EXPERTS_210_86_COMPLETED_CHECKPOINT_20261028_V1';index=json.loads((checkpoint/'COMPLETED_ALL_SOURCE_ERRORS_REPORTS_FROZEN_INDEX_V1.json').read_bytes())
 assert index['files'] and len(index['source_folders_frozen'])==7
 for row in index['files']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes']
  if p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip'):assert ns['H'](p.read_bytes())==row['SHA']
 # Metadata for partial payload hardlinks is derived from existing manifests
 # and file identity, never from reading a model or raw asset for Git.
 A=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/payloads/seed27';priorrows={r['relative']:r for r in json.loads((A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};source=L/'TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1/current_closed101_models/h1/formal/model_final.pt';binary=[]
 for p in N.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip'):continue
  rel=p.relative_to(N);digest=None;origin=None
  if p.name=='H1_native103_qualified101_input.pt' and os.path.samefile(p,source):digest='35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f';origin='existing qualified101 producer + same physical hardlink'
  elif len(rel.parts)>2:
   suffix=Path(*rel.parts[2:]).as_posix();row=priorrows.get(suffix)
   if row and (A/suffix).is_file() and os.path.samefile(p,A/suffix):digest=row['SHA'];origin='existing101 source manifest + same hardlink'
  binary.append(dict(path=str(p),bytes=p.stat().st_size,SHA=digest,SHA_source=origin,no_binary_content_read=True))
 with (R/'SOURCE103_EXISTING_HARDLINK_PRODUCER_BINARY_INDEX_FOR_CAPTURE.json').open('x',encoding='utf8') as f:json.dump(binary,f,indent=2)
 ns['prior'](G/'versions/20261028_mod4-native-flat20-source99-producer-reference-repair101/ordinary_closed101_formals_full_curves_and_runtime_clone/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[checkpoint,*[L/x for x in index['source_folders_frozen']],L/'W35_210_N1_ASSET_COLLIDER_DIAGNOSTIC_SOURCE_V1',L/'H1_FUDAN_COMBINED_REWARD_ADAPTATION_SOURCE_V102_20261028',N,*[L/('TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V'+str(i)) for i in (1,2,3)]]
 ns['run_stage']('fudan',roots,[Path(__file__)],'''ONE unique actual phase102: W35 adapted400N50Hz frozen-regression GPU environment failures and new86 cloned-runtime CUDA/primitive SDK admission. This tag does NOT claim native Fudan103 GPU learning. W35 V1 and diagnostic-only V2 reached real SDK/reset but failed before model restore/native24; V2 persisted RuntimeError Two wheel colliders are required before app.close. Both full original false/error/logs retained. NEW bounded N1 original build_env only, no model/main/runner, one actual environment, reproduced both wheel counts0/0 and wheel_shapes=[]/articulation32. Original assertion retained; exact read-only ujitsoCollisionCooking=True/remoteCacheEnabled=False is evidence, not a proven root cause or permission to change physics. Worker actualwait0 is not environment success. All own oldV2 terminal/out and N1wait/privateEX release proofs/full UTF8 preserved. No learning GO/account charges/refund or adapted-skill graduation.

New86 original proven72 runtime bundle copied and narrowly relocated in preceding closed101 ordinary supplement. New project-environment V2B primitive probe actually returned0: metadata/Torch2.10cu128 CUDA tensor/IsaacLab cube24physicssteps at2.5ms/TGS32/4 and selected4090 passed, actual waits/selfidentities/full original logs/privateEXrelease. V1 unused preflight refused for unredirected HOME/XDG/TMP; V2 generator SyntaxError/local-restorer failure retained, selectedV2B project paths/direct copied glibc loader succeeded. SDK runtime source untouched, original dependency metadata conflicts retained, no false pipcheckpass. Cube is not MOD4 native24controls/fullstate/actual PPO readiness. NEW normal-H1 PPO86B typed400N50Hz initialCPU succeeded on new71db5543.../16879851B, complete inverse fourfield difference/fullstate/RNG preserved; original20k100Hz source0c1e, LR.00038443359375000017/17Adam832460. Runtime age+2/fullGPUrestore/native24/PPO still pending in separately active runtime source, not captured as completed training.

Root Fudan103 source preparation is included as source/CPU evidence only. Pinned publicFudan8204e853 complete original source/API/blobSHA and original text-reader errors retained. PureCPU instantaneous jump and stair-recovery formulas match upstream oracles; stateful encourage_jump contact-history counterexample retained and explicitly omitted along with native127-unavailable collision/old dq/priorprior action terms. New task uses same actual270mm authoredstep, named own hip-wheel geometry, terminal rootgoal.75/.652446 and2s request, forward.5 command, state-refreshed jump/recovery/top-placement reward, same native ownWM/imaginedBPTT architecture and original400plant/reset/RNG/physics. Original dualwheel crossing/fullfootprint/topcontact12/stable200=.5s remains exact acceptance. Virtual leg length .31/.16 are reward targets; reset-bank FK is source mapping/units evidence, not airborne dynamic feasibility. No counterfeit Fudan joint trajectory, manual force, action override or airborne reset.

Two new103 targetSDK/source initialfullnativeCPU candidates passed (actualwait0): strict WM/Pi/Critic/norms/3opts/frozenRSL832460/SDK/asset400/resetbank/reward/goal/config. Latest101 input35e165.../256232393B/global14784-147840WM-14272Pi, not old99/97 nor normalPPO. Original first source preparer descriptor native_iteration vs updates error, replacement-order assertion, original GPU-empty preflight refusal, and firstseed27 bank reader KeyError guide_roller_00 all retained. New unused namespace bank reader only matches original scut .get(name,0.) defaults, no pose/physics change. First failed targetCPU loaded native101+normal86 once before error; repaired NEWcandidate loads1+1 perrole are separately recorded, not a rerun of original101 formal initial review or for Git/statistics. No actor/WMforward, optimizer step or nativeGPU training happened.

Source-only controller V1 missing GO.goal_conditioning caught before launch; V2 preparer KeyError/malformed error reporter and partials retained, selected V3 binds actual admitted Task goal metadata. Actual generated GO-source closure/negative tests passed; original owner/common/forward bytes identical. V3 activation frozen UNUSED. Both72 selected GPUs fresh snapshots had23371MiB free but nonempty computeUUID, third-party identities not queried or disturbed. NO103 owner/GO/fee/newWM/Pi/success and no four-training-card claim. First-observer/normal900collector/twoformalreviewer for103 still explicitly pending before any GPU GO, never re-use consumed101 once. Child active future normalH1 runtime/new210cause directories excluded until freeze.

All full source/errors/false/reader failures/reports/receipts preserved. Text capture complete and ordered; binary model/raw/USD/NPZ/media only actual path/statbytes/existingproducerSHA or explicitunknown, never read/hash for Git. Same hourly mod4-10 V16, no continuousGoal. Original sole72 writer/account/reserve/caps and2.5ms/TGS32/4/native100Hz-vsPPO50Hz/400N assumptions unchanged. ONE annotation via record_experiment, protect1471 previous tagobjects/peels; push failure resumes existingobjects, never retag101/102. Future actual103 GPU phase gets its own unique once after genuine learning, not now. PostGit verification conversation only.''','Preserve W35 real collider failures and new server CUDA SDK admission')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('UNIQUE102_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True),f,indent=2)
  raise
