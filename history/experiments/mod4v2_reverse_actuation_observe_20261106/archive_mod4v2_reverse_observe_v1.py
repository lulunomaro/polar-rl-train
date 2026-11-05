"""Seal ONE new reverse-profile actual-physics observation, original helper once.
After any commit/tag creation resume existing objects; never rerecord this ID.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust';ID='mod4v2-reverse-actuation-observe'
BASE=Path('history/experiments/mod4v2_reverse_actuation_observe_20261106');OUT=REPO/BASE
CASE=R/'T01_OBSERVABILITY_V1/runs/v2_t01_reverse_observe_nominal_520130_001'
NOTE='''# MOD4v2: ONE new reverse low-speed actual actuator/source-time observation

Same goalrevision29active/max40,whole36formally0/36,T01ongoing/35pending. Actual new nominalcase520130 only,12s1200controls24000MuJoCo integration steps/49.146s wall/fresh model+FullDR each1. Public flat_run opposite endpoint-5.5m/-1m/yaw0 initialization before physics;-.3m/s2–8s/stand+stopotherwise. Old waypointstart-9m was not extended into undocumented reverse space. Actual path/direction differs from old forward,so NOT a matched forward/M1 causal comparison. Old three v2 cases unchanged;v2 physical total4nominal4800control96000physics. UPRIGHTprior not naturalrise. Original P0cylinder.0625/.01/guide.015/.9/300N60mm still not oldv1facetedtire qualification. NoGPU/SSH/PPO/RLtree/newagent/deps/hardware/flash/oldQA/oldraw replay.

New case noncontact checks alltrue:pitchpeak.0162916rad/rollpeak.0322385/vxRMSE.0202963/progress1.823457m/lateral.045477m/stopRMS.0287206m/s. Each-mainwheel support93.640/98.540%,wholepositive-normal-sum<=1N76isolated.5mspoints,guidehard0. Original >=95% and whole0gates unchanged:case_screen_passFALSE,not T01/full36/reliability qualification. Extra route-center diagnostic is not gate relaxation or full body-footprint proof. M1 still not adopted;this is observation NOT M2,only M1ofmax3 consumed. FourTRAIN DR still paused.

ObservedV2Plant explicitly composes prior private motor telemetry and source-time mixins;default runtime unmodified. Originalapply/clip/contacthooks once,originalPD→physicaltargetprojection→D4→currentPD→signedDC→gain→signedDC preserved. Actual all24000PREticks/each2DCstages six-axis changed counts ALLZERO;after-secondDC to held control difference also0. Thus this NEW entire12s records support failure without DC modification,including all76low-total points. Do not fill in old forward/M1 unknown2kHz clipping or infer hardware current/thermal/communications/delivery. Maximum left normal1796.740N@PRE8.513s while same-step heldtau[2.909443,-3.453945,.010661,1.794364,-3.150215,.185670]Nm. Sim heldctrl not measuredhardwaretorque;no unique-cause conclusion.

PublicSignalAdapter normalizes original public packet roles and actual source windows,does not rewrite packet/controllerstate;endpoint/held_command point spans only if known,sampled_boxcar retains true20-point mean windows.1198actual interpolated observation frames/two startup unknowns,0schemaerrors/latch,actual common epoch5.25ms beforepacketepoch and diagnostic after-tick arrivalage15.25ms. Not instantaneous synchronization;mean-window bias persists. Rate/curvature/noise/clock bounds/alpha/true output-torque calibration absent,numeric_bounds_complete/force_input_ready/hardware_sync_proven false in ALLframes. No force/FSM/controller connection,3ms/.55/.8gates unchanged.

ONEnew control trace1200rows pass reduction,0motor/contact payload reads/oldraw/models/physics/controllerreplays/hashrereads. Window/receipt/convex-epoch checks consistent. Target rewrite or common branch lift1atcontrolindex1,not enough type information to call physical clamp/mechanicallimit. Producer-streamed SHA/bytes/line receipts created WHILEWRITING for3newraws;archive stores metadata only without payload reread/hash. New small source/protocol/result/logs/provenance snapshot is not standalone asset workspace. P0 XML/CAD external existing identity or unknownSHA remains as such.

No more same-kind observational/microgap probes or consumed checks;next is physically derived second wheel-leg/VMC mechanism at most1new nominalcase,not a gain grid/oldC3axialD retry/unknown-forcefeedback. Source files/default robot physics/old gates/gains and old results are not rewritten to pass. Original recorder unchanged/one invocation/in-memory sparse-add only;atomic nonforce ownbranch+unique annotatedtag then remote identities verified. No RL worktree/index/main reset/push. Prior5659/4892/f4/a362/c0fe and historical pending archives retained;postreceipt edit rides next real source stage,no receipt archive cycle.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged data')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Prefix/tag exists: resume existing objects,no recorder retry')
 result=json.loads((CASE/'result.json').read_text(encoding='utf-8'))
 reduction=json.loads((R/'T01_OBSERVABILITY_V1/REDUCTION001/RESULT.json').read_text(encoding='utf-8'))
 if not result['complete']or result['controls']!=1200 or result['physics_steps']!=24000 or result['case_screen_pass']is not False:raise RuntimeError('Unexpected case receipt')
 motor=result['private_motor_observation'];signal=result['public_signal_observation']
 if motor['actual_observed_physics_rows']!=24000 or motor['sections']['all']['any_dc_changed_ticks']!=0 or signal['aligned_frames']!=1198 or signal['force_input_ready']is not False:raise RuntimeError('Unexpected observer receipt')
 if not all(reduction['same_actual_case_consistency'].values())or reduction['old_raw_reads']!=0 or reduction['physics_steps']!=0:raise RuntimeError('Unexpected once-reduction receipt')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Keep large payload external:'+str(source))
  put(rel,source.read_bytes())
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','observed_bridge_v1.py','public_signal_adapter_v1.py','diagnostic_stream_v1.py',
 'prepare_observability_v1.py','prepare_observability_v1_001.log','runtime_v2.py','bridge_v2.py','dr_v2.py','model_builder_v2.py',
 'controller_base_v2.py','controller_coord_v2.py','controller_roll_v2.py','controller_heading_v2.py','v2_linearization.py','nominal_gain_v2.json',
 'actuation_telemetry_v1.py','signal_alignment_v1.py','SENSOR_TIME_METADATA_V1/publisher.py',
 'T01_OBSERVABILITY_V1/run_reverse_observe.py','T01_OBSERVABILITY_V1/PROTOCOL.json','T01_OBSERVABILITY_V1/PREPARATION.json',
 'T01_OBSERVABILITY_V1/README.md','T01_OBSERVABILITY_V1/reverse_observe_001.log','T01_OBSERVABILITY_V1/reduce_control_once.py',
 'T01_OBSERVABILITY_V1/reduce_control_once_001.log','T01_OBSERVABILITY_V1/REDUCTION001/START.json','T01_OBSERVABILITY_V1/REDUCTION001/RESULT.json']
 root+=['T01_OBSERVABILITY_V1/runs/'+CASE.name+'/'+name for name in ['config.json','protocol.json','meta.json','result.json']]
 for rel in root:copy(R/rel,Path('payload/v2')/rel)
 for rel in ['physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','sensor_core.py','sensor_core_v4.py','RM_ROBUSTNESS_V1/t01_contact_audit.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','RM_FPS_PLAYER_V1/terrain.py']:
  copy(V1/rel,Path('provenance/v1')/rel)
 receipts=[]
 for receipt in result['producer_raw_receipts']:
  p=Path(receipt['path'])
  if p.stat().st_size!=receipt['bytes']:raise RuntimeError('Closed raw size differs from producer receipt')
  receipts.append(dict(receipt,archival_payload_read=False,archival_payload_hash=False))
 xml=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'
 receipts.append(dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',identity='existing published P0 identity,no archival payload read/hash'))
 cad=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml')
 receipts.append(dict(path=str(cad),bytes=cad.stat().st_size,sha256=None,identity='actual CAD artifact,no archival payload read/hash'))
 put('EXTERNAL_ARTIFACTS.json',json.dumps(receipts,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'))
 put(Path(__file__).name,Path(__file__).read_bytes());listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_reverse_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v2 new reverse actual actuator and source-time observation','--kind','evaluation','--note-file',str(OUT/'NOTE.md'),
 '--validation','ONEnew12s/1200control24000physics,noncontactpass/contactFAIL93.64/98.54%+76low;all24000twoDCstageschanged0;1198actualinterpolation/noalpha/bounds/force;ONEnewtrace1200once/0oldraw;not matchedforward/T01/full36qualification.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotated trial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
