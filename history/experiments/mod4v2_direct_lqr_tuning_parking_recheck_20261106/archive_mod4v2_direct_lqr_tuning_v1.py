"""ONE human-requested direct tuning stage + unarchived completed R31 receipts.
No replay/rawhash;old score/strict failures preserved;original recorder untouched.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102';REPO=W/'repo-lqr-robust'
BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-direct-lqr-tuning-parking-recheck';BASE=Path('history/experiments/mod4v2_direct_lqr_tuning_parking_recheck_20261106');OUT=REPO/BASE

def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingobjects/prefix:never rerun recorder')
 summary=json.loads((R/'DIRECT_LQR_TUNING_V1/FINAL_SUMMARY001/RESULT.json').read_text(encoding='utf-8'))
 if summary['full_CAD_physics']!=144000 or summary['flat_physics']!=112000:raise RuntimeError('Unexpected direct tuning evidence')
 roots=['TERRAIN_ADAPTATION_TASKS_V2.md','controller_parking_trial_v1.py','prepare_direct_lqr_tuning_v1.py','prepare_direct_lqr_tuning_001.log',
  'prepare_estimator_e1_validation_v1.py','prepare_estimator_e1_validation_001.log','estimator_cauchy_e1.py','observer_audit_v1.py',
  'runtime_v2.py','model_builder_v2.py','bridge_v2.py','dr_v2.py','v2_linearization.py','nominal_gain_v2.json',
  'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py','observed_bridge_v1.py','actuation_telemetry_v1.py',
  'public_signal_adapter_v1.py','signal_alignment_v1.py','diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py']
 for dirname in('DIRECT_LQR_TUNING_V1','T01_ESTIMATOR_E1_VALIDATION_V1'):
  roots.extend(p.relative_to(R).as_posix()for p in sorted((R/dirname).rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log'))
 roots=list(dict.fromkeys(roots));old=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py','sensor_core_jump_v1.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 p0=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';extra=[(Path('provenance/P0/kinematics_v2.py'),p0/'kinematics_v2.py'),(Path('provenance/P0/runtime_adapter_v2.py'),p0/'runtime_adapter_v2.py')]
 for p in [R/x for x in roots]+[V1/x for x in old]+[p for _,p in extra]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selectedsource:'+str(p))
 note='''# Direct human-requested LQR tuning, parking improvement and actual +/-2m/s benchmark

2026-11-06 14:18 human explicitly complained of excessive audit loops and requested actual tuning. This stage changed REAL DARe-solved gains/legparameters and ran6new fullCAD DRclosedloops plus2nominal28sfullrobotflatbenchmarks. NoobserverE1retuning/newaudits/replay/rootteacher/newagents/GPU/SSH/PPO/deps/hardwareflash. OriginalP0c19asset/300N60mm/k2000d3unmeasured/cylinder.0625/.01guides.015/.9/6connect4mimic/31robotbody+world/100Hz-.5msNewton100/PD-targetD4-currentPD-signedDC-gain-sameDC/gatesunchanged. Newconfig results retained,old3FFfailures/E1data not erased.

Fixednew530300training:baseline vs Qpitchrate4/Qvelocity2.25 actualKmaxdiff16.0651 vs sameLQRwithdifferentialKP90KD6;bothworsenedfixedscore/pitchRMS,notadopted. ThirdandFINALchangedgaincandidate R4(oldQ/leg120-4)predeclaredafterthosefailures;same trainingepisode/newdistinctgaincase,notbaseline replay. R4score2.67693vs2.80886=4.697%better but BELOWold5%selectionrule;old not-selected conclusion preserved. It did restoreoriginalstopgate.053773->.045809m/s,thereforea separatelydeclarednew530301DIAGNOSTIC parkingrecheck—notretroactivewinner—heldR4fixed. RechecksameDR/initialqpos:stop.065334->.054786(16.145%better),score2.98760->2.69147;pitch/rollbetter,velocitytracking slightlyworse. Stilloriginalstop>.05/wholepositive-lowpoints/strictCADscreensfalse,no scope widening. Trainingwhole2->5,recheck24->17. Source scope recheck bothtrue,trainingbothfalse retained. Noautomaticformaldefault/reliability/T01qualification.

ActualcompleteP0nominal EXTRA longflatfixture baseline/R4each28s2800controls56000physics:command+2,brake,-2,brake;baselineactualmeans+2.05033/-2.05044,R4+2.06345/-2.06365. StopRMSbase.012271/.012024,R4.012393/.012127. Allcomplete/noreset/fall. Originalbetterinnominalspeedfixture,soR4isparkingprioritytrialnotuniversalreplacement. Explicitnot latestCAD/T02acceptance/DRproof. Existingflatmodelbranchpurpose relabelledinbenchmarkmeta,notpretendinglinearizationorwholearena. CSVactualqpos37recorded100Hz,nocontinuous-sweep/hardwareproof.

Exported parking trial recipe actualKreference plusoptincontroller factory with EXACTtestedbaseP25settings(defaultposition25 etc),R4re-solvedonnewv2dynamics,shareddefaultruntimeunchanged. NoMPCchangeclaimed. New8closedloop256000physics. OldunarchivedR31threecompletecase receipts/source also includedwithoutreplay:nominalE1standpass/520211D3=10msnewpairrollimprovesbutwhole4->14worse,bothstrictfail/scopeTrue,E1notdefault. OldR31once/newrawbudgetsretained;not pretending R31 was previouslycommitted.

Goalgetat14:19revision30paused/disarmed31/40;resumeinterface requiresuser,notclaimedactive/noalternateGoal. Currentdirecthumanrequestexecuted. Allcase failures/unchanged originalgates persist. Large27CADraw+2flatCSV/sourceassetspathsize/existingproducerSHAorunknownONLY,NOarchivalpayloadhash/read. Snapshotnotstandaloneassets;olderpendingstatesretain. Actualsmall summary:\n
'''+json.dumps({k:v for k,v in summary.items()if k not in('rows','flat_benchmark')},indent=2)
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in roots:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in old:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 for rel,p in extra:put(rel,p.read_bytes())
 receipts=[];seen=set()
 for folder in('DIRECT_LQR_TUNING_V1','T01_ESTIMATOR_E1_VALIDATION_V1'):
  for p in sorted((R/folder).rglob('result.json')):
   x=json.loads(p.read_text(encoding='utf-8'))
   for rc in x.get('producer_raw_receipts',[]):
    if rc['path']in seen:continue
    if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closedrawsizechanged')
    seen.add(rc['path']);receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 for name in('flat_baseline_530302_001','flat_effort4_530302_001'):
  p=R/'DIRECT_LQR_TUNING_V1/FLAT_SPEED_BENCH'/name/'trace.csv';receipts.append(dict(path=str(p),bytes=p.stat().st_size,sha256=None,reason='producer did not record SHA;not rehashed for archive',archival_payload_read=False,archival_payload_hash=False))
 xml=p0/'mjcf/scene.xml';cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_direct_lqr_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 actual LQR gain tuning: reproduced R4 parking improvement and fullrobot +/-2m/s flat benchmark',
  '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation','6newCADcases144000physics/3changedgaincandidates;R4stop14.81percentand16.14percentbetter2settings,strictgapsretained;2fullrobotflat28s112000physicsactual+/-2m/s;no rawreplay/hardware;oldR31receiptsincluded.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),raw_artifact_indexes=len(receipts),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
