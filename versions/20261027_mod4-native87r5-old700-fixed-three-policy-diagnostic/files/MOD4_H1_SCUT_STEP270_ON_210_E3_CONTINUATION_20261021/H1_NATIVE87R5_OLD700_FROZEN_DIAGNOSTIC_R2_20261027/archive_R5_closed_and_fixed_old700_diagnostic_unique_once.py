"""One new actual diagnostic phase; supplement closed87, never repeat its trial."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';R=S/'reports'
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=N/'archive_native87_source_and_actual_startup_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed87_archive_definitions_only_for_new_fixed_diag',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("'fudan':'mod4-own-fudan-h1-native87-source-and-available-gpu-startup'","'fudan':'mod4-native87r5-old700-fixed-three-policy-diagnostic'")
patch("nr=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'/'reports'","nr=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'/'reports'")
patch("(p.name in {'ACTUAL_SINGLE_ATTEMPT_FRAMES.jsonl','ACTUAL_SINGLE_ATTEMPT_CONTROLS.jsonl'} and p.parent.name=='attempt' and 'actual_72' in p.parts)","(p.name in {'ACTUAL_SINGLE_ATTEMPT_FRAMES.jsonl','ACTUAL_SINGLE_ATTEMPT_CONTROLS.jsonl'} and p.parent.name=='attempt' and 'actual_72' in p.parts) or (p.name in {'ACTUAL_400HZ_31BODY_FRAMES.jsonl','ACTUAL_100HZ_CONTROLS.jsonl'} and p.parent.name=='episode' and ('actual72' in p.parts or 'missing_actual72' in p.parts))")
patch("or p.name.endswith('.json.partial')","or p.name.endswith('.json.partial') or p.name=='NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda'")
ns={'__name__':'new_fixed87R5_diag_archive_definitions_only','__file__':str(m.m.engine),'same_sha_entries':{}}
exec(compile(s,str(m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='4abf4b9f3f3745389bed1d46eeaa902f01551594' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1459
 assert git('rev-parse','trial-20261027-mod4-own-fudan-h1-native87-source-and-available-gpu-startup')=='353e675e3ff457bf505eedd483b2c637d3d26c2f'
 assert json.loads((R/'FROZEN_FIXED_THREE_SEED_ORIGINAL_GOAL_AND_MOTION_ACTUAL.json').read_bytes())['case_count']==3
 hardware=L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1'
 index=json.loads((hardware/'FROZEN_SHA_INDEX_ACTUAL.json').read_bytes())
 for row in index['files_excluding_index']:
  p=hardware/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 old=G/'versions/20261027_mod4-own-fudan-h1-native87-source-and-available-gpu-startup'
 ns['prior'](old/'COMPLETE_FILE_CAPTURE_INDEX.json')
 ns['prior'](old/'ordinary_R4_proxy_API_failure_R5_actual_native_first_policy/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 active='native88_gas400_typed_native_migration_bridge_source_v1'
 with (R/'EXPLICIT_ACTIVE88_SOURCE_PENDING_ORDINARY_CAPTURE_ACTUAL.json').open('x',encoding='utf8') as f:
  json.dump(dict(epoch=time.time(),pending=[str(L/active)],reason='one sequential helper is still authoring new typed400N migration source; capture only after frozen, do not label mutable as frozen',no88payload_Task_GO=True),f,indent=2)
 roots=[N,T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_20261027',S]+[p for p in L.iterdir() if p.is_dir() and p.name not in (active,'__pycache__')]
 extras=[p for p in L.iterdir() if p.is_file()]+[W/'AGENTS.md']+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(204,208)]
 note="""Diagnose actual native87R5 frozen policy and preserve qualified R5 closure/hardware400N correction preparation. Goal remains ACTIVE and unsuccessful.

Previous87 unique353e675e trial is consumed and protected. Its new complete closure is an ordinary supplement captured here alongside this genuinely new three-seed frozen diagnostic phase, not a repeated87 record/tag. R5 both full nativeFINAL twohostSHA/oneinitialCPU/finite WM/Pi/Critic/3optimizers/native127/runtimeorder/frozen normal86 bootstrap passed; h1 iter3317 WM33170 Pi3253 sourceae5ff918..., recovery1409/14090/1345 source870e63b6.... They are method sources, not normalPPO/E2/E3 promotion. Full completed control events are3755/748takeoff but0cross/landing/recovery in both. Original independent fees3606.00230884552+3611.930762529373=7217.933071374893, closing569553.363275528; normalduration/allout/CNone/original locksfree at collection. No model/reader/oldraw rerun for Git.

Human supplied selected gas spring400N each, extended eye200mm/stroke60mm. Native vision directly read original screenshots; unknown diameters/force curve/friction/damping remain unknown. Confirmed old asset k3500N/m with qtarget.22063944109012937 and eyeoffset.1793605597515834m gives nominal700N at200mm, not400; old limits eye152.656..214.564mm. Source qtarget is not eye length. Current own converted reference9223... max196.2484mm fits200, so the reference-exceeds200 hypothesis is refuted. Frozen source audits, nominal400 k2000 candidate and conservative upperlimit200/lowerpreserved28CPU, exact source diffs and tiny4attribute asset-authoring source are captured. They are engineering nominal calibration, no measured gas progression/damping or actual asset/SDK admission. No400N physics rollout or new training was started. New typed inherited-weights/WM-readaptation integration is explicitly pending one helper; source-only not Task/GO.

User explicitly removed Luna and requests current model native vision. Prior Luna HTTP502 produced no useful result and was not used/retried. Active skill moved to disabled-skills (credentials not read/Git), W/AGENTS preference and original bytes plus receipts captured. No restoration/OpenRouter calls.

New fixed diagnostic uses qualified selected h1 R5 model, deterministic native mean, saved normalizers fixed, three predeclared seeds20260928/29/30 freshN1, max5s/500controls/2000callbacks per case. This deliberately preserves OLD700 CONFIGURATION for diagnosis, not400N hardware acceptance or best-case selection. Optional actual SDK/physical/source/runtime order admission before actor all passed in R2. No learner/WM/optimizer training, no oldnative86/20kstate replay, no account writes or production source promotion. Unknown16828 process retained; only fresh emptyc27 used. R1 exact original source/error retained: contact getter is Warp but new recorder used strictTensor/Proxy reader, failing initialcapture BEFORE any actor/control/physics. Parent also hit ZombieProcess polling at exit. Missing-only206 proved exact own515220out/CNone/locksfree and collected the original error; no case retry at oldroot. New R2 namespace reuses original H1 Warp-to-Torch read-only adapter only for this sensor and fixes parent disappearance/zombie handling then wait. No relaxation of original strict DR tensor helper. All first wrong path/local source-patch/schema reader errors retained, not training failures.

R2 three actual cases completed all5seconds, source Pi+norms literal unchanged, takeoff/cross/landing/recovery/success all0, original done=time_out only. No badorientation/basecontact/closure/mimic/lowbase/arenaexit termination. Max bothwheel bottom13.302/9.295/12.248mm, nearest BOTH-leadingfront gap237.168/243.845/256.642mm. They show small stance extension/balance rather than effective jump-to-edge in this limited frozen mean scope. Parent/allownchildrenout, Cbytes unchanged; fixedcases no retry/cherrypick. New rawphysics/controlJSONL retained and indexed only by actualproducerSHA, compact derived arrays/plot retained/indexed. No extra raw/model/actor read for Git.

Bounded analytic check of exact original native objectivee574... on new recorded states: during request six-termtracking fraction~.814/.817/.815 despite no step event, post200 stationary~.834 while position term only.0196-.0212 and other five near1. Code has six additive reference tracking terms, no direct wheel-clearance/cross/landing reward; originalphysicalV8 is separately logged, not this optimizednative return. This confirms an objective-alignment gap, not unique causal proof or actual WM accuracy. Do not blindly launch unchangedobjective after only spring correction. Source repair/appropriate differentiable contact/geometry objective and actual source/SDK/resource/account admission remain needed before next new learning. No guaranteed fast convergence/skill claim.

Sole72 finite authority/old210retirement/strict86412.86069250107/caps3900/3600/300 and exact original fees remain. Original physical2.5ms/TGS32/4/100Hz/FP32, clip6/PD/delay/DR/dualwheel270realcross+topcontact+200callback stable recovery and original closure2mm single-envreset unchanged. No newprecision gate, kill/hotpatch/secondwriter/grant/refund or T2z. Full failed/success source/CPU/reports/monitors/licenses captured UTF8/plainordered; large arrays/models/raw/figures only realpath/bytes/existingproducerSHA. Protect all1459old tags+peels. One new actual diagnostic tag, subsequent supplements ordinary only, postGit conversation verification only.
"""
 ns['run_stage']('fudan',roots,extras,note,'Diagnose frozen native H1 standing solution and400N model mismatch')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEW_FIXED_DIAGNOSTIC_GIT_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
   json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),never_repeat_existing_record_or_tag=True),f,indent=2)
  raise
