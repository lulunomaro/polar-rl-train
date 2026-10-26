from pathlib import Path
import importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
p=J/'archive_actual_Fudan_reference_and_all_pending_SM_unique_once.py'
sp=importlib.util.spec_from_file_location('fudan_archive_definitions_only86',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("'fudan':'mod4-supermimic-fudan-jump-reference-and-pending-experts'","'fudan':'mod4-three4090-native85-resume-phase72-typed86b'")
patch("nr=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'/'reports'","nr=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'/'reports'")
patch("if suffix not in {'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.diff','.patch','.ini','.cfg'}:","if suffix not in {'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.diff','.patch','.ini','.cfg'} and not (p.name in {'LICENSE','NOTICE','COPYING'} or (p.name=='occupied_directory.json.partial' and p.parent.name=='cpu_phase_attempt_1793019412219594400' and 'H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026' in p.parts)):")
ns={'__name__':'archive_actual86b_utilities_only','__file__':str(m.engine)};exec(compile(s,str(m.engine),'exec'),ns);git=ns['git']

def main():
 assert git('rev-parse','HEAD')=='a988d60288a0f6dafd38cc443730b54b22d6c301' and len(git('tag','--list').splitlines())==1456 and not git('status','--porcelain')
 prev=G/'versions/20261026_mod4-dual72-fudan-supermimic-sdk-and-single-writer-handoff85'
 for path in [prev/'COMPLETE_FILE_CAPTURE_INDEX.json']+sorted(prev.glob('ordinary_*/ORDINARY_CAPTURE_INDEX.json')):ns['prior'](path)
 proof=json.loads((R/'THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json').read_bytes())
 assert proof['passed'] and proof['actual_finite_returned'] and proof['phase_exposure_observed']
 assert proof['targets']['e2']['native_first']['before_control']==72 and proof['targets']['e2']['native_first']['policy_updates']==59
 note='''Actual three4090 continuation from formal native85 preserves WM/Pi/Critic, all three optimizers and global iteration68/680WM/58Pi, with fresh original physical episodes and48-step replay refill. Root investigated zero-task-events in85: freshfirstPi312 and64-row replay discard the no-reset100..179jump phase; actual-source fixtures also show reset trajectories can retain exposure. SavedWM action/task gradients are nonzero; quaternion input allegation was refuted. Neither an autograd failure nor a unique root cause is claimed. Missing distance/dynamic-context/post-apex objective limitations remain separate source work.

One human-authorized GPT6.1Sol xhigh helper delivered native typed source52/52, normal H1/E3 typed source56/56 and closing source35/35 synthetic CPU checks in three frozen directories sequentially. A modelcapacity error was resumed in the same helper; no concurrent/nested/new agents. Root retains original byte guards, exact CRLF metadata2536/c6e421..., original normal worker/SDK/RSL AST and actor35/6STD/17Adam, separate native model semantics, original copy/source/resource/lock/account admission. Source-only fixtures are not actual target evidence.

All real rejections and local reader errors are preserved. Original210 root/home filesystem free0 rejected the first isolated-dependency destination before upload; expandedNTFS/rw original bind had~716GB and is used by the new325-file isolated control-dependency directory. No cleanup, oldmount changes, trainingenv changes or old210account activation. Actual source210-to72 strict original-pin SSH/direct-tcpip and exact paramiko5 CPUimport passed. Initial N86 native SDK admission loaded qualified native/bootstrap/restore then rejected missingrich dependency path in the CPUentry before owner/node/GO/fee. New86B namespace only corrects the existing pinned dependency path in that entry; actual SDK/source/native/reference/RSL/fullstate CPU passed. Local normalpayload wrong-keyword TypeError is retained; newmissing-only preparation completes E3 and finalizes H1 without repeating source models. H1/E3 target SDK and typed production source checks passed independently.

Actual86B single72 owner486429/creation1793027051.82 launched signed3GO. Single210H1 GPU937b, dual72nativeH1 GPU16828, E3 GPUc27 are three exact distinct UUIDs with fullPID/exe/argv/create verified. Original native85 source SHA94e7f272, frozen83B bootstrap8bb9869/Adam829700 and normal83BH1 plus complete85E3 are separately pinned. Old210canonical remains retired/fenced; sole72 finite original account/charge_values AST and actual independent GO-terminal costs remain unchanged/pending. Temporaryunlimited expired/0fees. No native model becomes normalE2/PPO.

Actual first NEW native policy update occurred at control72/cumulative690WM/59Pi, immutable preupdate_fullsource_3.pt140492649bytes SHA268f7fa68f2c9e5cf015e61d77bf89b19ef893a8da8d4d93297326251741b8a2 is producer metadata only, not downloaded/final/source. Actual optional phase3calls1536starts includes80starts100..135 and207horizon intersections. This proves phase exposure, not completed optimizer counts, task convergence or frozen-policy skill. Original first72rows*20k=1.44M taskevents0 are a snapshot only. Retarget Fudanpartial reference/actual30joint order verified; no reward/action/command/physics/sampling-distribution change.

First observerV1 embeddedSyntaxError occurred before metadata. V2 saved the successful owner signedGO/newPi/phase snapshot then failed a wrong direct-python argv assumption for72's approved glibc loader. V3 missing-target-only reuses cached owner/firstPi/phase evidence and validates actual approved node loader-prefix/full exe/argv/create; alltarget checks passed. Original errors and successful proofs coexist; no reader error is reclassified as trainingfailure or replayed once.

Original270mm realdualwheelcross/topcontact+200callbacks=.5s recovery standard,2.5ms/TGS32/4,H1100Hzx4/E350Hzx8,FP32,2mm per-env reset and original health/fullsave/27field stack/DEFLATE1/fullSHA/preupdatePT/atomic/retention/readonlyjournals remain. No extraFP64/bitwise/triangle gates/nativequeries, localpolicy/physics/GPU for Git, unknownpeer action, ledgercopy/refund/newwriter or oldsource reactivation.

Unused frozen three-node close source/wrappers and transport178 preserve pre-secret local900 and actualowner900 gates, owner850/node180 serial waits, exact own processlifetime text exception, complete originals/cost/allout/fullSHA transfers. Earliest2026-10-26T23:54:21.130218+08:00. Typed initial CPUreview loads eachFINAL andunique sourceonce, native all3optimizers/windowPi delta>58/frozenbootstrap separate from normal17Adamx20 checks; optionalphase is not modelgate. Closing and skill remain pending. Existing mod4-10 ACTIVE/hourly same target updated; no second watcher or remote progresspoll.

This is one new real86/86B phase; old1456 tagobjects/peels preserved, old85trial not repeated. Capture every saved source/error/partial/SDK/GO/newPi/monitor/helper report as fullUTF8 or exact prior capture reference; binary content only actualpath/bytes/existing producerSHA, no binary reread for Git. Subsequent closure/results append ordinary supplements, not a new trial/tag. PostGit verification stays in conversation.
'''
 roots=[T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026',N,T/'H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026']+[J/x for x in ('agent_native86_typed_source_worker_cpu_20261026','agent_normal86_H1_E3_typed_source_cpu_20261026','agent_three_gpu86b_closing_CPU_protocol_20261026')]
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(167,179)]
 ns['run_stage']('fudan',roots,extras,note,'Resume native Fudan SuperMimic at phase72 on three4090 with typed source guards')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('UNIQUE86B_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_second_record_tag=True),f,indent=2)
  raise
