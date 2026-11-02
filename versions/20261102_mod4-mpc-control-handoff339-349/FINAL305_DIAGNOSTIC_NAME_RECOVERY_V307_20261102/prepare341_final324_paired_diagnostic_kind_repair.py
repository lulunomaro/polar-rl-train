"""New final324 frozen actual-pair diagnostic following real339 failed crossing/replay."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess, sys, time

P=Path(__file__).resolve().parent
T=P.parent
S=T/'FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V317_20261102'
A=T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102'
E=T/'FINAL324_ACTUAL_PAIRED_DIRECTION_DIAGNOSTIC_V341_20261102'
R=P/'reports'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=read(A/'reports/ROOT339_EVALUATION_FULL_RETURNED.json')['result']
assert result['passed'] and result['strict_successes']==result['crossed_cases']==0
assert (A/'RECORDED339_NATIVE_FRAMES/ACTUAL339_FINAL324_BODY_POSE_SEQUENCE.png').is_file()
assert read(A/'reports/ROOT339_ALL_SSH_CLOSED_FREE.json')['all_owned_SSH_closed']
E.mkdir(exist_ok=False)
(E/'reports').mkdir()
shutil.copytree(A/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
worker=(S/'source/evaluate317.py').read_text('utf8').replace('317','341').replace('305','324')
worker=worker.replace("sys.path[:0]=[str(Path(__file__).resolve().parent),", "sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent),",1)
worker=worker.replace("ck['total_WM_updates']==12468 and ck['actual_new_Pi_updates']==2724", "ck['total_WM_updates']==16879 and ck['actual_new_Pi_updates']==4379")
worker=worker.replace('wm.updates==12468 and all(int(v[\'step\'])==12468', 'wm.updates==16879 and all(int(v[\'step\'])==16879')
worker=worker.replace('source_Pi_updates=2724','source_Pi_updates=4379')
worker=worker.replace("wm.updates==12468 and all(int(value['step'])==12468", "wm.updates==16879 and all(int(value['step'])==16879")
worker=worker.replace("wm.model.out_norm.update=lambda value:None", "wm.model.out_norm.update=lambda value:None\n actual_endpoint_rows=[]\n sampling_rng_before=wm.generator.get_state().clone()")
worker=worker.replace("  actual_phase.append(start_phase.detach().clone())", "  actual_phase.append(start_phase.detach().clone())\n  actual_endpoint_rows.append(dict(p=start_state[:,:3].detach().cpu().tolist(),Rzz=wm.measured_layout.unpack(start_state)[1][:,2,2].detach().cpu().tolist(),phase=start_phase.detach().cpu().tolist(),actions=actions.detach().cpu().tolist(),done=done.bool().detach().cpu().tolist()))")
needle=" put('ACTUAL341_FINAL324_PAIRED_WM_PREDICTION_METRICS.json',report)"
extra=''' # Measure predicted signed movement/yaw against real contiguous endpoints.
 def yaw_from_R(rot):return torch.atan2(rot[...,1,0],rot[...,0,0])
 def wrapped(x):return torch.atan2(torch.sin(x),torch.cos(x))
 actual0=wm.measured_layout.unpack(batch['s'][:,0]);p0=actual0[0];yaw0=yaw_from_R(actual0[1])
 horizons=[]
 for i in(0,3,7,15,31):
  valid=mask[:,i]
  pred_delta=predicted[0][:,i]-p0;real_delta=actual[0][:,i]-p0
  pyaw=wrapped(yaw_from_R(predicted[1][:,i])-yaw0);ryaw=wrapped(yaw_from_R(actual[1][:,i])-yaw0)
  horizons.append(dict(step=i+1,valid=int(valid.sum()),predicted_dx_mean=float(pred_delta[valid,0].mean()),actual_dx_mean=float(real_delta[valid,0].mean()),dx_MAE=float((pred_delta[valid,0]-real_delta[valid,0]).abs().mean()),predicted_dy_mean=float(pred_delta[valid,1].mean()),actual_dy_mean=float(real_delta[valid,1].mean()),predicted_dyaw_mean=float(pyaw[valid].mean()),actual_dyaw_mean=float(ryaw[valid].mean()),dyaw_MAE=float(wrapped(pyaw[valid]-ryaw[valid]).abs().mean()),wrong_dx_sign_fraction=float(((pred_delta[valid,0]*real_delta[valid,0]<0)&(real_delta[valid,0].abs()>.001)).float().mean())))
 # H4 action-gradient diagnostic with all actual labels/actions and frozen WM.
 # This is local model sensitivity, not a measured physical derivative.
 from future_safe_wm_warm273 import context_from_start_anchor273
 from native_depth_world_model50_v255 import normalize_context40
 phase_all=torch.stack(actual_phase)
 b=wm.buffer;slots=b._row(torch.arange(b.size,device=wm.device));candidates=wm.anchors.data['valid_anchor'][slots].nonzero()
 selected=candidates[:min(256,len(candidates))];rows,envs=slots[selected[:,0]],selected[:,1]
 anchor=wm.anchors.gather(rows,envs);initial=wm.measured_layout.unpack(b.data['s'][rows,envs].detach().clone());phase=phase_all[rows,envs]
 action=b.data['a'][rows,envs].detach().clone().requires_grad_(True);previous=b.data['a_prev'][rows,envs].detach().clone()
 state=initial;costs=[];component_means={}
 for i in range(4):
  context=context_from_start_anchor273(anchor,state,i,wm.native_geometry)
  state=wm.model.step(state,action,normalize_context40(context))
  label=reference.labels(phase+i,envs,real.target324)
  cost,terms=tracking_cost324(state,label,learner.legs,learner.wheelbodies,previous,action)
  costs.append(cost)
  for key,value in terms.items():component_means[key]=component_means.get(key,0.)+float(value.detach().mean())/4
  previous=action
 coststack=torch.stack(costs,1)
 exp_loss=-torch.exp(-coststack/5.).sum(1).mean()
 direct_loss=coststack.sum(1).mean()/5.
 exp_grad=torch.autograd.grad(exp_loss,action,retain_graph=True)[0]
 direct_grad=torch.autograd.grad(direct_loss,action)[0]
 assert torch.isfinite(exp_grad).all()and torch.isfinite(direct_grad).all()
 sensitivity=dict(scope='frozenWM H4 actionheldconstant sensitivity atactualobservedstarts;NOTactualphysicalfiniteDifference',sample_count=len(envs),source_phase_min=int(phase.min()),source_phase_max=int(phase.max()),cost_mean=float(coststack.detach().mean()),cost_max=float(coststack.detach().max()),exp_negative_return=float(exp_loss.detach()),direct_scaled_cost=float(direct_loss.detach()),exp_gradient_L2=float(exp_grad.norm()),direct_gradient_L2=float(direct_grad.norm()),exp_gradient_per_action_mean=exp_grad.mean(0).cpu().tolist(),direct_gradient_per_action_mean=direct_grad.mean(0).cpu().tolist(),tracking_components=component_means,optimizer_steps=0)
 report.update(direction_horizons=horizons,model_local_action_sensitivity=sensitivity)
 put('ACTUAL341_FINAL324_PAIRED_WM_PREDICTION_METRICS.json',report)
 put('ACTUAL341_REAL_ENDPOINT_DIRECTION_ROWS.json',dict(epoch=time.time(),schema='64controlsx80environments startp_Rzz_phase_action_done',rows=actual_endpoint_rows,model_reads=0,source='new341actualownphysicalmeasurement'))
'''
assert needle in worker
worker=worker.replace(needle,extra)
with (E/'source/evaluate341.py').open('x',encoding='utf8')as f:f.write(worker)
contract=(S/'contract317.py').read_text('utf8').replace('317','341').replace('305','324')
with (E/'contract341.py').open('x',encoding='utf8')as f:f.write(contract)
parent=(A/'target339_parent.py').read_text('utf8').replace('339','341').replace('controls_max=400,physics_max=3200','controls_max=64,physics_max=512')
with (E/'target341_parent.py').open('x',encoding='utf8')as f:f.write(parent)
runner=(A/'run339_eval_once.py').read_text('utf8').replace('339','341')
with (E/'run341_eval_once.py').open('x',encoding='utf8')as f:f.write(runner)
shutil.copyfile(A/'reference324.npz',E/'reference324.npz')
task=read(S/'TASK317_FROZEN.json')
current=read(A/'TASK339_FROZEN.json')
for key in('model_path','model_SHA','model_bytes','source_full_CPU_receipt_SHA','source_run','GPU_UUID','reference'):
    task[key]=current[key]
task.update(kind='FROZEN_FINAL324_ACTUAL_PAIRED_WM_DIAGNOSTIC341',expected_Pi_updates=4379,max_controls=64,worker_SHA=H(E/'source/evaluate341.py'),worker_seconds=900)
with (E/'TASK341_FROZEN.json').open('x',encoding='utf8')as f:json.dump(task,f,indent=2)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'))
namespace={}
exec(compile(contract,str(E/'contract341.py'),'exec'),namespace)
assert namespace['validate_task'](task)
probe="from pathlib import Path\np=Path("+repr(str(E/'source/evaluate341.py'))+")\ns=p.read_text('utf8');exec(compile(s[:s.index('p=argparse.ArgumentParser()')],str(p),'exec'),dict(__file__=str(p)))\nprint('PASS')"
checked=subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=E/'source',capture_output=True,text=True,encoding='utf8',check=True)
assert checked.stdout.strip()=='PASS'
assert 'wm.updates==12468' not in worker and 'source_Pi_updates=2724' not in worker
rows=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))if path.is_file()]
index=E/'INDEX341_EVAL_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),files=rows,kind='FINAL324_ACTUAL_PAIRED_H4_H32_AND_ACTIONSENSITIVITY_DIAGNOSTIC341'),f,indent=2)
report=dict(epoch=time.time(),passed=True,root=str(E),INDEX=str(index),INDEX_SHA=H(index),new_purpose='measureactualfinal324WMdirections/H4andH32pairedprediction/localactiongradient after independent339 failure andnativeview',
    inherited_actual317_protocol=True,actor_andWM_frozen=True,normalizers_frozen=True,optimizer_steps=0,account_writes=0,GO=0,model_reads_preparation=0,network=0,actual_diag_not_run=True,
    physical_derivative_measured=False,local_model_gradient_notphysicalproof=True,old339_skill_result_preserved=True)
with (R/'STATIC341_FINAL324_PAIRED_DIRECTION_DIAGNOSTIC.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
