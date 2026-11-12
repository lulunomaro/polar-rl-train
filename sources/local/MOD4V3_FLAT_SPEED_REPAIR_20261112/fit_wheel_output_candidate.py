"""Bounded policy repair candidate: fit a common wheel-output change in the existing actor.
Leg outputs, hidden layers, standard deviations, interface and plant stay fixed.
This is an offline least-squares experiment, not a PPO training round.
"""
from pathlib import Path
import sys,torch,numpy as np,json,hashlib,copy,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'))
import kinematics_audit as audit
a=audit.actors['parent'];hidden=torch.nn.Sequential(*list(a.children())[:-1]);X=[];Y=[];samples=[]
files=[R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112/evidence/SPEED_RESPONSE_TRAJECTORIES.npz',T/'evidence/mj_parent_height_grid/TRAJECTORIES.npz']
def add(obs,error,label,weight=1.):
 with torch.no_grad():features=hidden(torch.as_tensor(obs,dtype=torch.float32)).numpy().astype('float64')
 features=np.c_[features,np.ones(len(features))];target=np.full(len(features),.5*error/(.0625*10))
 scale=np.sqrt(weight/len(features));X.append(features*scale);Y.append(target*scale)
 samples.append(dict(label=label,n=len(features),speed_error=float(error),target_common_wheel_change=float(target[0]),weight=weight))
for path in files:
 d=np.load(path)
 for key in d.files:
  if not key.startswith('parent_') or key.startswith('parent_legs_') or not key.endswith('_observation'):continue
  if '_d5_' in key and 'h0.38_' not in key:continue
  prefix=key.removesuffix('_observation');obs=d[key][-200:];v=d[prefix+'_kinematics'][-200:,0];add(obs,float(obs[:,0].mean()-v.mean()),str(path.relative_to(R))+':'+prefix)
path=T/'evidence/native_control_trace_r1/trajectory.npz';d=np.load(path)
for i in range(4):
 obs=d['observation'][180:299,i];v=d['values'][180:299,i,0];add(obs,float(obs[:,0].mean()-v.mean()),'native_original_env'+str(i),weight=1.)
x=np.concatenate(X);y=np.concatenate(Y);ridge=.03;theta=np.linalg.solve(x.T@x+ridge*np.eye(x.shape[1]),x.T@y);pred=x@theta
parent=audit.MODELS['parent'];data=torch.load(parent,map_location='cpu',weights_only=False);state=data['actor_state_dict'];w=state['mlp.6.weight'].clone();b=state['mlp.6.bias'].clone()
state['mlp.6.weight'][4:]+=torch.tensor(theta[:-1],dtype=w.dtype);state['mlp.6.bias'][4:]+=float(theta[-1])
assert torch.equal(state['mlp.6.weight'][:4],w[:4]) and torch.equal(state['mlp.6.bias'][:4],b[:4])
# Old Adam moments for the two edited tensors no longer describe these parameters.
cleared=[]
for key in (7,8):
 st=data['optimizer_state_dict']['state'][key];expected=state['mlp.6.weight' if key==7 else 'mlp.6.bias'].shape
 if st['exp_avg'].shape!=expected:raise ValueError('Unexpected optimizer parameter order')
 cleared.append(dict(id=key,shape=list(st['exp_avg'].shape)));del data['optimizer_state_dict']['state'][key]
meta=dict(method='offline common wheel-output ridge fit inside original35/256/128/64/6actor; no added runtime branch',parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),parent_iteration=data['iter'],PPO_updates=0,ridge=ridge,relaxation=.5,correction_formula='0.5*(cmd_vx - measured_vx_mean)/(wheel_radius.0625*wheel_scale10)',only_edited_actor_tensors=['mlp.6.weight[4:6]','mlp.6.bias[4:6]'],same_common_correction_both_wheels=True,hidden_layers_and_leg_rows_unchanged=True,std_unchanged=True,canonical_plant_unchanged=True,optimizer_moments_cleared_for_modified_tensors=cleared,fit_weighted_rmse=float(np.sqrt(np.mean((pred-y)**2))),delta_l2=float(np.linalg.norm(theta)),samples=samples,acceptance='Candidate only; must pass closed-loop MuJoCo+PhysX and capability retention; least-squares fit is not success evidence')
data['flat_speed_repair']=meta;data['resume_scope']='Derived actor wheel-output-only least-squares candidate; retained parent full critic/RNG/state; Adam moments for edited tensors reset; no PPO updates'
wdir=T/'weights';wdir.mkdir(exist_ok=True);out=wdir/'parent_wheel_head_jointfit_r1.pt';assert not out.exists();torch.save(data,out);meta.update(output=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,epoch=time.time())
(T/'evidence/WHEEL_HEAD_FIT_R1.json').write_text(json.dumps(meta,indent=2));(T/'MODELS_FIT_R1.json').write_text(json.dumps({'parent':str(parent),'candidate':str(out)},indent=2));print(json.dumps({k:meta[k] for k in ('sha256','bytes','fit_weighted_rmse','delta_l2')}))
