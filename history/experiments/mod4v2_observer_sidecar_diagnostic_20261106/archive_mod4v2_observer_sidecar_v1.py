"""ONE R29 diagnostic archive; original recorder once, existing objects after commit."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-observer-sidecar-diagnostic'
BASE=Path('history/experiments/mod4v2_observer_sidecar_diagnostic_20261106');OUT=REPO/BASE
D=R/'T01_OBSERVER_AUDIT_V1';CASE=D/'runs/v2_t01_observer_only_dr_520190_001'
def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resumeobjects,no recorderretry')
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'));proto=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
 if result['controls']!=1200 or result['physics_steps']!=24000 or not result['observer_diagnostic_valid']or result['controller_changed']is not False or result['observer_sidecar_summary']['maximum_estimate_output_difference']!=0.:raise RuntimeError('Unexpected diagnostic receipt')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','prepare_observer_audit_source_v1.py','prepare_observer_audit_source_001.log',
  'observer_audit_v1.py','verify_observer_audit_v1.py','verify_observer_audit_001.log','prepare_observer_audit_case_v1.py','prepare_observer_audit_case_001.log',
  'T01_NOMINAL_BAND_TRAIN_V1/run_band_train_case.py','T01_NOMINAL_BAND_TRAIN_V1/PROTOCOL.json','PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/PLAN.json']
 root.extend(Path(pin['path']).relative_to(R).as_posix()for pin in proto['frozen_small_sources']if Path(pin['path']).is_relative_to(R))
 for dirname in('OBSERVER_AUDIT_V1','OBSERVER_CONTRACT_REVIEW_V1','T01_OBSERVER_AUDIT_V1'):
  root.extend(p.relative_to(R).as_posix()for p in sorted((R/dirname).rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log'))
 root=list(dict.fromkeys(root));old=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py','sensor_core_jump_v1.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 p0=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';extra=[(Path('provenance/P0/kinematics_v2.py'),p0/'kinematics_v2.py'),(Path('provenance/P0/runtime_adapter_v2.py'),p0/'runtime_adapter_v2.py')]
 for p in [R/rel for rel in root]+[V1/rel for rel in old]+[p for _,p in extra]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source:'+str(p))
 note='''# MOD4v2 R29: original observer/actor unchanged, audit witness agrees; DR gravity correction availability

Whole36formal0/36,T01ongoing35pending,goal29activearmed/max40. NoM4/noold3of3reset/no paused520184/185 or520112..115continuation. SameP0c19asset/300N60mmk2000d3unmeasured/CYLINDER.0625/.01guide.015/.9/31robotbody+world/6connect4mimic/full29x16CAD/.5msNewton100/100Hz/originalPD-target-D4-currentPD-signedDC-gain-sameDC/gates/windows. Supportedspawnnotnaturalrise. NoGPU/SSH/PPO/RLtree/newagents/deps/hardwareflash/oldQA/raw. OnlyexistingC reusedread-only6texts/2smallfilesreview,normalstopped/noexecutionSDKstats.

Newaudit subclass generatedfromoriginalStateEstimator.updateAST with ONLYclear-audit andsnapshot-locals diagnostic statements;remove2→originalASTequal/sharedsourceunchanged. Sidecarindependentstate/geometrycopy/samepublicPacket;originalalgorithm runsfirst and exactoriginalEstimate objectalwaysreturned toM0. Newstubtest128packets+1held/1164assert/outputDIFF0/packetunchanged,0FKmodelPHY/oldQA. Live1200calls/allnewfusion/0held/observerfailures0/outputDIFF0. NoextraNativeModel/forward/physics;sidecarpuregeometryworknotepisodes. This is not a paired primary-plant replay;no observer output/truth/DRparametersfedactor/proxy/FSM/force.

Independentreview confirmsmixedepochview:state0..6firstorderarrival,roll/rates/bodyfieldsheldsource,C1combinesheldroll+predpitch/joints. Explicitinterfaceasymmetry/consumptionapproximation,notprovenregressionoruniquecause. OldrollRMS.026556wasalreadyalignedSENSORtruth,soarrival-roll extrapolationcannotbeassumeditswholecause;noactorbiascorrectioncreated.

ONEnewfixed520190fullDRslow purposeobservationnotseed-redrawpassattempt,12s1200ctrl24000physics/freshmodelFullDR1/46.411181swall. D3actually0(no reselection),D4leg2.5ms/wheel0;mass1.043692056/mu.961290323/6gainsindependent. Notallchanneloractiondelayzero. OriginalcaseFAILwhole10points+stopRMS.05320117>.05,LR98.975+99.365%pass/guidehard0/allothergatespass/scopeobservedtrue/robustcertificatefalse. OldR26robustsourceboundstillfailed.0D3counterexampleonlyshows10mssharedqueue notnecessaryforthisfailureclass;differentdrawnotold520183matchedcausalcomparison.

Originalgravitycorrectionweightmean.159871646/zero564of1200=47%;gravityinnovationmean1.2346/max208.825startupincluded. Final9-12weight.155070149/innovationmean1.01302RMS1.10181. Finalvxresidualmean+.0179293RMS.0218382/pitch-.000338689/.00910265/rollsensor-.00720910/.00766140. Atage0firstorderrollgap0. These are pipeline/state diagnostics notcontactprobability/KFcalibration/uniquegravitygatecause. No confidence set1/residualmeansubtraction/DRcancellation. Purelysampledtruthgradingresidualsrecordedinline/noadditionalrawreadorreduction.

Newraw3producerSTREAMSHA/bytes/linesonly;alloldoncebudgetsconsumed. Newmodeldataarelivecaseonlynotcalibration/hardware/WCET/95%reliability/T36proof. Totalv2now8nominal+3DR=11cases13200ctrl264000physics. Nextfocusgravityinnovationgate vsdeclarednoise/mean/dynamicscontract;any futureobserverfixmustbemodule-named/frozen/pairednewprotocol/clearsystemchange,notcallingfeedbackvariantobserver-onlyoroldsystemunchanged. Oldcontrol3mechanisms/K/pausedseedsremain.

Actual small receipt:
'''
 note+=json.dumps({k:result.get(k)for k in('status','complete','controls','physics_steps','total_case_wall_s','checks','case_screen_pass','metrics','contact_metrics','observer_sidecar_summary','observer_diagnostic_valid')},indent=2)
 note+='\n\nOriginalhelperonce/inmemorysparseadd/atomicnonforceownbranch+tag/remote3EXACT/mainreadonlyconcurrent/noRLindex-main-reset-force;oldpendingretained. Largepayloadnoarchivalreadhash,notstandalonewholeassets.\n'
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in old:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 for rel,p in extra:put(rel,p.read_bytes())
 receipts=[]
 for rc in result['producer_raw_receipts']:
  if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closed raw size changed')
  receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 xml=p0/'mjcf/scene.xml';cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_observer_sidecar_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 observer-only audit: original outputs equal, DR gravity correction availability measured',
  '--kind','diagnostic','--note-file',str(OUT/'NOTE.md'),'--validation',
  'NEW52019012s1200ctrl24000physics/originalestimateDIFF0/observervalid;D3draw0;gravityweightzero564of1200;originalscreenFAILwhole10+stop.0532;newstub1164assert0models;0oldraw/QA/newcontroller/hardware;overall0of36.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
