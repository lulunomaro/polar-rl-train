from pathlib import Path
import json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;G=W/'polar-rl-train';R=J/'reports';engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py';s=engine.read_text('utf8')
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'","'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','fudan':'mod4-supermimic-fudan-jump-reference-and-pending-experts'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'","nr=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("and '__pycache__' not in p.parts and not p.is_symlink()","and '__pycache__' not in p.parts and '.git' not in p.parts and not p.is_symlink()")
ns={'__name__':'fudan_reference_archive_utilities_only','__file__':str(engine)};exec(compile(s,str(engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='7d16caa0fbfb26a951e01b6d11f4abd1c2891d0d' and len(git('tag','--list').splitlines())==1454 and not git('status','--porcelain')
 ns['prior'](G/'versions/20261026_mod4-three4090-normal-experts-return-after-native82q-83/COMPLETE_FILE_CAPTURE_INDEX.json')
 proof=json.loads((R/'FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json').read_bytes());assert proof['actual_finite_returned'] and proof['own_reference_child_actual_out'] and proof['reference_returncode']==0 and len(proof['assets'])==24
 note='''New human-requested phase: use pinned Fudan Tianshu repository jump through native SuperMimic, and prepare all unfinished experts through the same demonstration/retarget/own-learning/acceptance route. Human explicitly reopens GPT-6.1 Sol xhigh delegation; two local CPU/source helpers operate without remote/GPU/Git access. This record is NOT another83 trial, nor a T2z run.

Preserve83B complete3FINAL/fullSHA/wholeCPU/normal original fees10943.796510219574/closing595256.8240613937/allout and new saved-only48-control diagnosis. H1 complete62.4M recorded transitions contains30254 takeoffs and0leadingcross/landing/recovery, not frozen-policy/permanent failure. Original pxr wrong-interpreter import and source-discovery errors retained, corrected newentry reconstructs sameUSD without physics. Source/CPU-only V10 nearedgetuck hypothesis is held after human directs SuperMimic; never installed or trained.

Public repo fixed8204e853dfd2ed06d85a322e1a998c3d20a3be2c.24selectedassets23557014bytes andtwo157656byteONNX transferred to owned72research root with primaryGitblobSHA1 and first two-endSHA256. No original binaryweights localcopy. V1 HTTP IncompleteRead after10files, V2 networkread failures after22files and binaryGitHubconnector UnicodeDecodeError preserved; V3 onlytwo missingSTL via byte mirror with exact primaryhash. No repeatmodels/knownfiledownload or oldonce. SeparateCPUvenv leaves trainingenv untouched. Original headless policy source observation/history/PD/action/torque/mode functions normalizedAST exact; UI removed, bounded original0.55s jump request and readonly logging added. OriginalXMLactualdt.002 and explicitdeclared.005 variants separately recorded. Defaultactualdt standingjump has measured relativeminimum-wheel-bottom peak.33668m and later returned support, not our270mmstep/stable recovery. .005standing highpeak/no postjumpcontacts is retained and not selected; .005forward variant lower.1461m lift retained. Allcase/control artifacts fullproducer indices, no MOD4 dynamics/GPU/worldmodel updates.

Immutable native-finalization candidate21CPU lifecycle tests/fullASTdiff/expectedfailures included, uninstalled, actual82Qcause remainsunproven. Existing failednative82Qprefix never promoted. Retarget and nextmixed84 protocol helpers remain active in two explicitly listed pending directories, to be captured by later ordinary supplements. Firstactual direct retarget111/201 failure is preserved there; constrained static261/261 V2 with amplitude0.1 is producer-reported but runtime joint ordering, lossV3 ascent-only/support-height objective, actualSDK/source/nativeCPU/resources/GO are still pending. No84Task/model/GO or Fudan-nativePi at this archive. Queue8unfinishedgroups is a plan, not allskills trained/admitted; frozenE0/W35 and qualified83 baselines retained. All physical/success/accounting/retention/no-unknownpeer restrictions remain.
'''
 roots=[T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026',T/'H1_STEP270_CLOSED83B_SAVED_REPLAY_AFTER_V8_20261026',T/'H1_STEP270_NEAR_EDGE_TUCK_V10_PREPARATION_20261026']+[J/x for x in ('source','public_sources','reports','actual_72_reference_text','actual_72_reference_artifacts','agent_native_finalization_cpu')]
 extras=list(J.glob('*.py'))+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(139,144)]
 ns['run_stage']('fudan',roots,extras,note,'Validate Fudan jump reference for SuperMimic and queue unfinished experts')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('UNIQUE_FUDAN_REFERENCE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_second_record_tag=True),f,indent=2)
  raise
