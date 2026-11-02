"""Actual-model H/f fixtures + independent SciPy analytic-gradient oracle.
No parent controller/plant imports or physics steps. Existing NumPy/SciPy only.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,math,traceback
import numpy as np
from scipy.optimize import minimize
import scipy
from build_condensed import HERE,WORK,SOURCE,MODEL,sha,condensed

def dump(name,obj):(HERE/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def kkt(H,f,z,lo,hi):
 g=H@z+f;r=g.copy();r[(lo==hi)]=0;r[(z==lo)&(g>0)]=0;r[(z==hi)&(g<0)]=0
 return float(np.max(np.abs(r)))
def oracle(H,f,lo,hi):
 fun=lambda z:.5*float(z@H@z)+float(f@z)
 jac=lambda z:H@z+f
 settings={'gtol':1e-10,'ftol':1e-15,'maxiter':20000,'maxls':50,'maxcor':20}
 result=minimize(fun,np.clip(np.zeros(len(f)),lo,hi),jac=jac,bounds=list(zip(lo,hi)),method='L-BFGS-B',options=settings)
 z=np.clip(result.x,lo,hi)
 original={'method':'SciPy L-BFGS-B analytic gradient','options':settings,'success':bool(result.success),'status':int(result.status),
           'message':str(result.message),'nit':int(result.get('nit',0)),'nfev':int(result.nfev),'raw_kkt':kkt(H,f,z,lo,hi),
           'raw_x':z.tolist(),'raw_cost':fun(z)}
 # Independent active-face equality/KKT polish, not coordinate descent. Preserve
 # the original optimize status even if its function-tolerance stop is early.
 active=np.zeros(len(f),dtype=int);active[np.abs(z-lo)<1e-7]=-1;active[np.abs(z-hi)<1e-7]=1;active[lo==hi]=2
 for iteration in range(201):
  z[active==-1]=lo[active==-1];z[active==1]=hi[active==1];z[active==2]=lo[active==2]
  fixed=np.flatnonzero(active!=0);free=np.flatnonzero(active==0);target=z.copy()
  if len(free):target[free]=np.linalg.solve(H[np.ix_(free,free)],-f[free]-H[np.ix_(free,fixed)]@z[fixed])
  if np.any(target[free]<lo[free]) or np.any(target[free]>hi[free]):
   d=target-z;alpha=1.;hit=None;hit_sign=0
   for i in free:
    if d[i]>0 and target[i]>hi[i]:a=(hi[i]-z[i])/d[i];sgn=1
    elif d[i]<0 and target[i]<lo[i]:a=(lo[i]-z[i])/d[i];sgn=-1
    else:continue
    if a<alpha:alpha=max(0.,float(a));hit=int(i);hit_sign=sgn
   if hit is None:raise RuntimeError('Oracle active-face boundary search failed')
   z=np.clip(z+alpha*d,lo,hi);active[hit]=hit_sign;continue
  z=target;g=H@z+f;viol=np.zeros(len(f));viol[active==-1]=np.maximum(-g[active==-1],0);viol[active==1]=np.maximum(g[active==1],0)
  if np.max(viol)>1e-8:active[int(np.argmax(viol))]=0;continue
  residual=kkt(H,f,z,lo,hi)
  if residual>1e-8 or np.any(z<lo) or np.any(z>hi):raise RuntimeError(f'Oracle KKT certificate failed {residual}')
  return {'scipy_original':original,'polish':'free-face linear solve + active KKT sign release, max200, absolute1e-8',
          'polish_iterations':iteration+1,'z':z.tolist(),'cost':fun(z),'kkt':residual,'active_lower':np.flatnonzero((z==lo)&(lo!=hi)).tolist(),
          'active_upper':np.flatnonzero((z==hi)&(lo!=hi)).tolist(),'fixed':np.flatnonzero(lo==hi).tolist()}
 raise RuntimeError('Oracle active-face iteration limit')
def fl(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def arr(v):return '{'+','.join(fl(x) for x in v)+'}'

def main():
 raw,A,B,Q,P,F,G,W,Hraw,H,H32=condensed();Hq=H32.astype(float);n=15;definitions=[]
 def case(name,x=None,last=0.,ref=None,vref=0.,cap=5.):
  definitions.append({'id':len(definitions),'name':name,'x8':x or [0.]*8,'last_u':last,'ref8':ref or [0.]*8,'vref':vref,'lo':[-cap]*n,'hi':[cap]*n})
 case('equilibrium')
 case('position_plus_2cm',[.02,0,0,0,0,0,0,0]);case('position_minus_2cm',[-.02,0,0,0,0,0,0,0])
 case('pitch_plus_10mrad',[0,.01,0,0,0,0,0,0]);case('pitch_minus_10mrad',[0,-.01,0,0,0,0,0,0])
 case('velocity_plus_point1',[0,0,0,0,.1,0,0,0]);case('velocity_minus_point1',[0,0,0,0,-.1,0,0,0])
 mixed=[.02,.008,-.004,.003,.08,-.04,.02,-.01]
 case('mixed_small_errors_with_lag',mixed,last=.15)
 case('hip_average_5mrad',[0,0,.005,0,0,0,0,0]);case('delta_average_5mrad',[0,0,0,.005,0,0,0,0])
 case('velocity_reference_point4',ref=[.03,0,0,0,.4,0,0,0],vref=.4)
 case('position_active_point15',[.02,0,0,0,0,0,0,0],cap=.15)
 case('pitch_active_point25',[0,.015,0,0,0,0,0,0],cap=.25)
 case('velocity_active_point5',[0,0,0,0,-.25,0,0,0],cap=.5)
 case('mixed_active_point5',mixed,last=.15,cap=.5)
 case('tracking_active_point4',ref=[.03,0,0,0,.8,0,0,0],vref=.8,cap=.4)
 case('asymmetric_scheduled_boxes',mixed,cap=.4);definitions[-1]['lo']=[-.2]*n;definitions[-1]['hi']=[.1 if i<5 else .4 for i in range(n)]
 case('fixed_first_common_input',mixed,cap=.4);definitions[-1]['lo'][0]=definitions[-1]['hi'][0]=0.
 cases=[];previous=None
 for d in definitions:
  state=np.r_[d['x8'],d['last_u']];refs=np.tile(np.r_[d['ref8'],0.],(n,1));refs[:,0]+=np.arange(1,n+1)*.01*d['vref']
  f=2*G.T@W@(F@state-refs.ravel());fq=f.astype(np.float32).astype(float);lo=np.asarray(d['lo']);hi=np.asarray(d['hi']);lq=lo.astype(np.float32).astype(float);hq=hi.astype(np.float32).astype(float)
  o64=oracle(H,f,lo,hi);oq=oracle(Hq,fq,lq,hq)
  warm=np.zeros(n) if previous is None else np.r_[previous[1:],previous[-1]];warm=np.clip(warm,lq,hq).astype(np.float32).astype(float)
  previous=np.asarray(oq['z'])
  free=np.linalg.solve(H,-f)
  item={**d,'f64':f.tolist(),'f32':fq.tolist(),'lo32':lq.tolist(),'hi32':hq.tolist(),'warm32':warm.tolist(),
        'warm_source':'zeros' if d['id']==0 else f'shifted previous synthetic case {d["id"]-1} quantized oracle; not closed-loop data',
        'oracle64':o64,'oracle_quantized':oq,'input_quantization_z_inf':float(np.max(np.abs(np.asarray(o64['z'])-oq['z']))),
        'unconstrained_free_z':free.tolist(),'unconstrained_feasible':bool(np.all(free>=lo)&np.all(free<=hi))}
  if np.all(np.asarray(d['ref8'])==0) and d['vref']==0 and item['unconstrained_feasible']:
   item['first_free_vs_DARE_abs']=abs(float(free[0])-float((-np.asarray(raw['K'])@state).item()))
  cases.append(item)
 dump('actual_model_vectors.json',{'mode':'ACTUAL_MODEL_H_NUMERICAL_ONLY_NOT_PHYSICS','H64':H.tolist(),'H32':Hq.tolist(),'cases':cases})
 lines=['/* Actual MPC8+lag9 H, not firmware qualification or live controller. */','#ifndef MPC8_REAL_FIXTURES_H','#define MPC8_REAL_FIXTURES_H',
  'static const float model_H225[]='+arr(Hq.ravel())+';',
  'typedef struct {const char *name;float f[15],lo[15],hi[15],warm[15];} actual_fixture;',
  'static const actual_fixture actual_cases[]={']
 for c in cases:lines.append('{"'+c['name']+'",'+','.join(arr(c[k]) for k in ('f32','lo32','hi32','warm32'))+'},')
 lines+=['};','#endif'];(HERE/'actual_fixtures.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 dare=A.T@P@A-P-A.T@P@B@np.linalg.solve(np.asarray([[float(raw['R'])]])+B.T@P@B,B.T@P@A)+Q
 provenance={'source':{'path':str(SOURCE),'bytes':SOURCE.stat().st_size,'sha256':sha(SOURCE)},'model':{'path':str(MODEL),'bytes':MODEL.stat().st_size,'sha256':sha(MODEL)},
  'generator':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},'NumPy':np.__version__,'SciPy':scipy.__version__,'python':sys.version,
  'n':n,'state8':raw['state8'],'input':raw['input'],'H_condition_2':float(np.linalg.cond(H)),'H32_condition_2':float(np.linalg.cond(Hq)),
  'H_raw_asymmetry_max':float(np.max(np.abs(Hraw-Hraw.T))),'H32_exact_symmetric':bool(np.array_equal(H32,H32.T)),
  'DARE_absolute_residual_inf':float(np.max(np.abs(dare))),'cases':len(cases),'original_unconstrained_cases':sum(c['unconstrained_feasible'] for c in cases),
  'active_cases':sum(bool(c['oracle_quantized']['active_lower'] or c['oracle_quantized']['active_upper'] or c['oracle_quantized']['fixed']) for c in cases),
  'max_input_quantization_z_inf':max(c['input_quantization_z_inf'] for c in cases),
  'max_oracle_quantized_KKT':max(c['oracle_quantized']['kkt'] for c in cases),
  'max_raw_SciPy_KKT':max(c['oracle_quantized']['scipy_original']['raw_kkt'] for c in cases),
  'SciPy_non_success_preserved_count':sum(not c['oracle_quantized']['scipy_original']['success'] for c in cases),
  'parent_imported':False,'mujoco_loaded':any(k=='mujoco' or k.startswith('mujoco.') for k in sys.modules)}
 assert not provenance['mujoco_loaded'];dump('provenance.json',provenance);print(json.dumps(provenance,indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'fixture_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
