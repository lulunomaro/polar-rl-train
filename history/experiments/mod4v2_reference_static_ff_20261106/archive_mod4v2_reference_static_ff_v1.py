"""Archive ONE actually completed M2 case, including negative design evidence.
Original recorder ONCE. After commit/tag creation continue objects,never retry ID.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-reference-static-ff'
BASE=Path('history/experiments/mod4v2_reference_static_ff_20261106');OUT=REPO/BASE
CASE=R/'T01_REFERENCE_STATIC_FF_V1/runs/v2_t01_reference_static_ff_nominal_slow_520141_001'
NOTE='''# MOD4v2 M2: reference-only nominal static differential feedforward — FAILED,not adopted

Whole36formal0/36,T01ongoing/35pending,goalrevision29activearmed/max40. ALLtraditionalLQRnowMOD4v2 per directhuman,not withdrawnGPU/RLexpert normalization. NoGPU/SSH/PPO/RLtree/newagents/deps/hardwareflash/oldQAorrawreplay. P0 originalc19..HW300N60/31robotbody+world/6connect4mimic/300N60mm/cylinder.0625/.01+guide.015/.9unchanged. Runtime.5msimplicitfastNewton100/control100Hz/actual29x16m47289staticCAD,notv1facetedfulltirequalification. UPRIGHTspawnnotnaturalrise. FourDRTRAIN stillpaused.

ExistingC/E4 reused for disjoint NEW pure design only,then both normalfinish/stopped. C:one nominalJacobian(9internalpureFK)+one tinyFK/0SDK,normalized virtual PD crossrho=.0950714;deleting offdiagonal shifts jointstiffness109.582/132.607 vs120I,not huge coupling/unique cause. NOT_SELECTED/no physicaldiagcandidate. ActualbridgeAPI optional comparison SKIPPED duezeroSDKconstraint,not claimedcomplete. E4:sealedSDK-free terms reused at two targetconfigs/internal18pureFK/0simulatorcompile-forward-step/oldQA. An unexecuted analyticdraft retained and labelled UNEXECUTED,never imported/run. NaturalF0 from existingtrim70.057416/70.168100N,notmg/2hardcode/measuredFn;trimreconstruction2.67e-15Nm. +/- .02rad referenceexample staticdelta[-.220167,.309338,.200511,-.289694]Nm,mostlygas;small2mradPD-equivalent referenceerror NOT predictionofactualerror/rootcause/guaranteedbenefit.

M2 parentcontroller preserves oldcommonLQR/120-4differentialPD/K/shaper/yaw,adds only JOINTdifferential component of nominal static change at smoothC1reference. Fixedpublicproper(0,0,9.81),zero rates/accelerations STATIC assumption NOT measured unknownalpha substitution. Noforceproxy/contact/root/episodeDRinputs. F0fixeddesign,gas2000/3stillunmeasured. Wholepair headroomscale keeps addedJOINTcommonzero,NOTCartesianforcezero. OriginalinverseNomPD->mechanicaltargetprojection->D4->currentPD->signedDC->gain->sameDC untouched. Default runtime/UI/BSP untouched.

ONLYnewcase520141nominal,forward+.3m/s2-8s/stand0-2+stop8-12/original publicstart-9,-1,total12s1200controls24000actualphysics/freshsimulationmodelandFullDReach1/65.8383swall/exit0complete. Sameforwardprofileasbaselinebutnotreliability proof. Allnoncontactcheckstrue;mainL/Rsupport92.210/98.715%,wholepositive-normal-sum<=1N43isolated.5mspoints/guidehard0. OriginalEACH>=95%/whole0gatesremainFALSE:case_screen_passFALSE. Baseline91.570/98.035%+92points vsM2improvescountsBUTrollRMS.00941665->.0210572radworse;rollpeak.0332899,pitchpeak.0180326,vRMSE.0420189/progress1.626089/lateral.0379770/stopRMS.0164248. NOT_ADOPTED,nomorecoefficient/seed/DRextension. M1+M2=2ofmax3consumed,diagpurestudyNOTthirdmechanism. V2total5nominal6000control120000physics;noT01/full36graduation.

AllNEW24000actualsubsteps both originalDCsixaxis changedcounts0/secondcliptohelddifference0,notoldcasebackfill/hardwaretorque/currentthermal/delivery.1198publicinterpolatedobservations/unknownalpha,bounds,calibration/forceFalse/noobserverreturntothecontrollerproxyFSM. ExtraFF peakjoint1.9572/2.0121Nm,wheels0/headroomscaled1/min0/commonincrementresidual0. RuntimeSDK-free terms1201includinginitialization/FK10809 are controller computations NOTindependentcases. FFwalltotal17.0882s/mean14.24ms/max35.9062ms/wholecommand21.9431s,NOT100HzwallclockorARMWCETqualification. Simulationstep/control clocksunchanged.

Preparationfirst3spaceanchorvsactual2failed BEFORE derivedruntime/prefix/model/physics. Originalgenerator/log retained; ONE exactAST singlecallstringindent recovery then solecase. No robotfailure counted from prep,no blind retries. Allcase/drydesign/generators consumed;noQA rerun. Rawfiles not additionallyreducedthisstage. Threebignewrawmetadata producer-streamedbytes/lines/SHAwhilewriting only,nopayloadarchivalread/hash. OriginalP0/CAD externalactualpathsize/existingpublishedorunknownSHA,notstandalonewholeworkspace. Originalrecorder unchanged/one invocation/inmemorysparse-add/unique annotatedtrial/atomicnonforceownbranch+tag/remoteown-tag-peeledexact. NootherRLworktree/index/main/reset/force;prior d8f/5659/489/f4/a362/c0fe and historicalpending retained. PostreceiptTaskedit rides next realstage,no archive-receiptloop.
'''

def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resume objects,no recorder retry')
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'))
 if not result['complete']or result['controls']!=1200 or result['physics_steps']!=24000 or result['case_screen_pass']is not False:raise RuntimeError('Unexpected closed M2 receipt')
 if result['reference_static_ff_aggregate']['calls']!=1200 or result['private_motor_observation']['sections']['all']['any_dc_changed_ticks']!=0:raise RuntimeError('Unexpected M2 observer/FF receipt')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Largeartifact external only:'+str(source))
  put(rel,source.read_bytes())
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','controller_reference_static_ff_v1.py','runtime_reference_static_ff_v1.py',
 'prepare_reference_static_ff_v1.py','prepare_reference_static_ff_retry001.py','prepare_reference_static_ff_v1_001.log',
 'prepare_reference_static_ff_retry001.log','REFERENCE_STATIC_FF_PREP_ATTEMPT001.json',
 'T01_REFERENCE_STATIC_FF_V1/run_reference_static_ff_v1.py','T01_REFERENCE_STATIC_FF_V1/PROTOCOL.json',
 'T01_REFERENCE_STATIC_FF_V1/PREPARATION.json','T01_REFERENCE_STATIC_FF_V1/README.md','T01_REFERENCE_STATIC_FF_V1/reference_static_ff_001.log',
 'REFERENCE_STATIC_FF_DESIGN_V1/static_ff.py','REFERENCE_STATIC_FF_DESIGN_V1/design_static_ff.py',
 'REFERENCE_STATIC_FF_DESIGN_V1/PREEXEC.json','REFERENCE_STATIC_FF_DESIGN_V1/RESULT.json','REFERENCE_STATIC_FF_DESIGN_V1/README.md',
 'VMC_DIAGONAL_DESIGN_V1/PREEXEC.json','VMC_DIAGONAL_DESIGN_V1/PREEXEC_INPUT_PINS.json','VMC_DIAGONAL_DESIGN_V1/compute_once.py',
 'VMC_DIAGONAL_DESIGN_V1/RESULT.json','VMC_DIAGONAL_DESIGN_V1/FORMULAS.md','VMC_DIAGONAL_DESIGN_V1/compute_once_001.log',
 'CONTACT_PROXY_V2/nominal_model.py','CONTACT_PROXY_V2/PUBLIC_NOMINAL_CONSTANTS.json',
 'runtime_v2.py','bridge_v2.py','dr_v2.py','model_builder_v2.py','v2_linearization.py','nominal_gain_v2.json',
 'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py',
 'observed_bridge_v1.py','actuation_telemetry_v1.py','public_signal_adapter_v1.py','signal_alignment_v1.py',
 'diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py']
 root+=['T01_REFERENCE_STATIC_FF_V1/runs/'+CASE.name+'/'+name for name in ['config.json','protocol.json','meta.json','result.json']]
 for rel in root:copy(R/rel,Path('payload/v2')/rel)
 for rel in ['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py',
 'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']:
  copy(V1/rel,Path('provenance/v1')/rel)
 receipts=[]
 for receipt in result['producer_raw_receipts']:
  p=Path(receipt['path'])
  if p.stat().st_size!=receipt['bytes']:raise RuntimeError('Closedrawsize differs')
  receipts.append(dict(receipt,archival_payload_read=False,archival_payload_hash=False))
 xml=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'
 receipts.append(dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',identity='existingpublishedP0,noarchivepayloadreadhash'))
 cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.append(dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,identity='actualCAD,unknownSHA/noarchivepayloadreadhash'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_static_reference_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 M2 reference-static differential FF nominal FAILURE preserved',
 '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',
 'ONEnew12s1200control24000physics:noncontactpass/supportFAIL92.210/98.715%+43low,rollRMSworse;allDCchanged0;FFmax2.012Nm/35.906msNOTRT;twoNEWSDKfreedesigns/notselecteddiag;0oldQA/rawreplays,hware0,full36still0.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
