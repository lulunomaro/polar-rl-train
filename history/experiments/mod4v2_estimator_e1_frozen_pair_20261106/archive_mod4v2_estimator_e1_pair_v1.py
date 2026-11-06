"""ONE R30 paired observer E1 evaluation; original recorder once, old failures retained."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-estimator-e1-frozen-pair'
BASE=Path('history/experiments/mod4v2_estimator_e1_frozen_pair_20261106');OUT=REPO/BASE;D=R/'T01_ESTIMATOR_E1_PAIR_V1'
def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resumeobjects,no recorderretry')
 comparison=json.loads((D/'COLLECTION001/RESULT.json').read_text(encoding='utf-8'));proto=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
 if not comparison['pair_valid']or comparison['simulation_episodes']!=2 or comparison['independent_DR_parameter_settings']!=1:raise RuntimeError('Unexpected pair receipt')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','prepare_estimator_e1_v1.py','prepare_estimator_e1_001.log','estimator_cauchy_e1.py','verify_estimator_e1_v1.py','verify_estimator_e1_001.log',
  'prepare_estimator_e1_pair_v1.py','prepare_estimator_e1_pair_001.log','prepare_estimator_e1_pair_recovery001.py','prepare_estimator_e1_pair_recovery001.log',
  'observer_audit_v1.py','T01_OBSERVER_AUDIT_V1/run_observer_audit_case.py','T01_OBSERVER_AUDIT_V1/PROTOCOL.json','PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/PLAN.json']
 root.extend(Path(pin['path']).relative_to(R).as_posix()for pin in proto['frozen_small_sources']if Path(pin['path']).is_relative_to(R))
 for dirname in('ESTIMATOR_CAUCHY_E1_V1','T01_ESTIMATOR_E1_PAIR_V1'):
  root.extend(p.relative_to(R).as_posix()for p in sorted((R/dirname).rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log'))
 root=list(dict.fromkeys(root));old=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py','sensor_core_jump_v1.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 p0=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';extra=[(Path('provenance/P0/kinematics_v2.py'),p0/'kinematics_v2.py'),(Path('provenance/P0/runtime_adapter_v2.py'),p0/'runtime_adapter_v2.py')]
 for p in [R/rel for rel in root]+[V1/rel for rel in old]+[p for _,p in extra]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source:'+str(p))
 note='''# MOD4v2 R30: first named observer-module E1 paired validation; both original screens/scope fail

Whole36formal0/36/T01ongoing35pending/Goal29activearmedmax40. OldnominaltorqueM1/M2/M3=3of3frozen/notadopted,nofourthtorque/K/grid. NEWobserverstageE1=1ofmax3:exactoneinnovationmultiplier replacement max(0,1-r)→1/(1+r²),sameexistinglimit1/no coefficientsearch. Originalgravitynormgate/accel_correction1.5/errorclip/KFothermath/epochapproximationunchanged. Newfinite-inputguardexplicit. Originalsharedsources/defaultM0runtime/UI/BSP/P0/CADnotmodified. E1changesfeedback/system explicitly,not observer-only or baselineequivalence. Same-variantwitness0meanswitnessmatchesownactor,notbaseline==E1.

P0c19asset/300N60mm/k2000d3unmeasured/cylinder.0625/.01guide.015/.9/31robotbody+world/6connect4mimic/full29x16CAD/.5msNewton100/100Hz/originalPD-target-D4-currentPD-signedDC-gain-sameDC/gates/windows unchanged. Supporteduprightspawnnotnaturalrise. NoGPU/SSH/PPO/RLtree/newagent/deps/hardwareflash/oldQA/rawrescan. No teacher residual subtraction/DRparameterinverse/oldpausedseedcontinuation.

Newsoftwarecheck454assert/11mathpoints/64idealstatic+40newdisturbancepackets/simplifiedgeom0FKmodelPHY:staticstate14diff0/sameE1witnessdiff0/disturbancebaseline-E1differenceNONzero explicitfeedbackchange. Notrobotaccuracy/performanceproof. ASTrestoreonechangedmultiplier→oldauditedupdateexact;twoexistingdiagnosticstatementsretained. Firstpairprepmetadata17vsactual16spaceanchorfailedBEFOREderivedprefix/model/physics/seed;originalsource/log+PAIR_PREP_ATTEMPT001kept,oneexactASTrecoveryoneCall/twoliteralsactualsemanticindent. No blind replay/nativefailure.

ONEnewfixed520200pairedsetting,notoldcase replay:baseline/E1eachfreshmodelFullDR1/12s1200ctrl24000physics. SAMEinitialDRreceipts exact/SAMEqpos37diff0/SAMEtorqueLQRKdiff0/sourceprotocol;twoepisodesareONEindependentrandomsetting. Max2singlethreadphysicalworkers. D3both0asdrawn/no seedselection. Bothcomplete/allmatching-variantwitnessdiff0/diagnosticvalid. Baselinewall50.1954/E149.3650s NOTrealtime/WCET/hardware.

BOTHoriginalcase_screenFAILonlywhole0gate,guidehard0,LRsupports96.980/97.565→98.030/98.560,whole39→25. RollRMS.0283846→.0140824/rollpeak.0519033→.0230045/heldrollsensorresidualRMS.0372400→.0168117;weightmean.125306→.406136/zero690→8. ButpitchRMS.0123436→.0132732andstopRMS.0152679→.0184214slightlyworse(bothpassstop). PartialimprovementNOTpass/uniquerootcause/reliability. Both100Hz311geometryscopeFALSE:cachedXYmaxexcess.0338229/.0255360m,poseboundsTrue;sourcebandnotcertifiedforDR/oldR26robustteststaysfailed,no marginwidening/gaterelax. pair_validcontrolscomparisonconditions,NOTscopequalification.

No defaultE1adoption. Raw6producerSTREAMreceipts/statmetadataonly,no payloadarchivehash/additionalrawreduction;collectionreads2NEWsmallresult+2meta0raw/modelPHY. Totalv2now13simulations15600ctrl312000physics,8nominal+5DRepisodesbut4independentDRsettings. Oldallfailure/oncebudgets/paused520184185and520112..115retained. E1formula frozen,notimmediateE2/coefficientgrid;futureexplicitnewnominalregression/boundedpairneededbeforeadoption. Actual collected comparison follows:\n
'''+json.dumps({k:comparison[k]for k in('pair_checks','pair_valid','same_initial_qpos_maxdiff','same_torque_LQR_K_maxdiff','independent_DR_parameter_settings','E1_minus_baseline','default_E1_adoption')},indent=2)
 note+='\n\nOriginalhelperunchanged/ONEinvocation/inmemorysparseadd/atomicnonforceownbranch+tag/remote3EXACT/mainreadonlyconcurrent;noRLindex-main-reset-force. Snapshotnotstandaloneassets,olderpendingstagesretain.\n'
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in old:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 for rel,p in extra:put(rel,p.read_bytes())
 receipts=[]
 for row in comparison['rows']:
  for rc in row['producer_receipts']:
   if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closedrawsizechanged')
   receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 xml=p0/'mjcf/scene.xml';cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_estimator_e1_pair_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 observer E1 fixed paired setting: partial roll improvement, both whole/scope fail',
  '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',
  'NEW520200baseline/E1pair2freshmodels2400ctrl48000physics/oneDRsetting/DRqposKexact;E1feedbackchangeexplicit;bothscreenFAILwhole39to25/scopefalse;rollRMS.02838to.01408;newcheck454assert0model;0oldrawQA/hardware;overall0of36.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
