"""Independent stdlib box-QP fixtures; no robot Hessian, source exec or new package.
1D analytic oracle; 2D corner/edge/interior enumeration; n15/n16 exact dyadic KKT.
"""
from pathlib import Path
import hashlib,json,math,random,struct,traceback
HERE=Path(__file__).resolve().parent

def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def clip(x,l,h):return min(h,max(l,x))
def cost(H,f,z):return .5*sum(z[i]*sum(H[i][j]*z[j] for j in range(len(z))) for i in range(len(z)))+sum(a*b for a,b in zip(f,z))
def residual(H,f,l,h,z):
 g=[f[i]+sum(H[i][j]*z[j] for j in range(len(z))) for i in range(len(z))]
 r=[0. if l[i]==h[i] else (max(-g[i],0.) if z[i]==l[i] else (max(g[i],0.) if z[i]==h[i] else abs(g[i]))) for i in range(len(z))]
 return max(r),g

def oracle_2d(H,f,l,h):
 candidates=[]
 for x in (l[0],h[0]):
  candidates.append([x,clip(-(f[1]+H[1][0]*x)/H[1][1],l[1],h[1])])
 for y in (l[1],h[1]):
  candidates.append([clip(-(f[0]+H[0][1]*y)/H[0][0],l[0],h[0]),y])
 det=H[0][0]*H[1][1]-H[0][1]*H[1][0]
 x=(-f[0]*H[1][1]+H[0][1]*f[1])/det;y=(-H[0][0]*f[1]+H[1][0]*f[0])/det
 if l[0]<=x<=h[0] and l[1]<=y<=h[1]:candidates.append([x,y])
 return min(candidates,key=lambda z:cost(H,f,z))

def fl(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def arr(v):return '{'+','.join(fl(x) for x in v)+'}'
def dump(name,obj):(HERE/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def main():
 rng=random.Random(20261102);fixtures=[]
 for k in range(24):
  H=[[f32(rng.uniform(.3,4))]];f=[f32(rng.uniform(-5,5))];l=[f32(rng.uniform(-2,.5))];h=[f32(l[0]+rng.uniform(.2,3))]
  if k%6==0:h=l[:]
  z=[clip(-f[0]/H[0][0],l[0],h[0])]
  fixtures.append({'n':1,'H':H,'f':f,'lo':l,'hi':h,'solution':z,'kind':'analytic_1d','tolerance':2e-5})
 for k in range(36):
  a=f32(rng.uniform(1.5,4));d=f32(rng.uniform(1.5,4));b=f32(rng.uniform(-.95,.95));H=[[a,b],[b,d]]
  f=[f32(rng.uniform(-5,5)) for _ in range(2)];l=[f32(rng.uniform(-2,.2)) for _ in range(2)];h=[f32(v+rng.uniform(.3,2.5)) for v in l]
  if k%9==0:h[0]=l[0]
  if k%13==0:h[1]=l[1]
  z=oracle_2d(H,f,l,h)
  fixtures.append({'n':2,'H':H,'f':f,'lo':l,'hi':h,'solution':z,'kind':'enumerated_2d','tolerance':2e-5})
 for k in range(7):
  n=16 if k==6 else 15;A=[[rng.choice([-2,-1,0,1,2]) for _ in range(n)] for _ in range(n)]
  H=[[float(sum(A[t][i]*A[t][j] for t in range(n))+(20 if i==j else 0)) for j in range(n)] for i in range(n)]
  l=[];h=[];z=[];gradient=[]
  for i in range(n):
   if i%4==0:l.append(.5);h.append(1.5);z.append(.5);gradient.append(.5*(i+1))
   elif i%4==1:l.append(-1.75);h.append(-.25);z.append(-.25);gradient.append(-.5*(i+1))
   elif i%4==2:l.append(-1.);h.append(1.);z.append((i%3-1)*.25);gradient.append(0.)
   else:l.append(.25);h.append(.25);z.append(.25);gradient.append((i+1)*.25)
  f=[-sum(H[i][j]*z[j] for j in range(n))+gradient[i] for i in range(n)]
  assert all(f32(x)==x for row in H for x in row) and all(f32(x)==x for x in f+z+l+h)
  r,g=residual(H,f,l,h,z);assert r==0 and g==gradient
  fixtures.append({'n':n,'H':H,'f':f,'lo':l,'hi':h,'solution':z,'gradient_at_solution':gradient,
                   'kind':'exact_dyadic_KKT','tolerance':2e-4})
 for q in fixtures:
  q['cost']=cost(q['H'],q['f'],q['solution']);q['oracle_residual'],q['oracle_gradient']=residual(q['H'],q['f'],q['lo'],q['hi'],q['solution'])
  assert math.isfinite(q['cost']) and q['oracle_residual']<1e-10
 dump('python_vectors.json',{'purpose':'PURE_NUMERICAL_BOX_QP_NOT_ROBOT_MPC','seed':20261102,'fixtures':fixtures,
  'oracles':'1D closed form; 2D exhaustive edges/corners/interior; n15/n16 exact integer-H/dyadic-z KKT',
  'no_robot_or_physics_import':True,'input_values_quantized_to_binary32':True})
 lines=['/* Synthetic SPD box QP fixtures, not robot/controller parameters. */','#ifndef BQP_FIXTURES_H','#define BQP_FIXTURES_H',
 'typedef struct {unsigned n,exact_kkt;float H[256],f[16],lo[16],hi[16],solution[16],cost,tolerance;} bqp_fixture;',
 'static const bqp_fixture qp_cases[]={']
 for q in fixtures:
  lines.append('{'+','.join([str(q['n']),str(int(q['kind']=='exact_dyadic_KKT')),arr([x for row in q['H'] for x in row])]+[arr(q[k]) for k in ('f','lo','hi','solution')]+[fl(q['cost']),fl(q['tolerance'])])+'},')
 lines+=['};','#endif'];(HERE/'bqp_fixtures.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 counts={kind:sum(q['kind']==kind for q in fixtures) for kind in ['analytic_1d','enumerated_2d','exact_dyadic_KKT']}
 provenance={'generator':'generate_vectors.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'seed':20261102,'fixture_counts':counts,'total_fixtures':len(fixtures),'largest_n':16,
  'n15_count':sum(q['n']==15 for q in fixtures),'n16_count':sum(q['n']==16 for q in fixtures),
  'sources':'Synthetic stdlib algebra only; no parent model or gain/observer files imported or executed.'}
 dump('provenance.json',provenance);print(json.dumps(provenance))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'vector_generation_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
