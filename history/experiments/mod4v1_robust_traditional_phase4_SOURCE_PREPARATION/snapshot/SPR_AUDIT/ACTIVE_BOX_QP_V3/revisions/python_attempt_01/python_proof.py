"""Feasible primal active-set proof and independent quantized double oracles.
No parent controller, dynamics, robot/physics imports or random episode tuning.
"""
from pathlib import Path
import itertools,json,hashlib,traceback
import numpy as np
from scipy.optimize import minimize
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'C_MPC8_NUMERIC_V1'
def q32(x):return np.asarray(x,dtype=np.float32).astype(float)
def kkt(H,f,l,u,z):
 g=H@z+f;r=np.abs(g);r=np.where(z==l,np.maximum(-g,0),r);r=np.where(z==u,np.maximum(g,0),r);r=np.where(l==u,0,r);return float(np.max(r)),g
def cost(H,f,z):return float(.5*z@H@z+f@z)
def active_proof(H,f,l,u,warm,max_pivots=256,tol=1e-9):
 z=np.clip(warm,l,u).copy();state=np.where(l==u,2,np.where(z==l,-1,np.where(z==u,1,0)));trace=[];seen=set();releases=blocks=0
 for pivot in range(max_pivots+1):
  residual,g=kkt(H,f,l,u,z);entry={'pivot':pivot,'kkt':residual,'cost':cost(H,f,z),'free':np.flatnonzero(state==0).tolist(),'state':state.tolist()};trace.append(entry)
  if residual<=tol:return {'status':'CONVERGED','pivots':pivot,'releases':releases,'blocks':blocks,'z':z.tolist(),'kkt':residual,'cost':cost(H,f,z),'trace':trace}
  if pivot==max_pivots:break
  signature=(state.tobytes(),z.tobytes())
  if signature in seen:return {'status':'CYCLE','pivots':pivot,'z':z.tolist(),'kkt':residual,'trace':trace}
  seen.add(signature);free=np.flatnonzero(state==0);p=np.zeros(len(z))
  if len(free):p[free]=np.linalg.solve(H[np.ix_(free,free)],-g[free])
  if not len(free) or np.max(np.abs(p))<=1e-11*(1+np.max(np.abs(z))):
   v=np.where(state==-1,-g,np.where(state==1,g,-np.inf));index=int(np.argmax(v))
   if v[index]<=tol:return {'status':'NO_PROGRESS','pivots':pivot,'z':z.tolist(),'kkt':residual,'trace':trace}
   state[index]=0;releases+=1;entry['release']=index;continue
  alpha=1.;hit=-1
  for i in free:
   a=(u[i]-z[i])/p[i] if p[i]>0 else ((l[i]-z[i])/p[i] if p[i]<0 else np.inf)
   if a<alpha:alpha=max(0.,float(a));hit=int(i)
  before=z.copy();z=np.clip(z+alpha*p,l,u)
  if hit>=0:z[hit]=u[hit] if p[hit]>0 else l[hit]
  old=state.copy();state=np.where(l==u,2,np.where(z==l,-1,np.where(z==u,1,0)));added=int(np.sum((state!=0)&(old==0)));blocks+=added;entry.update(alpha=alpha,blocking=hit,added=added)
  if np.array_equal(z,before) and np.array_equal(state,old):return {'status':'NO_PROGRESS','pivots':pivot+1,'z':z.tolist(),'kkt':kkt(H,f,l,u,z)[0],'trace':trace}
 return {'status':'MAX_PIVOTS','pivots':max_pivots,'z':z.tolist(),'kkt':kkt(H,f,l,u,z)[0],'trace':trace}

def enumeration(H,f,l,u):
 n=len(f);fixed=l==u;best=None
 for choice in itertools.product([-1,0,1],repeat=int(np.sum(~fixed))):
  state=np.full(n,2);state[~fixed]=choice;z=np.where(state==1,u,l).copy();free=np.flatnonzero(state==0);active=np.flatnonzero(state!=0)
  if len(free):z[free]=np.linalg.solve(H[np.ix_(free,free)],-(f[free]+H[np.ix_(free,active)]@z[active]))
  if np.any(z<l-1e-10) or np.any(z>u+1e-10):continue
  z=np.clip(z,l,u);r,_=kkt(H,f,l,u,z)
  if r>1e-8:continue
  c=cost(H,f,z)
  if best is None or c<best[0]:best=(c,z.copy(),r)
 assert best is not None
 return {'method':'independent exhaustive active-face enumeration','z':best[1].tolist(),'cost':best[0],'kkt':best[2]}
def oracle(H,f,l,u):
 if len(f)<=4:return enumeration(H,f,l,u)
 fixed=l==u;F=np.flatnonzero(~fixed);A=np.flatnonzero(fixed);z=np.clip(np.zeros(len(f)),l,u)
 if not len(F):return {'method':'all fixed','z':z.tolist(),'cost':cost(H,f,z),'kkt':0.}
 HR=H[np.ix_(F,F)];fr=f[F]+H[np.ix_(F,A)]@z[A]
 solve=minimize(lambda x:float(.5*x@HR@x+fr@x),z[F],jac=lambda x:HR@x+fr,bounds=list(zip(l[F],u[F])),method='L-BFGS-B',options={'gtol':1e-10,'ftol':1e-15,'maxiter':20000,'maxls':50,'maxcor':20});z[F]=solve.x
 raw={'success':bool(solve.success),'status':int(solve.status),'message':str(solve.message),'nit':int(solve.nit),'z':z.tolist(),'kkt':kkt(H,f,l,u,z)[0]}
 near=1e-7*(1+np.maximum(np.abs(l),np.abs(u)));state=np.where(fixed,2,np.where(z-l<=near,-1,np.where(u-z<=near,1,0)));z[state==-1]=l[state==-1];z[state==1]=u[state==1]
 for iteration in range(256):
  free=np.flatnonzero(state==0);active=np.flatnonzero(state!=0);candidate=z.copy()
  if len(free):candidate[free]=np.linalg.solve(H[np.ix_(free,free)],-(f[free]+H[np.ix_(free,active)]@z[active]))
  violations=np.maximum(l-candidate,candidate-u);violations[state!=0]=-np.inf
  if np.max(violations)>1e-10:
   j=int(np.argmax(violations));state[j]=-1 if candidate[j]<l[j] else 1;z[j]=l[j] if state[j]==-1 else u[j];continue
  z=np.clip(candidate,l,u);r,g=kkt(H,f,l,u,z)
  if r<=1e-8:return {'method':'independent SciPy LBFGSB + exact free-face sign polish','scipy_original':raw,'polish_iterations':iteration+1,'z':z.tolist(),'cost':cost(H,f,z),'kkt':r}
  v=np.where(state==-1,-g,np.where(state==1,g,-np.inf));j=int(np.argmax(v))
  if v[j]<=1e-10:break
  state[j]=0
 return {'method':'independent oracle FAILED','scipy_original':raw,'z':z.tolist(),'cost':cost(H,f,z),'kkt':kkt(H,f,l,u,z)[0]}

def generated_cases():
 budget=json.loads((HERE/'NUMERICAL_BUDGET.json').read_text());spec=budget['independent_stress'];rng=np.random.default_rng(spec['seed'])
 for n in spec['dimensions']:
  for condition in spec['condition_classes']:
   for rep in range(spec['replicates']):
    U,_=np.linalg.qr(rng.normal(size=(n,n)));e=np.geomspace(1/condition,1,n)*100;h=(U*e)@U.T;h=.5*(h+h.T);H=q32(h);f=q32(rng.normal(size=n)*[.5,5.,50.][(rep+n)%3]);l=q32(-rng.uniform(.1,2.,n));u=q32(rng.uniform(.1,2.,n));w=q32(rng.uniform(-3,3,n))
    if rep==1:l[::5]=u[::5]=q32(rng.uniform(-.1,.1,len(l[::5])))
    yield {'name':f'random_n{n}_cond{condition}_r{rep}','family':'independent_random_SPD','n':n,'H':H.tolist(),'f':f.tolist(),'lo':l.tolist(),'hi':u.tolist(),'warm':w.tolist(),'target_condition':condition}
 n=16;H=q32(10*np.ones((n,n))+np.diag(np.linspace(.1,2,n)));f=q32(np.array([(-1)**i*(3+i) for i in range(n)]));l=q32(np.full(n,-.25));u=-l;w=q32(np.where(np.arange(n)%2,.25,-.25))
 yield {'name':'correlated_active16','family':'crafted_active_stress','n':n,'H':H.tolist(),'f':f.tolist(),'lo':l.tolist(),'hi':u.tolist(),'warm':w.tolist()}
 yield {'name':'release_then_block2','family':'crafted_active_stress','n':2,'H':q32([[2,1.8],[1.8,2]]).tolist(),'f':[-3.,1.],'lo':[-.5,-.5],'hi':[.5,.5],'warm':[-.5,-.5]}
 yield {'name':'all_fixed16','family':'fixed_constraints','n':16,'H':np.eye(16).tolist(),'f':q32(np.linspace(-3,3,16)).tolist(),'lo':q32(np.linspace(-.2,.2,16)).tolist(),'hi':q32(np.linspace(-.2,.2,16)).tolist(),'warm':[100.]*16}

def cf(x):
 s=format(float(np.float32(x)),'.9g');return s+('f' if '.' in s or 'e' in s else '.0f')
def main():
 assert not (HERE/'PROBLEMS.json').exists();data=json.loads((OLD/'actual_model_vectors.json').read_text());cases=[]
 for r in data['cases']:
  q={'name':r['name'],'family':'real_H15','n':15,'H':data['H32'],'f':r['f32'],'lo':r['lo32'],'hi':r['hi32'],'warm':r['warm32'],'warm_source':r['warm_source'],'oracle':r['oracle_quantized']};cases.append(q)
 cases+=list(generated_cases());results=[];failed=[]
 for case_id,q in enumerate(cases):
  H=np.asarray(q['H'],float);f=np.asarray(q['f'],float);l=np.asarray(q['lo'],float);u=np.asarray(q['hi'],float);w=np.asarray(q['warm'],float);eigs=np.linalg.eigvalsh(H);q['eigen_min']=float(eigs[0]);q['condition_exact_quantized_double']=float(np.linalg.cond(H))
  if eigs[0]<=0:q['input_quantized_not_SPD']=True;failed.append({'case':case_id,'name':q['name'],'cause':'input quantization lost SPD'});continue
  if 'oracle' not in q:q['oracle']=oracle(H,f,l,u)
  oz=np.asarray(q['oracle']['z']);assert np.all(oz>=l) and np.all(oz<=u);q['oracle_checked_kkt']=kkt(H,f,l,u,oz)[0];assert q['oracle_checked_kkt']<=1e-8,(q['name'],q['oracle_checked_kkt'])
  for mode,start in [('cold',np.zeros(q['n'])),('warm',w)]:
   proof=active_proof(H,f,l,u,start);proof.update(case_id=case_id,name=q['name'],family=q['family'],mode=mode,z_inf_vs_oracle=float(np.max(np.abs(np.asarray(proof['z'])-oz))));results.append(proof)
   if proof['status']!='CONVERGED':failed.append({'case':case_id,'name':q['name'],'mode':mode,'status':proof['status']})
 report={'cases':cases,'no_physics':True,'source':'real H32 inputs unchanged; independent generated H never altered by solver/oracle result','seed':20261102};(HERE/'PROBLEMS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 (HERE/'PYTHON_PROOF.json').write_text(json.dumps({'runs':results,'failures':failed,'math_only':True},indent=2)+'\n',encoding='utf-8')
 h=['#ifndef AB3_CASES_H','#define AB3_CASES_H','#include <stdint.h>','typedef struct {uint32_t n,real;const char *name;float H[256],f[16],lo[16],hi[16],warm[16];} ab3_fixture;','static const ab3_fixture ab3_cases[]={']
 for q in cases:
  H=np.zeros((16,16));H[:q['n'],:q['n']]=q['H'];arrays=[H.ravel()]
  for key in ['f','lo','hi','warm']:
   a=np.zeros(16);a[:q['n']]=q[key];arrays.append(a)
  h.append('{'+str(q['n'])+'u,'+('1u' if q['family']=='real_H15' else '0u')+',"'+q['name']+'",'+','.join('{'+','.join(cf(x) for x in a)+'}' for a in arrays)+'},')
 h+=['};','#endif'];(HERE/'ab3_cases.h').write_text('\n'.join(h)+'\n',encoding='utf-8')
 print(json.dumps({'problems':len(cases),'real_H15':18,'Python_runs':len(results),'proof_failures':failed,'max_pivots':max(r['pivots'] for r in results),'active_real_max_pivots':max(r['pivots'] for r in results if r['family']=='real_H15'),'physics_steps':0},indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'python_proof_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
