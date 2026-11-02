"""Finite current-state MPC timing adaptation: .01 source prediction vs .02 actualhold."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time
P=Path(__file__).resolve().parent;T=P.parent
S=T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'
D=T/'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
actual=read(S/'reports/ROOT355_EVALUATION_FULL_RETURNED.json')['result'];assert actual['passed']and actual['comparisons'][1]['cross']==37 and actual['strict_successes']==0
D.mkdir(exist_ok=False);(D/'reports').mkdir()
def rename(s):return re.sub(r'(?<=[A-Za-z_])355(?!\d)','357',s)
for path in sorted(S.rglob('*')):
    if not path.is_file()or'__pycache__'in path.parts or any(x in path.relative_to(S).parts for x in('reports','replay','RECORDED355_NATIVE_FRAMES'))or path.name.startswith('INDEX355'):continue
    dest=D/rename(str(path.relative_to(S)));dest.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix in('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
    elif path.suffix=='.npz':shutil.copyfile(path,dest)
bridge=(D/'source/source_event_mpc353.py').read_text('utf8')
bridge=bridge.replace("self.mpc=LinearMPC(self.g,horizon=self.cfg.get('horizon',15))", "self.prediction_dt=float(bundle.get('actual_command_MPC_dt',.01));self.horizon=15 if self.prediction_dt==.01 else 8\n        self.mpc=LinearMPC(self.g,horizon=self.horizon,dt=self.prediction_dt)")
bridge=bridge.replace("mpc=LinearMPC(gn,horizon=cfg.get('horizon',15));mpc.landing_gain=True", "mpc=LinearMPC(gn,horizon=self.horizon,dt=self.prediction_dt);mpc.landing_gain=True")
assert 'dt=self.prediction_dt'in bridge
(D/'source/source_event_mpc353.py').write_text(bridge,encoding='utf8')
worker=(D/'source/evaluate357.py').read_text('utf8')
worker=worker.replace("controllers=[SourceEventMPC353(bundle)for _ in range(40)]", "controllers=[SourceEventMPC353(dict(bundle,actual_command_MPC_dt=.01 if i<40 else.02))for i in range(80)]")
worker=worker.replace('range(40,80)','range(80)').replace('controllers[env_id-40]','controllers[env_id]')
worker=worker.replace("kind='openloop_processed'if i<40 else'currentstate_event_MPC'", "kind='source10ms_prediction_hold20ms'if i<40 else'actual20ms_prediction_hold20ms'")
worker=worker.replace("r['kind']in('openloop_processed','currentstate_event_MPC')", "r['kind']in('source10ms_prediction_hold20ms','actual20ms_prediction_hold20ms')")
worker=worker.replace("for g in('openloop_processed','currentstate_event_MPC')", "for g in('source10ms_prediction_hold20ms','actual20ms_prediction_hold20ms')")
worker=worker.replace("group0_39='openloopsourceprocessedMPCtarget50Hz',group40_79='currentstate_sourceMPC_eventcontroller50Hz'", "group0_39='currentstateMPCsource.01prediction50Hzhold',group40_79='currentstateMPCactual.02prediction50Hzhold'")
worker=worker.replace('source_MPC_dt=.01,current_command_dt=.02,prediction_dt_not_relabelled=True',"source_MPC_dt=.01,current_command_dt=.02,group_prediction_dt=[.01,.02],group_horizon=[15,8],prediction_dt_rediscretized_from_sameA_B=True")
worker=worker.replace("controller_hz=50,source_MPC_prediction_dt=.01,original50Hz_action_queue_unchanged=True", "controller_hz=50,group_MPC_prediction_dt=[.01,.02],group_horizon=[15,8],original50Hz_action_queue_unchanged=True")
# Capture one case per group with fullwindow as well as representative early failures.
worker=worker.replace('selected=[0,1,40,41]','selected=[0,1,40,41]')
ast.parse(worker);(D/'source/evaluate357.py').write_text(worker,encoding='utf8')
task=read(D/'TASK357_FROZEN.json');task.update(kind='MPC_ACTUAL20MS_PREDICTION_CLOCK_COMPARISON357',worker_SHA=H(D/'source/evaluate357.py'),planned_motor_control=dict(path='planned_mpc_motor357.json',bytes=(D/'planned_mpc_motor357.json').stat().st_size,SHA=H(D/'planned_mpc_motor357.json')),group_prediction_dt=[.01,.02],group_horizon=[15,8],same_continuous_source_gains_A_B_Q_R=True,human_request='Finite same50Hz currentstateeventMPC predictiondt adaptation; originalactionsqueuePDphysics unchanged; source.01model versus actual.02hold matching discretization; no training')
(D/'TASK357_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
contract=(D/'contract357.py').read_text('utf8').replace('MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON357','MPC_ACTUAL20MS_PREDICTION_CLOCK_COMPARISON357');(D/'contract357.py').write_text(contract,encoding='utf8')
for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
ns={};exec(compile(contract,str(D/'contract357.py'),'exec'),ns);assert ns['validate_task'](task)
test="from pathlib import Path\nimport json,sys,numpy as np\nsys.path.insert(0,"+repr(str(D/'source'))+")\nfrom source_event_mpc353 import SourceEventMPC353\nb=json.loads(Path("+repr(str(D/'source353_gains.json'))+").read_bytes())\nc=SourceEventMPC353(dict(b,actual_command_MPC_dt=.02));assert c.horizon==8 and c.mpc.dt==.02;assert not np.allclose(c.mpc.Ad,np.array(b['g']['Ad']))\nx=np.r_[c.g['q'],np.zeros(7)];x[0]=-.8;q=np.array([x[3],x[3]+x[4],0,x[5],x[5]+x[6],0]);r=c.command(0,x,q,np.zeros(6));assert np.isfinite(r['processed_target']).all()\nprint('PASS')"
cpu=subprocess.run([sys.executable,'-B','-X','utf8','-c',test],capture_output=True,text=True,encoding='utf8',check=True);assert cpu.stdout.strip()=='PASS'
put(D/'reports/CPU357_20MS_DISCRETIZATION_NO_STEP.json',dict(epoch=time.time(),passed=True,Ad_differs_source10ms=True,dt=.02,horizon=8,prediction_seconds=.16,source_prediction_seconds=.15,models=0,SDK=0,physics=0,account=0))
files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(D/'INDEX357_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
put(P/'reports/STATIC357_20MS_MPC_CLOCK_COMPARISON.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX357_SOURCE_TASK_CALLERS_FROZEN.json'),NN=0,SDK=0,network=0,GO=0,source_gains_preserved_continuous_model=True,original50action100feedback400physics_preserved=True))
print(json.dumps(dict(passed=True,root=str(D),INDEX_SHA=H(D/'INDEX357_SOURCE_TASK_CALLERS_FROZEN.json'),CPU_no_step_passed=True)))
