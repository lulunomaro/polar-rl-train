"""Independent stdlib linkage/LQR algebra fixtures. No plant/simulator import,
source exec, fitting, training, board access or installation. Writes only HERE.
"""
from pathlib import Path
import hashlib,json,math,random,traceback
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[1]
SENSOR=WORK/'source_snapshots/r00/sensor_core.py'
MANIFEST=WORK.parent/'traditional_control_20261101/reports/model_manifest.json'
GAIN=WORK/'nominal_gain_v1.json'
GAIN_FROZEN=WORK/'source_snapshots/r00/nominal_gain_v1.json'
LABELS=['O','K','P','A','B','C','D','W']

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
def add(a,b):return [a[0]+b[0],a[1]+b[1]]
def norm(a):return math.hypot(*a)
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def wrap(x):return math.atan2(math.sin(x),math.cos(x))
def rot(v,q):
 c,s=math.cos(q),math.sin(q);return [c*v[0]+s*v[1],-s*v[0]+c*v[1]]
def angle(v,w):return wrap(-(math.atan2(w[1],w[0])-math.atan2(v[1],v[0])))
def intersect(a,ra,b,rb,sign):
 d=sub(b,a);length=norm(d)
 if not abs(ra-rb)+1e-7<length<ra+rb-1e-7:raise ValueError('Linkage unreachable or singular')
 t=(ra*ra-rb*rb+length*length)/(2*length);h=math.sqrt(max(0.,ra*ra-t*t));x=[v/length for v in d];y=[-x[1],x[0]]
 return [a[i]+t*x[i]+sign*h*y[i] for i in range(2)]
def pose(p,hip,crank,side,track):
 L=lambda a,b:norm(sub(p[a],p[b]));q={k:rot(v,hip) for k,v in p.items()};q['A']=rot(p['A'],crank)
 q['B']=intersect(q['A'],L('A','B'),q['P'],L('B','P'),math.copysign(1.,cross(sub(p['P'],p['A']),sub(p['B'],p['A']))))
 rocker=angle(sub(p['B'],p['P']),sub(q['B'],q['P']));q['C']=add(q['P'],rot(sub(p['C'],p['P']),rocker))
 q['D']=intersect(q['K'],L('K','D'),q['C'],L('C','D'),math.copysign(1.,cross(sub(p['C'],p['K']),sub(p['D'],p['K']))))
 shin=angle(sub(p['D'],p['K']),sub(q['D'],q['K']));wheel=add(q['K'],rot(sub(p['W'],p['K']),shin))
 return [wheel[0],track/2 if side==0 else -track/2,wheel[1]],wrap(shin-hip)
def kinematics(p,hip,crank,hd,cd,spin,omega,side,track,radius,eps):
 r,knee=pose(p,hip,crank,side,track);der=[]
 for dh,dc in ((eps,0.),(0.,eps)):
  a,ka=pose(p,hip+dh,crank+dc,side,track);b,kb=pose(p,hip-dh,crank-dc,side,track)
  der.append([(a[i]-b[i])/(2*eps) for i in range(3)]+[wrap(ka-kb)/(2*eps)])
 J=[der[col][row] for row in range(4) for col in range(2)]
 relative=[J[2*i]*hd+J[2*i+1]*cd for i in range(3)];kd=J[6]*hd+J[7]*cd;wy=omega[1]+hd+kd+spin
 forward=radius*wy-relative[0]-(omega[1]*r[2]-omega[2]*r[1])
 return {'r':r,'knee':knee,'J':J,'relative':relative,'kneedot':kd,'omega_y':wy,'forward':forward}
def fl(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def arr(v):return '{'+','.join(fl(x) for x in v)+'}'

def main():
 manifest=load(MANIFEST);gain=load(GAIN);frozen=load(GAIN_FROZEN)
 assert gain['gain']['K']==frozen['gain']['K'] and gain['gain']['tau']==frozen['gain']['tau'] and gain['gain']['q']==frozen['gain']['q']
 pins=[{k:manifest['neutral_skeleton_xz_m'][side][k] for k in LABELS} for side in ('left','right')]
 assert all(len(v)==2 and all(math.isfinite(x) for x in v) for p in pins for v in p.values())
 K=gain['gain']['K'];ff=gain['gain']['tau'];reference=gain['gain']['q']+[0.]*7
 assert len(K)==6 and all(len(row)==14 and all(math.isfinite(x) for x in row) for row in K)
 assert len(ff)==6 and len(reference)==14
 track=.4376;radii=[gain['hardware_nominal_spec_radius_m'],gain['wheel_chart_radius_m']]
 selected={'pins_order':LABELS,'side_order':['left','right'],'neutral_skeleton_xz_m':dict(zip(['left','right'],pins)),'track_m':track,
  'radius_options':[{'m':radii[0],'meaning':'hardware nominal specification, not measured'},{'m':radii[1],'meaning':'USD geometric circumradius, not measured rolling radius'}],
  'K':K,'tau_feedforward':ff,'state_reference14':reference,'actuator_rows':'opaque order copied from gain JSON; no guessed HAL permutation',
  'gain_kind':gain['kind'],'gain_declared_model_SHA':gain['model_SHA'],'cad_declared_STEP_SHA':manifest['source']['source_sha256']}
 dump('selected_inputs.json',selected)
 candidates=[(-.5,-.5),(-.2,-.2),(0.,0.),(.25032810955413787,.05032810955413787),(.35,.2),(.1,-.2),(-.2,.1),(.4,.4),(.8,.8),(0.,.4),(0.,-.4),(.2,.7),(-.4,.2)]
 fixtures=[];rejected=[];reference_stencil_delta=0.
 for side in range(2):
  for index,(hip,crank) in enumerate(candidates):
   for radius in radii:
    hd=.2*math.cos(index*.3);cd=-.15*math.sin(index*.2);spin=3.0-index*.2;omega=[.12,-.18,4*math.pi if index%2 else -4*math.pi]
    try:
     e=kinematics(pins[side],hip,crank,hd,cd,spin,omega,side,track,radius,1e-6)
     frozen_eps=kinematics(pins[side],hip,crank,hd,cd,spin,omega,side,track,radius,1e-5)
    except ValueError as exc:
     rejected.append({'side':side,'hip':hip,'crank':crank,'radius':radius,'exception':str(exc)});continue
    reference_stencil_delta=max(reference_stencil_delta,max(abs(a-b) for a,b in zip(e['J'],frozen_eps['J'])))
    fixtures.append({'side':side,'hip':hip,'crank':crank,'hipdot':hd,'crankdot':cd,'spin':spin,'omega':omega,'radius':radius,'expected':e})
 rng=random.Random(20261102);lqr=[]
 for index in range(48):
  x=reference[:] if index==0 else [reference[j]+rng.uniform(-.2,.2) for j in range(14)]
  ref=reference[:];limits=[100. if index<16 else (2. if index<32 else 0.)]*6
  raw=[ff[i]-sum(K[i][j]*(x[j]-ref[j]) for j in range(14)) for i in range(6)]
  out=[min(limits[i],max(-limits[i],raw[i])) for i in range(6)];mask=sum(1<<i for i in range(6) if abs(raw[i])>limits[i])
  lqr.append({'state':x,'reference':ref,'limit':limits,'expected_raw':raw,'expected':out,'saturation_mask':mask})
 dump('python_vectors.json',{'mode':'INDEPENDENT_STDLIB_ALGEBRA_NOT_SIMULATION','reference_fd_eps':1e-6,'frozen_python_fd_eps':1e-5,
  'reference_max_J_delta_vs_frozen_eps':reference_stencil_delta,'kinematics':fixtures,'rejected_pose_fixtures':rejected,'lqr':lqr,
  'pure_spin_constraint':'omega=(0,0,wz), spin_i=-wz*y_i/radius => both estimated forward velocities zero',
  'fixture_limits':'100 / 2 / 0 Nm uniform per test, NOT physical actuator limits'})
 lines=['/* Derived fixture inputs, not a controller selection or measured calibration. */','#ifndef CTK_FIXTURES_H','#define CTK_FIXTURES_H',
 'static const float ctk_fixture_pins32[]='+arr([x for p in pins for k in LABELS for x in p[k]])+';',
 'static const float ctk_fixture_K84[]='+arr([x for row in K for x in row])+';',
 'static const float ctk_fixture_ff6[]='+arr(ff)+';',
 'static const float ctk_fixture_reference14[]='+arr(reference)+';',
 'typedef struct {unsigned side;float hip,crank,hd,cd,spin,omega[3],radius,r[3],knee,J[8],relative[3],kneedot,wy,forward;} ctk_fixture;',
 'static const ctk_fixture ctk_cases[]={']
 for v in fixtures:
  e=v['expected'];pieces=[str(v['side'])]+[fl(v[k]) for k in('hip','crank','hipdot','crankdot','spin')]+[arr(v['omega']),fl(v['radius']),arr(e['r']),fl(e['knee']),arr(e['J']),arr(e['relative']),fl(e['kneedot']),fl(e['omega_y']),fl(e['forward'])]
  lines.append('{'+','.join(pieces)+'},')
 lines+=['};','typedef struct {float state[14],reference[14],limit[6],raw[6],expected[6];unsigned mask;} ctk_lqr_fixture;','static const ctk_lqr_fixture ctk_lqr_cases[]={']
 for v in lqr:lines.append('{'+','.join([arr(v[k]) for k in ('state','reference','limit','expected_raw','expected')]+[str(v['saturation_mask'])])+'},')
 lines+=['};','#endif']
 (HERE/'ctk_fixtures.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 provenance={'sources':[{'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)} for p in [SENSOR,MANIFEST,GAIN,GAIN_FROZEN]],
  'read_method':'Host read before implementation; generator parses JSON data and hashes Python, never executes frozen code',
  'source_ranges':{'sensor_core.py':[34,59],'model_manifest.json':[120,205],'nominal_gain_v1.json':[13,140]},
  'track_m':track,'radii_m':radii,'radius_is_external':True,'gain_and_frozen_parameter_arrays_equal':True,
  'fixture_counts':{'kinematics':len(fixtures),'rejected_math_poses':len(rejected),'lqr':len(lqr)},
  'reference_fd_eps':1e-6,'reference_max_J_delta_vs_frozen_1e5':reference_stencil_delta}
 dump('provenance.json',provenance)
 print(json.dumps(provenance,ensure_ascii=False))

if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'vector_generation_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
