"""ONE R28 evaluation archive. Original recorder unchanged; never retry after commit."""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-nominal-band-train-screen'
BASE=Path('history/experiments/mod4v2_nominal_band_train_screen_20261106');OUT=REPO/BASE
D=R/'T01_NOMINAL_BAND_TRAIN_V1'
def main():
 def git(*a):return subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrongbranch/stageddata')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existingprefix/tag:resumeobjects,no recorderretry')
 summary=json.loads((D/'COLLECTION001/RESULT.json').read_text(encoding='utf-8'))
 protocol=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
 if summary['executed_case_count']!=3 or summary['physics_steps_total']!=72000 or summary['wave1_pass']is not False or summary['wave2_status']!='PAUSED_BY_PREDECLARED_FAILURE_RULE':raise RuntimeError('Unexpected frozen failure stop receipt')
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','prepare_nominal_band_train_v1.py','prepare_nominal_band_train_001.log',
  'T01_NOMINAL_BAND_M0_V1/run_nominal_band_m0.py','T01_NOMINAL_BAND_M0_V1/PROTOCOL.json','PUBLIC_NOMINAL_BAND_EXPERIMENT_V1/PLAN.json']
 root.extend(Path(p['path']).relative_to(R).as_posix()for p in protocol['frozen_small_sources'])
 root.extend(p.relative_to(R).as_posix()for p in sorted(D.rglob('*'))if p.is_file()and p.suffix in('.py','.json','.md','.log'))
 root=list(dict.fromkeys(root));provenance=['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py','sensor_core_jump_v1.py',
  'RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']
 p0=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
 extra=[(Path('provenance/P0/kinematics_v2.py'),p0/'kinematics_v2.py'),(Path('provenance/P0/runtime_adapter_v2.py'),p0/'runtime_adapter_v2.py')]
 for p in [R/x for x in root]+[V1/x for x in provenance]+[p for _,p in extra]:
  if not p.is_file()or p.stat().st_size>2_000_000:raise RuntimeError('Missing/large selected source: '+str(p))
 note='''# MOD4v2 R28: nominal stand PASS; first two frozen TRAIN DR FAIL; remaining seeds paused

Whole36formal0/36,T01ongoing35pending;goal29activearmed/max40. AlltraditionalLQRonMOD4v2,not withdrawn GPU/RL migration. OriginalM0/newband/sourceP0c19/CYLINDER.0625/.01/guide.015/.9/300N60mm/k2000d3unmeasured/31robotbody+world/6connect4mimic/full29x16CAD/.5msNewton100/100Hz/originalPD-target-D4-currentPD-signedDC-gain-sameDC/gates/windows preserved. No M4 or old3of3 reset. Supportedspawn not naturalrise. Robustcorridorcertificate false.

Five seeds520181..185 frozen before any draw,16v2smallsource/gain identity pins checked beforecaseprefix/model. Firstnewnominalstand520181PASS15checks/main100+100/wholeguidehard0/XYdrift.00972679. Then two1thread workers max2parallel:520182DRstand and520183DRslow complete12s1200control24000physics each,3freshmodels+FullDRtotal/72000physics. Stand99.96+99.96%/whole2,onlywhole0gateFAIL. Slow99.035+99.635%/whole9+final9-12vxRMS.0665084>.05FAIL,allothergatespass. Notmacroflight/unique-causeproof. Bothscopeobservedtrue/all24000DCchanged0each,notrail/currentthermal/hardwaretorque/delivery. Remaining520184/185NOTEXECUTED by predeclared wave1-failure rule,not independent failures. Old520112..115paused/no oldcase replay/no seed redraw/parameter change/score-window extension.

BothDR D3=10ms;notall-delaycoverage.520182D0-onlynominal branch retainsD1-D7,leg/wheelD4=2.5/5ms.520183mass1.052495896/mu.864516129/independent6gains/D4leg5ms-wheel0. Source real draws reported;noDR cancellation. Sevenpriornominalcases remain;now8nominal+2DR=10cases12000control240000realphysics,notdryclock/staticforward.

New smallcollection reads3resultJSONs only. New twoDRtraces readONCE1200each/2400total for observation diagnosis;0oldraw/motorcontactpayload/hashreread/replay/FK/model/forward/physics. Comparecontroller-usedvx/pitch atcommand epoch topreviousPOSTsameepoch1199pairs;heldroll separatelysensor epoch1198. Finalslowvxresidualmean-.0115986/RMS.0151266m_s,pitchmean-.027385/RMS.0279612rad,heldrollmean-.0264209/RMS.0265557. Pipeline residuals NOTsensor calibration/unique delay cause/actor truth correction. Final12s vxnear0 doesnoterasefrozen9-12RMSfailure. This once budget consumed. Unknownalpha/noiseclockbounds/outputtorquecalibration/force readiness remainunknown/false;privateonly/nocontrollerproxyFSMreturn.

No agent/deps/GPU/SSH/PPO/RLtree/hardwareflash/oldQA/newcontroller. Next inspect existing observation/time contracts against bounded new small results,notM4/gate/seed/source-preflight chain. FullT01/full36/T36/95%reliability/hardware/WCETnotgraduated.

Actual bounded receipt summary:
'''
 note+=json.dumps({k:summary[k]for k in('protocol_id','nominal_stand_pass','wave1_pass','wave2_status','executed_case_count','executed_screen_passes','physics_steps_total','controls_total','fresh_model_builds_total','FullDR_constructors_total')},indent=2)
 note+='\n\nLargeartifactsindexedbyactualpath/size/existingproducerSHAonly,not archival payload reread/hash. Originalhelperonce/inmemorysparseadd/atomicnonforceownbranch+tag/remote3exact;mainreadonly concurrent observation/noRLindex/main/reset/force. Older pending retained. Snapshotnotwholeassets.\n'
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 for rel in root:put(Path('payload/v2')/rel,(R/rel).read_bytes())
 for rel in provenance:put(Path('provenance/v1')/rel,(V1/rel).read_bytes())
 for rel,p in extra:put(rel,p.read_bytes())
 receipts=[]
 for r in summary['records']:
  for rc in r.get('producer_raw_receipts',[]):
   if Path(rc['path']).stat().st_size!=rc['bytes']:raise RuntimeError('Closed raw size changed')
   receipts.append(dict(rc,archival_payload_read=False,archival_payload_hash=False))
 xml=p0/'mjcf/scene.xml';cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.extend([dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',archival_payload_read=False,archival_payload_hash=False),
  dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,archival_payload_read=False,archival_payload_hash=False)])
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',note.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_band_train_recorder',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*a):
  if a and a[0]=='add':a=('add','--sparse',*a[1:])
  try:return original(*a)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 nominal-band frozen TRAIN screen: stand PASS, two DR FAIL, wave2 paused',
  '--kind','evaluation','--note-file',str(OUT/'NOTE.md'),'--validation',
  'NEW520181+182+183/3x12s3600ctrl72000physics/fresh3;nomstandPASS/DRstandwhole2FAIL/DRslowwhole9+stopRMS.0665FAIL;184185unused;2newDRrawonce2400rows0oldQA;originalM0/gates unchanged,overall0of36.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotated trial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remoteidentitymismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
