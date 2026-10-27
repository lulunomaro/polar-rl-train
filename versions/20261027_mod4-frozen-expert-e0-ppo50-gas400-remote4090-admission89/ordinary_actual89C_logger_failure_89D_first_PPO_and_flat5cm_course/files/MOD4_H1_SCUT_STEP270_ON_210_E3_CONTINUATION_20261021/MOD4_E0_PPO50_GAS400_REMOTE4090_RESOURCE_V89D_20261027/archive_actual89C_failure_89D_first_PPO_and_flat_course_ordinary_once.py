"""Ordinary supplement of consumed89 trial; never record/tag again."""
from pathlib import Path
import importlib.util,json,hashlib,time,traceback,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/archive_actual_E0_50Hz_gas400_remote_source_admission89_unique_once.py'
spec=importlib.util.spec_from_file_location('consumed89_archive_engine_definitions_only',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("nr=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027'/'reports'","nr=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027'/'reports'")
patch("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)/'ordinary_actual89C_logger_failure_89D_first_PPO_and_flat5cm_course'")
patch(" and not git('tag','--list',TAG)","")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL89D_FIRST_PPO_ORDINARY_GIT_NOTE.md'")
patch("'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","'ORDINARY_FIRST_PPO_COURSE_CAPTURE_STARTED_ACTUAL.json'")
start=s.index(" rec.git=recgit;sys.argv=");end=s.index(" head=git('rev-parse','HEAD')",start)
s=s[:start]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-m',title);git('push','origin','HEAD:main')\n"+s[end:]
patch(" and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==head", "")
s=s.replace("==old_count+1", "==old_count").replace("total_tags=old_count+1", "total_tags=old_count").replace("peeled=head", "peeled=git('rev-parse',TAG+'^{}')")
s=s.replace('COMPLETE_FILE_CAPTURE_INDEX.json','ORDINARY_CAPTURE_INDEX.json')
ns={'__name__':'ordinary89_firstPPO_course_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='81fea08cc13c61e8ca7a67bf1f7dd5608def8497' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1463
 assert git('rev-parse','trial-20261027-mod4-frozen-expert-e0-ppo50-gas400-remote4090-admission89')=='4d49fbf704693600406063814ce58ea6f1ef1938'
 assert json.loads((R/'E0_FIRST_ACTUAL_4090_PPO_V5_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json').read_bytes())['passed_first_PPO']
 ns['prior'](G/'versions/20261027_mod4-frozen-expert-e0-ppo50-gas400-remote4090-admission89/COMPLETE_FILE_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 frozen=[L/'E0_PPO50_gas400_single72_controller_source_preparation_v1',L/'E0_PPO50_gas400_logger_presave_V5_source_candidate_20261027',L/'E0_PPO50_gas400_single72_V5_89D_controller_source_candidate_v1',L/'W35_PPO50_gas400_source_preparation_20261027',L/'H1_FLAT_JUMP_CURRICULUM_20261027']
 for p in frozen:assert p.is_dir()
 f=frozen[0]/'FINAL_HANDOFF_20261027/FINAL_FULL_CONTROLLER_SOURCE_INDEX_ACTUAL.json';assert hashlib.sha256(f.read_bytes()).hexdigest()=='2dbff16ea526bc0b6d5584574a3639d1e504ca25f2681a4ec0a33b191c985b5b'
 f=frozen[3]/'W35_FROZEN_MINIMUM_SOURCE_ADMISSION_INDEX_V1.json';assert hashlib.sha256(f.read_bytes()).hexdigest()=='8242c696e93883382f3dc9378ccf5fbee9a7f8d63ada08c5966aa44b9f0c9b4c'
 prompt=R/'CURRENT_ACTUAL89D_FIRST_PPO_FLAT5CM_COURSE_MONITOR_SOURCE.txt';state=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert state['prompt']==prompt.read_text(encoding='utf8').rstrip('\n') and state['status']=='ACTIVE' and state['rrule']=='FREQ=HOURLY;INTERVAL=1'
 put('HOURLY_SAME_TARGET_FIRST_PPO_AND_FLAT5CM_SOURCE_VERIFIED_ACTUAL.json',dict(epoch=time.time(),same_id='mod4-10',ACTIVE_hourly=True,prompt_exact_except_terminal_LF=True,no_Goal_creation=True,actual_first_E0_PPO=True,native_flat_course_not_yet_GPU=True))
 roots=[N,T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027',*frozen]
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(233,244)]
 note='''Ordinary supplement of the existing89 trial. Remote4090 E0 PPO50/400N firstNEWupdate actually passed; native flat-jump curriculum remains source-only, no H1 step success.

89C actualGPU fullcore/D1-D7 restoration reached work assertions but initialpresave failed in RSLlogger.save_model because writer was not initialized. No native24/newPPO/qualifiedFINAL. V5 moves only the existing writer=None statement before firstsave; inversebytes/AST and FakeLogger reproduce/fix/laterlearnwriter cases retained. OriginalV4/source/error/partial retained. Root previously missed this known initialization-order pattern; no cause was attributed to the physical policy. Original sole72writer independently charged397.61036682128906s in full, closed561777.961785078, CNone/knownownout-or-nonexecutingzombie plus parentwait/all locksfree.236 KeyError run_id and237 wrong id fallback are original reader errors;238 matches genuine ownerPID/create/cohortGO/runid/expertstart schema without ledger mutation. Its overbroad incompletebinary label is corrected only in an append-only classification report; component roundtrip artifacts remain separate from incomplete own_startup0.pt.partial, unknown SHA not invented.

Newunused89D reuses qualified typed54f model/runtime exactcopy/fullSHA, never failedpartial.239 copiedsources/V5 but failed before metadata script execution on a nestednewline source SyntaxError;240 missing-only fixes bytes newline expression and publishes actual V5 extensiona51a28...f80a without re-copy/hash/load models. Base actualfullstateCPUd06 and V4 LR migration5509 remain exact originalbytes; failed89C originalcost/allout e90b is resource-only. Frozen single-slot controller retains charge_values/owner.account/locks/finite loops, no fake second registration or secondwriter.241 actual source ready/empty4090/private/shared/authority/port checks then sole72owner544164/create1793101424.86,node544173/create1793101425.21 launched, runtime HMACtoken memory/stdin only, never disk/Task/argv/Git.

Actual242 firstmetadata passed on GPUc27eecbd: original actor35/critic38/STD/17Adam639560/LR/D1-D7/CUDA states exact; actual24controls192physicscallbacks48feedback and24 RewardManager(dt.02) calls, actualgas400backend/preload, then firstNEWPPO update1/Adam639580. Producer model_update1.pt14030712B/SHA941f77cb...6cfae indexed only, not downloaded/hashed/read. Snapshot isn't continuousalive/formalFINAL/skill. Run E0_PPO50_GAS400_SINGLE72_1793101420360133100 GO1793101428.2093573; save20:43:48.209357BJT, nominal20:48:48.209357, normalcollector earliest20:33:48.209357. Newfees pending. Firstupdate447.287s includes coldSDK/fullrestore/setup, not a matched speed comparison or proven convergence.

Normal collector243 is prepared/AST-only UNUSED with local+remote900, owner850 thennode180, originalunique fee/allout/locks/sourceFINAL producer/twohostSHA and exactlyone newformal model transfer. It never starts before thegate or writes canonical. Fullfinite wholeNEWmodelCPU qualification remains necessary before any adapted sourcepromotion; earlysave/firstPPO not skill. Source before nodewait split retained. All earlier source failures and read errors retained.

User now explicitly starts a curriculum: actualflat5cm wheelclearance and0.5s landingstability, then10/20/27cm, forwardlanding andprogressivesteps, final270dualwheelcross/fullfootprint/topcontact12+stable200 unchanged. Root source-only phase/objective math uses initial2s standing then deterministic-ID staggered requests and periodic2.5s, no fake airreset/RNGdraws. Positive rational ownwheel cost does not reward standing during flight (~.00545 vs target.06); tilted pre-request~.01995 vs upright.06 and survival boundary matches actual.75rad. These are mathematical cases, not actualmotion or learninggain. Native ownWM/imaginedrollout/BPTT adapter still needs realFK/forcebasis/actualflat event counter, advancingphase and refresheddynamiccontact context, qualifiednative model/norm/opts lineage/futuregoal/zero-horizontal-command source and actualSDK admission. No nativeflatGPU started, no claim E0PPO is SuperMimic. Real Fudan video phase/source standingjump distinction retained; no false3Dmocap/270mm measurement or oldraw/render repeat.

W35 nextsource fullyfrozen469files and actualsourceCPUfixture, separate nearest250pose34/32MBbank/genuine originalsource/G3/retainedcommands/D1-D7/STD/LR1e-5 preserved, correctloggerfirst and scalarLR guard. TargetSDK/CUDA/native24/PPO pending, never source-only=>runtime. Its entire frozenfolder and allcontroller source/test/locator/quote/errors/handoffs captured here. Current E0window remains healthy and unchanged; no hotpatch to addslot. WM data collection not run by this E0worker; checkpoints aren't transition datasets. Existing61real failure-derived adapter proof and domain-separated historicalinventory retained.

Sole72finite authority unchanged, old210permanentlyretired, strict86412.86069250107 reserve/original3900/3600/300 and independentactualGO-terminal sumonce, no refund/grant/rounding/clamp/idlefee/ledgercopy/clearactive/secondwriter. Samehourlymod4-10/noGoal and no localGPU/249training. All fullsource/errors/false/reports/monitors UTF8/orderedparts, binaries onlyrealpathbytes/existingproducerSHA. No PT/raw/USD/NPZ/GPU/hostread forGit or trainingstop forarchive. All1463oldtagobjects/peels protected, no repeatedrecord/tag. Pushfailure resumesexistingobjects, postGitverification conversationonly.
'''
 ns['run_stage']('fudan',roots,extras,note,'Preserve E0 logger failure, verify4090 PPO50 gas400 and stage low flat-jump curriculum')
if __name__=='__main__':
 try:main()
 except BaseException:put('ORDINARY_FIRST_PPO_COURSE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_commit_never_record_or_tag=True));raise
