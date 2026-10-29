"""Actual NEW113 CPU diagnostic unique archive; no model/raw/host action for Git."""
from pathlib import Path
import json,runpy,subprocess,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';R=S/'reports'
ID='mod4-native111-actual-action-wm-forward-diagnostic113'
p=runpy.run_path(str(T/'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029/archive_actual112_coherent_reward_motion_WM_unique_once.py'),run_name='definitions_only')
s=p['s']
for a,b in [("'fudan':'mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112'","'fudan':'"+ID+"'"),("nr=T/'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029'/'reports'","nr=T/"+repr(S.name)+"/'reports'")]:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
ns=dict(__name__='new113_actual_CPU_unique_capture_definitions_only',__file__=p['ns']['__file__'],same_sha_entries={})
exec(compile(s,ns['__file__'],'exec'),ns)
def git(*args,input=None):
 q=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(G),*args],input=input,capture_output=True)
 assert q.returncode==0,q.stderr.decode('utf8','replace')
 return q.stdout.decode('utf8').rstrip('\r\n')
ns['git']=git
def main():
 assert git('rev-parse','HEAD')=='e0dafe86c55b2725c655ee02a6cef275b3cf1ff6' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1478
 assert git('rev-parse','trial-20261029-mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112')=='7e4fd933ee7aed6fd8d31454527d67fe0bfc40a4'
 ns['prior'](G/'versions/20261029_mod4-native111-coherent-reward-frozen-motion-wm-diagnostic112/ordinary_E0_acceptance_review_E3_reset34_numerics/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 selection=json.loads((R/'ARCHIVE113_FROZEN_ROOT_SELECTION_AND_ACTUAL_STATUS.json').read_bytes())
 roots=[Path(x) for x in selection['roots']]
 assert all(x.is_dir() and x.is_relative_to(T) for x in roots)
 actual=json.loads((R/'NEW113_ACTUAL_ACTION_WM_WORLD_X_VELOCITY_CPU_COMPLETE_ACTUAL.json').read_bytes())
 assert actual['passed_execution'] and actual['raw_controls_reads']==actual['full_checkpoint_decodes']==1
 note='''NEW113 is a new necessary CPU-only numerical worldX/worldVx diagnostic, separate from consumed111 initialformalCPU and112 frozen physics. Human asked reward-before-use and questioned whether world-model lack of jump coverage prevents task learning. This phase validates actual action forward predictions before picking a narrow further source change. One qualified111 h1 formal SHA24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12/256235849B/global18597-185970WM-17893Pi checkpoint decode, one integrity hash pass, and one NEW112 control raw read under an explicit NEW typed purpose. Only WM constructed/forward; Pi/Critic/optimizer not constructed or forwarded, no normal86/old107/108 models/raw, SDK/physics/GPU/SSH/account action. All586-pinned-source/manifest/header/schema/clock/127state/31context/6actualexecutedaction/newpurpose gates precede model loading; exact actual summary is below. Frozen WM parameters/norms remain literal. CPU2.14 versus producerGPU2.10 is explicit, no crossdevice bitwise gate.

All eligible actual-action contiguous starts:1/8/32 horizons2000/1993/1969 windows. Use actual executed action and static context at each step with predicted state after initialreal input; no policy-resampled actions, futuretruthinjection, reset crossing or independent-sample success rate. All predictions/summary/finiteguards retained in full UTF8. ActualworldVx MAE .0074218963/.020997759/.0457328372m/s, rootX .0000958995/.0008423873/.0076828133m. Only the measured actual low-speed/sub1.2cm trajectory, not .5m/s taskdomain/270mm/counterfactual accuracy or unique model cause. First-step predictedrootZ consistency with already publishedGPU112 differs atmost2.98e-8m, a consistency observation not a new FP32mechanical threshold. No raw/model reads for statistics/Git beyond this once necessary diagnostic.

Original guessedsourcepaths, V1 summary missing parenthesis/AST and unsealed syntax refusal, V2 metadata SHA helper str-versusPath rejection before raw/model, and NEWV3 metadata-only correction retained. FinalsuccessfulV3 entry consumed; no old once reexecution. The new source-only114 ownFK counterexample finds equal old167 neuralinput features for opposite worldheading/bodyvelocity-equivalent constructed states at one fixed-world terrain point, with different wheel-front/edge approach. OldWM.step rotates outputs, so equal neuralinput is not equalworldprediction or broken free-space covariance. Pure geometric10ms constantvelocity projection is not actualPhysX/manifold or sole physical failure proof. Contact history may carry partial heading information, zero/vertical-force cases still alias.

Candidate114 changes ONLY WM.inputs two yaw-normalized redundant orientation slots1/3 by bounded .005*(cosyaw-1),.005*sinyaw, width167/constructor/step/targets/state_error AST unchanged; exactoriginalbyte inverse retained. No weights/norm tensors/threeopts/actor/critic/reward111/learner/physics/clock change;25443 syntheticSO3 input/finite-gradient/seam/bounds cases, other165columns literalunchanged, rawshift<=.01/.005 and normalizedshift<=1/.5 under originaleps.01 zero-variance fixture. No originalcheckpoint for this sourceCPU and NO actualtargetnorm/runtimeadmission/GPU/TaskGO/training or skill claim. Candidate114 is SOURCE ONLY; far-from-edge jump-bonus tasktradeoff remains separately pending. V1 CRLF literalpreparation refusal before candidatecopy/proof and NEWV2 exactnewline repair retained. CurrentqualifiedMETHOD remains111 and actual270goalnotachieved. No blindly unchanged learning or cold restart.

Old-expert same sequential child early-E0 originalresample observer proof/source plus any frozen completecaller/SDKmetadata/reader packages are captured by explicit roots below. Targetmetadata/freshresource/secure actualstart still separately required; source-only packets aren't old-expert skill graduation. OriginalE0 V1 full1000 had0complete observedresample-resample instances and60000censored/reset/window closures; preserveoldclassification/missingJSONL rather than relabel. No originalmodel/raw/NPZ/GPU/host queries for this archive, no secondwriter/canonicalcopy/fees/refund/budgetgrant. One GLOBALserialSSH and memory-only/noechoSTDIN/memfd credentials remain. Protect1478oldtagobjectsandpeels, newactualCPU113 annotatedtrialonce; pushfailure continueobjects, neverretag111/112/113. Lateractual114runtime/E0events ordinaryappend or ownactualphase policy, source-onlynoGPUtag. PostGitverificationconversationonly.
'''
 note+='\nAuthoritative actualCPU summary:\n'+json.dumps(actual,ensure_ascii=False)+'\nFrozen root/status selection:\n'+json.dumps(selection,ensure_ascii=False)
 ns['run_stage']('fudan',roots,[Path(__file__),*[Path(x) for x in selection.get('extras',[])]],note,'Measure actual-action WM forward dynamics and fixed-world heading input alias')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('UNIQUE113_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),traceback=traceback.format_exc(),continue_existing_objects_no_rerecord_retag=True),f,indent=2)
  raise
