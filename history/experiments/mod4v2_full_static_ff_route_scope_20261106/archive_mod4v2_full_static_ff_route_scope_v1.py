"""ONE completed R25 trial: M3 FAILURE, bounded evidence, route-source correction.
After commit/tag creation, resume existing objects only;never replay this recorder.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-full-static-ff-route-scope'
BASE=Path('history/experiments/mod4v2_full_static_ff_route_scope_20261106');OUT=REPO/BASE
CASE=R/'T01_REFERENCE_FULL_STATIC_FF_V1/runs/v2_t01_reference_full_static_ff_nominal_slow_520151_001'
NOTE='''# MOD4v2 R25: M3 full reference-static FF failed; flat_run nominal tire strips not uniform

Whole36formal0/36,T01ongoing/35pending,goalrevision29activearmed/max40. LatesthumanALLtraditionalLQRonMOD4v2,not withdrawn GPU/RL expert migration. NoGPU/SSH/PPO/RLtree/newagents/deps/hardwareflash/oldQA. P0 HW300N60 originalc19.. unchanged,300N/60mm/k2000d3unmeasured,cylinder.0625/.01+guide.015/.9 NOTv1facetedmeshqualification. Full31robotbody+world/6connect4mimic/actual29x16CAD47289statics/47282collisionconvexes;runtime.5msNewton100/100Hz. Uprightspawnnotnaturalrise.

M2 NEWtrace1200lines reduced ONCE,0oldraw/motorcontactpayload/replay/FK/model/physics:referencehipexcursion.220769rad rather than initialdesign.02;packet/stateq agrees5.55e-17rad;matched sensor-epochrollerror1199/RMS.000740743rad;37/43wholelows at7-8s. Parent6NEWpuregeometryposes from compactderivedrows showmeanwheelXZdrift~3mm/-.2mm,NOTselectedCartIK. ExistingC reused only NEW actualgeometry API same-point2calls/internal10poses/SDKimportallowed/allmodel-physicsblocked;XZ/J/T0 agreesFDtol,noall-domainqualification/Y-Jyoldreferenceunknown. Agentnormalfinish/stopped/E4notresumed.

M3 restores full nominal reference-static correction including jointcommon component M2 deleted,keepsoriginalcommonLQR FEEDBACK/K/PD/shaper/C1C2/PD-target-D4-currentPD-doubleDC/limits/collisions/gates. NoFFweightgrid/extraControllermechanism. ONE520151nominal forward12s/1200control/24000actualphysics/freshmodelFullDR1each/63.5082s wall. Allnoncontactchecks true BUT main support92.545/98.425% and whole59isolated.5ms points fail originaleach95%/whole0;guidehard0. RollRMS.0209362 worse original.00941665. NOTADOPTED;M1/M2/M3=3of3 consumed,FROZEN,noM4/DR/gaterelax. Sixv2nominal7200controls144000physics total,not static/dryclock.

NEWall24000substeps bothoriginalDCsixaxis changedcounts0/secondDCtoheld0,not railoccupancy/currentthermal/hardwaredelivery/oldcasebackfill. FullFF extra4peak2.5381/2.7495/1.3833/1.2819Nm,wheels0;retainedcommonpeak.577386/.733815Nm,common-sum1.46763Nm,fullreference mapping0. Terms1201/FK10809 arecontrollercomputationsnotepisodes;FFmean13.7063ms/max28.6465ms NOTwallclock100Hz/ARMWCET.1198publicalignmentframes/unknownalpha+noiseclockbudgets+trueoutputtorquecalibration/forceFalse/noactor-proxy-FSMconnection.

Afterfreeze ONEdifferent source-only MACRO public-plan suitability question,not a contact/micron/nativephysicsprobe. Atpublicrootx-9/-8/-7.5/-5.5, nominalboth-tirecenter sourceheightdifferences11.459/25.194/89.450/11.459mm. At-7.5leftz+.0575542/right-.0318954m. 24sourcepointqueries/26selectedConvexHullbuilds/full47282bboxcoverage/noerrors/0SDKmodel-forward-physics/raw. Flat_run label+centerline is not proof of uniformboth-tireplane;not actualtrajectory or uniquedynamiccause. No route/scene/controller input changed. Nextfirstaudit publicCAD full-tire/bodycorridor;anynewplanneeds explicitnewscenario,old failures/cap retained,not same-condition gainimprovement.

Firstsourceaudit wrongly assumed allconvexes6vertices,failed BEFOREanyheightquery/0physics. Originalprefix/code/logretained. ONEstructuraldiagnosis shows6..420vertices(44563sixvertex),7visualexcluded/no unhandled transforms. ONE exactshape recovery separateRETRY001 uses existingSciPyConvexHull for selectedcandidates,notanothercontrol/hardwaretest. SourceXML functionalpasses originalfailed+structural+recovery,never archivalhash. M3rawNOTadditionallyreduced;allold once budgetsremainconsumed.

ThreebigM3raw actualpath/bytes/lines+existingproducerSTREAMSHA only(noarchivepayloadread/hash),sourceP0/CAD truepathbytes+publishedSHAorunknown. Smallsource/result/error/logsselected;notstandaloneassetworkspace. Originalrecord_experiment.py unchanged/ONEinvocation/inmemorysparse-add/atomicnonforce ownbranch+tag/remoteown-tag-peeledexact. NoRLindex/main/reset/force,prior533/d8f/5659/489/f4/a362/c0fe+historicalpending retained. Postreceiptledgeredit rides next realstage,no receipt-archive loop.
'''

def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resume objects,no recorder retry')
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'))
 if not result['complete']or result['controls']!=1200 or result['physics_steps']!=24000 or result['case_screen_pass']is not False:raise RuntimeError('Unexpected M3 receipt')
 if result['private_motor_observation']['sections']['all']['any_dc_changed_ticks']!=0 or result['reference_static_ff_aggregate']['common_component_deleted']is not False:raise RuntimeError('Unexpected M3 observer/FF role')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','update_round25_ledger.py','controller_reference_full_static_ff_v1.py',
 'runtime_reference_full_static_ff_v1.py','prepare_reference_full_static_ff_v1.py','prepare_reference_full_static_ff_v1_001.log',
 'T01_REFERENCE_FULL_STATIC_FF_V1/run_reference_full_static_ff_v1.py','T01_REFERENCE_FULL_STATIC_FF_V1/PROTOCOL.json',
 'T01_REFERENCE_FULL_STATIC_FF_V1/PREPARATION.json','T01_REFERENCE_FULL_STATIC_FF_V1/README.md','T01_REFERENCE_FULL_STATIC_FF_V1/reference_full_static_ff_001.log',
 'T01_REFERENCE_STATIC_FF_V1/reduce_control_once.py','T01_REFERENCE_STATIC_FF_V1/reduce_control_once_001.log',
 'T01_REFERENCE_STATIC_FF_V1/REDUCTION001/START.json','T01_REFERENCE_STATIC_FF_V1/REDUCTION001/RESULT.json',
 'T01_REFERENCE_STATIC_FF_V1/derive_common_reference_geometry_once.py','T01_REFERENCE_STATIC_FF_V1/derive_common_reference_geometry_001.log',
 'T01_REFERENCE_STATIC_FF_V1/COMMON_REFERENCE_GEOMETRY001/PREEXEC.json','T01_REFERENCE_STATIC_FF_V1/COMMON_REFERENCE_GEOMETRY001/RESULT.json',
 'PUBLIC_CONTROL_GEOMETRY_API_V1/PREEXEC.json','PUBLIC_CONTROL_GEOMETRY_API_V1/INPUT_PINS.json','PUBLIC_CONTROL_GEOMETRY_API_V1/check_api_once.py',
 'PUBLIC_CONTROL_GEOMETRY_API_V1/RESULT.json','PUBLIC_CONTROL_GEOMETRY_API_V1/check_api_once_001.log','PUBLIC_CONTROL_GEOMETRY_API_V1/NOTE.md',
 'audit_public_route_macro_heights_once.py','audit_public_route_macro_heights_001.log','inspect_route_source_shape_failure_once.py',
 'inspect_route_source_shape_failure_001.log','audit_public_route_macro_heights_retry001.py','audit_public_route_macro_heights_retry001.log',
 'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/PREEXEC.json','PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/SOURCE_SHAPE_FAILURE001.json',
 'PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/RETRY001/PREEXEC.json','PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/RETRY001/RESULT.json','PUBLIC_ROUTE_FOOTPRINT_SOURCE_V1/README.md',
 'REFERENCE_STATIC_FF_DESIGN_V1/static_ff.py','CONTACT_PROXY_V2/nominal_model.py','CONTACT_PROXY_V2/PUBLIC_NOMINAL_CONSTANTS.json',
 'runtime_v2.py','bridge_v2.py','dr_v2.py','model_builder_v2.py','v2_linearization.py','nominal_gain_v2.json',
 'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py',
 'observed_bridge_v1.py','actuation_telemetry_v1.py','public_signal_adapter_v1.py','signal_alignment_v1.py','diagnostic_stream_v1.py','SENSOR_TIME_METADATA_V1/publisher.py']
 root+=['T01_REFERENCE_FULL_STATIC_FF_V1/runs/'+CASE.name+'/'+name for name in ['config.json','protocol.json','meta.json','result.json']]
 provenance=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py',
 'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 for p in [R/rel for rel in root]+[V1/rel for rel in provenance]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source:'+str(p))
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in provenance:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 receipts=[]
 for receipt in result['producer_raw_receipts']:
  if Path(receipt['path']).stat().st_size!=receipt['bytes']:raise RuntimeError('Closedrawsize differs')
  receipts.append(dict(receipt,archival_payload_read=False,archival_payload_hash=False))
 xml=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'
 receipts.append(dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',identity='existingpublishedP0,noarchivepayloadreadhash'))
 cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.append(dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,identity='functionalsourceauditdone;noarchivepayloadreadhash'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_full_static_route_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 M3 full static FF FAILURE and public route tire-strip scope evidence',
 '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',
 'ONE520151nominal12s1200control24000physics:noncontactpass/supportFAIL92.545/98.425%+59low;3of3frozen;allDCchanged0;newM2traceonce;API2calls0models;source24macroqueries26hulls89.45mmcrossheight;0oldQA/hardware/full36still0.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotatedtrial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
