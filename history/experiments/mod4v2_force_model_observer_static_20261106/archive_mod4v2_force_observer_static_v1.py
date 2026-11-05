"""Archive sealed public force model + private observer + input time check once.
No statics/QA/physics rerun. Continue existing commit/tag after push failure.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;V1=W/'mod4v1_lqr_mpc_robust_20261102'
REPO=W/'repo-lqr-robust';BRANCH='mod4v1-lqr-mpc-robust'
ID='mod4v2-force-model-observer-static';BASE=Path('history/experiments/mod4v2_force_model_observer_static_20261106');OUT=REPO/BASE
NOTE='''# MOD4v2 public nominal force model, opt-in private motor observer and retained input-time gates

Same all-traditional-LQR MOD4v2 goal revision29 active/max40. Overall0/36 formally closed,T01 ongoing,35pending. Latest actual M1 case still fails support/contact gates and is not adopted;3v2nominal physical cases remain3600control/72000physics. This stage adds no real integration or robot episode, no old QA/holdout/raw reread, no M2/DR/GPU/SSH/new agent/hardware/motor traffic. Both reused children completed and stopped. Old v1 history,f4a6bcca/a362ef38 and older pending archive gaps remain.

Existing E4 delivered CONTACT_PROXY_V2 only:actualP0 HW300N60 scene SHA c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125,public constants SHA d394608bc662ce5c2b21dd9176668eaa68ebfca7eedac682b218c0a086abc546. 31body/30joint/14.294140288606286kg;actual principal diaginertia+inertial quaternion converted to BODY full tensor. Truehip-local delta branch[-1.0863195404360622,+.49192233306644084],active/follower continuous common lift retained;only five passive angle types wrapped. Gas springref.1706394410901294/k2000/d3,300N/60mm/140-200mmeyes;force curve still unmeasured. P0 authored cylinder tire.0625/.01 and8guides.015 remain,not v1 full-faceted tire representation. No original P0/v1/controller source modification,no K/trim recomputation.

One public nominal model compile,exactly3mj_forward,zero integration attempts,time0 throughout. Poses nominal/common+2pi/asymmetric.45pure nominal FK/54source kin calls/3static sensor fixtures. BODY/COM/inertia errors9.72e-17m/1.71e-16m/5.56e-17kgm2;maxangular Jacobian2.61e-11,gravity projection5.26e-11Nm,passive projection0. Original trim naturally solves chassis-Z[70.0574159960,70.1681002673]N,axial compression[69.3482152023,69.4577790018]N,Tp_y[2.3961313931,2.3999170597]Nm,not hardcoded half-weight. These are coordinate expressions of the SAME planar load,not new independent measurements/contact moments/contact identity. Warmup first2None,third fixture confidence~.49;hardcap<=.55 retained,unknownNone. Runtime only NumPy/stdlib,noSDK/DR/root/world/contact/random-parameter input. Gas hysteresis,guide/wheel spin/drive reaction,soft closure and calibration/timing uncertainties remain;noRNE/dynamicforce/hardware/T01/T24 qualification.

Parent added DEFAULT-OFF actuation telemetry mixin+optional V2Plant adapter,NOT wired into current runtime. Original clip/apply/contact callbacks called once,original actuation values returned;no extra model/RNG/step/clip/target queue/sensor publication. Logs first signed-DC input/output changes,post-gain second signed-DC changes,then actual held d.ctrl after mechanical power stage,with PREtick/POSTtime. Private grading diagnostics must never enter controller/proxy/FSM. Changed-input duty is not rail occupancy or measured motor current/torque/thermal/hardware delivery. Prior M1 actual2kHz saturation duty stays UNKNOWN.

NEW observer dry test6prescribed profiles:original apply+clip methods extracted unchanged,clock/contact are explicit stubs,realD4 reset/process methods without constructor/sample/RNG/model. Bare/on/off held output difference0Nm,761assertions,base120drysubstepsperarm+20disabletoggle=380stubclockcalls total. q/dq are deliberately prescribed,not physical trajectories. Realmodel/physics/oldcase reads0. Only observer transport/call-order equivalence,not independent actuator/dynamics/fullrobotintegration/WCET. No old QA rerun.

NEW input-time contract check6metadata examples/18assertions reuses sealed ContactProxy.step guards with INERTmodel,zero realFK/forceevaluation/model/forward/physics/oldraw. Source20pointPREwindow example has gyro/qd center~endpoint-5.25ms vs encoder endpoint/heldtorque~endpoint-.5ms;shared10msD3 translation does not remove skew. Original3msskew/30msage/cap unchanged;mixed/missing/future/stale epochs returnNone. Hypothetical equal metadata only reacheswarmup and is explicitly NOT alignment proof. No production resampler/packetadapter or controller connection exists. Next real work is sensor-side timing declarations/bounded history alignment with uncertainty,not copying endpoint epoch into every channel or widening gates.

Snapshot selected small source/constants/protocol/results/prefix/logs and provenance only,not standalone fullassetworkspace. Original P0 XML only external path/size/publishedSHA,no archival payload read/hash. All checks already consumed;never rerun for archive. Original recorder unchanged/one invocation/in-memory sparse-add adapter;only own branch+unique annotatedtrial atomicnonforcepush/exactremoteown-tag-peeled checks. No main/RL-worktree reset/push;mainread-only observation. Postreceipt edit rides next realstage,no receipt-archive loop.
'''
def main():
 def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True).stdout.strip()
 if git('branch','--show-current')!=BRANCH or git('diff','--cached','--name-only'):raise RuntimeError('Wrong branch or staged changes')
 if OUT.exists()or git('tag','--list',f'trial-*-{ID}'):raise RuntimeError('Existing prefix/tag: resume existing objects, do not rerecord')
 model=json.loads((R/'CONTACT_PROXY_V2/RESULT.json').read_text(encoding='utf-8'))
 observer=json.loads((R/'ACTUATION_TELEMETRY_V1/check001/result.json').read_text(encoding='utf-8'))
 timing=json.loads((R/'PROXY_INPUT_TIME_V1/check001/result.json').read_text(encoding='utf-8'))
 if model['counts']['mj_forward_calls']!=3 or model['counts']['forbidden_integration_attempts']!=0 or not model['source_before_after_equal']:raise RuntimeError('Unexpected static receipt')
 if not observer['passed']or observer['max_held_tau_difference_Nm']!=0 or timing['force_evaluations']!=0:raise RuntimeError('Unexpected input/observer receipt')
 OUT.mkdir(parents=True,exist_ok=False);selected=[]
 def put(rel,data):
  p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);selected.append(p.relative_to(REPO).as_posix())
 def copy(source,rel):
  if source.stat().st_size>2_000_000:raise RuntimeError('Large payload remains external: '+str(source))
  put(rel,source.read_bytes())
 root=['TERRAIN_ADAPTATION_TASKS_V2.md','actuation_telemetry_v1.py','bridge_motor_telemetry_v2.py','verify_actuation_telemetry_v1.py','verify_actuation_telemetry_v1_001.log',
 'check_proxy_input_timing_v1.py','check_proxy_input_timing_v1_001.log','nominal_gain_v2.json','bridge_v2.py','dr_v2.py','runtime_v2.py']
 root += ['ACTUATION_TELEMETRY_V1/'+p for p in ['README.md','check001/protocol.json','check001/result.json']]
 root += ['PROXY_INPUT_TIME_V1/check001/'+p for p in ['protocol.json','result.json']]
 root += ['CONTACT_PROXY_V2/'+p for p in ['export_public_nominal.py','prepare_sources.py','PREPARATION_PREEXEC.json','PUBLIC_NOMINAL_CONSTANTS.json','nominal_model.py','contact_proxy.py','SOURCE_DERIVATION.json','validate_static_once.py','STATIC_PREEXEC.json','STATIC_PREFIX_01.json','STATIC_PREFIX_02.json','STATIC_PREFIX_03.json','RESULT.json','README.md']]
 for rel in root:copy(R/rel,Path('payload/v2')/rel)
 copy(W/'traditional_control_20261101/control_core.py',Path('provenance/original_clip/control_core.py'))
 copy(V1/'physics_bridge.py',Path('provenance/v1/physics_bridge.py'))
 copy(V1/'physics_bridge_v3.py',Path('provenance/v1/physics_bridge_v3.py'))
 package=W/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
 for name in ['kinematics_v2.py','model_parameters.json','reports/model_manifest.json']:
  copy(package/name,Path('provenance/P0')/name)
 xml=package/'mjcf/scene.xml';external=[dict(path=str(xml),bytes=xml.stat().st_size,sha256='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125',reason='Original public asset external; existing static/runtime identity, no archival payload read')]
 put('EXTERNAL_ARTIFACTS.json',json.dumps(external,indent=2).encode('utf-8'));put('NOTE.md',NOTE.encode('utf-8'));put(Path(__file__).name,Path(__file__).read_bytes())
 listing=(BASE/'SELECTED_FILES.txt').as_posix();put('SELECTED_FILES.txt',('\n'.join(selected+[listing])+'\n').encode('utf-8'))
 sys.path.insert(0,str(REPO/'archive_tools'));spec=importlib.util.spec_from_file_location('original_v2_force_observer_recorder',REPO/'archive_tools/record_experiment.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original=mod.git
 def adapted(*args):
  if args and args[0]=='add':args=('add','--sparse',*args[1:])
  try:return original(*args)
  except subprocess.CalledProcessError as e:print('HELPER_GIT_FAILURE',e.stdout,e.stderr,flush=True);raise
 mod.git=adapted
 sys.argv=['record_experiment.py','--id',ID,'--title','Seal MOD4v2 nominal force model, private DC observer and unchanged input time gates','--kind','evaluation','--note-file',str(OUT/'NOTE.md'),
 '--validation','Public P0compile1/forward3/integration0;SDKfree nominal model matched,not contact calibration;new observer761asserts outputdiff0,380stubticks0physics;timegate18asserts0FK,3ms preserved;unintegrated,0of36,no old QA.', '--files',*selected]
 mod.main();head=git('rev-parse','HEAD');tags=git('tag','--points-at','HEAD','--list',f'trial-*-{ID}').splitlines()
 if len(tags)!=1:raise RuntimeError('Expected unique annotated trial')
 tag=tags[0];tagobj=git('rev-parse',tag)
 subprocess.run(['git','-C',str(REPO),'push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'refs/tags/{tag}:refs/tags/{tag}'],check=True)
 refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main',f'refs/heads/{BRANCH}',f'refs/tags/{tag}',f'refs/tags/{tag}^{{}}').splitlines()}
 if refs.get('refs/heads/'+BRANCH)!=head or refs.get('refs/tags/'+tag)!=tagobj or refs.get('refs/tags/'+tag+'^{}')!=head:raise RuntimeError('Remote identity mismatch')
 print(json.dumps(dict(commit=head,tag=tag,tag_object=tagobj,selected_count=len(selected),remote=refs,main_observed_readonly=True),indent=2),flush=True)
if __name__=='__main__':main()
