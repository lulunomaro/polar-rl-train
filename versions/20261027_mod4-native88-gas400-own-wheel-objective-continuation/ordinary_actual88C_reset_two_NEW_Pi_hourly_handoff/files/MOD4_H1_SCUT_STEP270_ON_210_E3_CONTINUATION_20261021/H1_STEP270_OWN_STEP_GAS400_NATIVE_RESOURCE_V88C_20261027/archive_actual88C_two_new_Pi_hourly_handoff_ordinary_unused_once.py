"""Ordinary88 supplement, no repeated record/tag, no model/GPU/host reads."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027/archive_native88_nominal400_own_step_actual_stage_unique_once.py'
sp=importlib.util.spec_from_file_location('consumed88_definitions_only_for_actualC_ordinary',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.s
def patch(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
patch("TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)","TAG='trial-20261027-'+ID;D=G/('versions/20261027_'+ID)/'ordinary_actual88C_reset_two_NEW_Pi_hourly_handoff'")
patch("nr=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027'/'reports'","nr=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027'/'reports'")
patch("assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()","assert not git('status','--porcelain') and git('tag','--list',TAG)==TAG and not D.exists()")
patch("note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'","note_file=nr/'ACTUAL88C_TWO_NEW_PI_HOURLY_ORDINARY_GIT_NOTE.md'")
patch("nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json'","nr/'ACTUAL88C_HOURLY_ORDINARY_ARCHIVE_STARTED_ACTUAL.json'")
a=s.index(' def recgit(*args):');b=s.index(" head=git('rev-parse','HEAD');",a)
s=s[:a]+" git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\\0'.join(x.encode() for x in files)+b'\\0')\n git('commit','-F',str(note_file));git('push','origin','HEAD:main')\n"+s[b:]
patch("remote['refs/tags/'+TAG+'^{}']==head","remote['refs/tags/'+TAG+'^{}']==git('rev-parse',TAG+'^{}')")
patch("len(git('tag','--list').splitlines())==old_count+1","len(git('tag','--list').splitlines())==old_count")
patch("peeled=head,total_tags=old_count+1","peeled=git('rev-parse',TAG+'^{}'),total_tags=old_count,ordinary_supplement_no_new_tag=True")
s=s.replace("D/'COMPLETE_FILE_CAPTURE_INDEX.json'","D/'ORDINARY_CAPTURE_INDEX.json'")
ns={'__name__':'actual88C_hourly_ordinary_definitions_only','__file__':m.ns['__file__'],'same_sha_entries':{}}
exec(compile(s,m.ns['__file__'],'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='0f2e606d2b123ecb46095f394259b958c559062b' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1461
 assert git('rev-parse','trial-20261027-mod4-native88-gas400-own-wheel-objective-continuation')=='f64656b2a31d6f3c4e4ced50262950ce8cbbd796'
 assert json.loads((R/'NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json').read_bytes())['passed'] is True
 assert json.loads((R/'USER_HOURLY_REPLACEMENT_GOAL_STATUS_TOOL_RESULT_ACTUAL.json').read_bytes())['actual_get_goal']['goal'] is None
 for name,expected in [('native88C_exact_reset_bank_lifecycle_source_v1','a0b97beb48b3c0ecc072211ecb2dc959166f0177f02887a2b8f5c94d593a6407')]:
  d=L/name;p=d/'INDEX_SHA256_ACTUAL.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
  for row in json.loads(p.read_bytes())['files']:
   x=d/row['relative'];assert x.stat().st_size==row['bytes'] and hashlib.sha256(x.read_bytes()).hexdigest()==row['SHA']
 prior=G/'versions/20261027_mod4-native88-gas400-own-wheel-objective-continuation'
 for path in [prior/'COMPLETE_FILE_CAPTURE_INDEX.json',prior/'ordinary_frozen_gas400_reset_bank17_next88C_plan/ORDINARY_CAPTURE_INDEX.json']:ns['prior'](path)
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 note='''Actual88C exact gas400 reset-bank repair: two true first NEW native policy publications, still no completed step-skill qualification. Ordinary supplement to consumed88trial, no newrecord/tag. Preserve all source, original local/schema failures, actualsourceSDK/CPU, actualaccount-derived resource correction, actualGO/firstPi and explicit hourly scheduling replacement.

Latest88B previously failed first reset before any native control/Pi; fee161.60727643966675/closed569391.7559990883 already settled, no refund/recharge. Native R5 model sources remain h1ae5ff918...3317/33170/3253 and recovery870e63b6...1409/14090/1345. New88C separately pins those qualified model roots and actual failed88B resource/error/normalcost/allout; never labels failed88B a model source. New target source CPU executes exact gas-reset compatibility source hook, flags computed from successful actual installed checks. Original133poses/74selection/RNG/writes/reset/2mm guard unchanged, exact fourgasattrs/400nominal unchanged. Real precontrol additionally requires original resetcache74x30 and written4096x30 q after VecEnvreset, then separate source-only bankproof is recorded with actualreset boolean. Source-only compatibility is not reclassified as GPUproof.

Both actual SDK/RSL/fullnative state/strict modules/norms/3opts/frozen normal86 witness832460/geometry/objective/reset-source/resources/originalvalidready/GO and first actualreset+400Nbackend/preload readback passed. Newrun AVAILABLE_TWO_H1_GAS400_OWN_STEP_NATIVE88C_1793081960015094500, owner525160/create1793081968.56, two nativeH1 roles only on GPU937/source210 and GPUc27/target72; occupied16828 retained. New700WM/6Pi and240completecontrols*4096=983040transitions each in first coherent publication; h1takeoff173, recovery666, bothcross/land/recovery0 at that FIRST snapshot. These are actual new-window optimizer/event records, not fullwindow result, speedgain, frozen-policy success or finalmodels. Native earlyweights not promoted/downloaded. Firstobserver220 consumed, source/model/GPU re-read not repeated for Git.

Original policy/WM/Critic/norms/3opts/globalcounters restored, fresh400Nphysical/replay/history, not exactPhysX resume. New64controls+64windowworldonly and minimum640NEWwm retained; originaloldpositivePi is not new progress. NativeV2 ownwheelheight/footprint/sidewall/contactmagnitude/stability objective is now active, reference9223 preserved. The original physicalV8/commands/clip6/PD/delay/clock2.5ms/TGS32/4/100Hz/FP32 and true dualwheel270/topcontact/12landingcallbacks/200stablecallbacks unchanged. 400N force model is nominal engineering calibration, not a measured forcecurve. No otherexpert/T2z/GPUunknownpeer work.

Original Cinstaller resource receipt stale balance label569553 despite genuine before/after sole72C569391 unchanged. Originalprotocol refused localactivation before remote/GO. Original report/controllerbytes retained; corrected new report changes ONLY that label and binds originalreceiptSHA+genuineaccount receipts; installedcode/model/CPUproof unchanged. Fresh original resources/account were then checked before actualGO. Earlier218 localrefusal and219actualGO both preserved. One read-only local ON_210E3 missingunderscore lookup is a reader typo, not training failure. Root source guard/reviewer changes and intentional source fixture history preserved, no broad runtime inventory weakening.

Current native88C fees pending, no newfinal closure claimed. Earliest original900gate BJT15:09:34.915874, save15:19:34.915874, nominalend15:24:34.915874 on2026-10-27. Actualtime is not completion proof. New exact bound collector/reviewer wrappers and transport221 prepared ONLY, neverexecuted;900local+remote gates/850owner->180h1->180recovery serial/allout/locks/originalindependentfees/fullsave/SHA and initialnewmodelCPU limits unchanged. No oldR5model re-read for analysis or Git.

Human latest explicitly replaces continuousGoal with hourly scheduled task. Same mod4-10 ACTIVE/hourly target retained. Pauseattempt returned threadhasnoGoal; actualget_goal=null verified, no Goal recreated/resumed. Full repair objective unachieved; existingfiniteGPUjobs continue their originalsave/exit/fees. Schedulechange is not skillcompletion. Fullnewsource/reports/agentfrozen/lifecycle/monitor/tool errors capturedUTF8/plainordered; binaries only realpathbytes/existingproducerSHA, no PT/raw/USD/GPU/hostread or fixture rerun forGit. Protect1461tagobjects/peels and original sole72finite ledger/old210retirement/strict86412.86069250107/caps3900/3600/300. PostGit verification conversationonly, no reportchasingHEAD.
'''
 roots=[N]+[L/x for x in ['native88C_two_available_H1_runtime_protocol_source_v1','native88C_selected_runtime_integration_source_v1','native88C_installed_source_CPU_candidate_v1','native88C_exact_reset_bank_lifecycle_source_v1']]
 extras=[L/'derive_native88C_exact_reset_and_failed_resource_source_unused_once.py',W/'AGENTS.md']+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/f'same_authorized_session_compressed_transport_v{i}.py' for i in range(217,222)]
 ns['run_stage']('fudan',roots,extras,note,'Preserve actual gas400 H1 reset and native policy updates with hourly task handoff')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ACTUAL88C_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(original_error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_repeat_record_or_tag=True),f,indent=2)
  raise
