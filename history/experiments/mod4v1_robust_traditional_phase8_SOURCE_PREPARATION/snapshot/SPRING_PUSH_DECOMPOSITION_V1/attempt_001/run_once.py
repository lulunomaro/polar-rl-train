"""Single bounded new NumPy experiment. No SDK, old QA, DR, integration or fitting."""
from pathlib import Path
import json,hashlib,shutil,sys,importlib.util,math,traceback
import numpy as np
import spring_push as helper
O=Path(__file__).resolve().parent;R=O.parent;A=O/'attempt_001'
S=json.loads((O/'SOURCE.json').read_bytes());M=json.loads((O/'METHOD.json').read_bytes())
A.mkdir()
for name in('SOURCE.json','METHOD.json','PREREGISTRATION.json','freeze_scope.py','spring_push.py','run_once.py'):shutil.copyfile(O/name,A/name)
def record(p):
    b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
pre=[]
for row in S['files']:
    p=R/row['relative'];a=record(p);assert a['SHA']==row['SHA']and a['bytes']==row['bytes'];pre.append(a)
assert not any(n=='mujoco'or n.startswith('mujoco.')or n.startswith('physics_bridge')for n in sys.modules)
spec=importlib.util.spec_from_file_location('bounded_spring_nominal_source',R/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py');mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
counts={'models':0,'FK_attempted':0,'FK_completed':0,'terms_calls':0};fklog=[];cache={};checks=0;gates=[];rows=[];guard_tests=[]
def check(ok,label):
    global checks
    checks+=1
    if not bool(ok):raise AssertionError(label)
def serial(x):
    if isinstance(x,np.ndarray):return serial(x.tolist())
    if isinstance(x,(tuple,list)):return[serial(v)for v in x]
    if isinstance(x,dict):return{k:serial(v)for k,v in x.items()}
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(float,np.floating))and not math.isfinite(float(x)):return {'nonfinite':repr(float(x))}
    if isinstance(x,np.floating):return float(x)
    return x
def put(n,x):
    with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(serial(x),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def close4(a,b,label):
    a=np.asarray(a,float);b=np.asarray(b,float);bound=1e-6+1e-8*np.abs(b);err=np.abs(a-b)
    gates.append(dict(kind='torque_Nm',label=label,max_abs_error=float(np.max(err)),error=err,bound=bound))
    check(a.shape==(4,)and b.shape==(4,)and np.isfinite(err).all()and np.all(err<=bound),label)
def power(a,b,label,tref,v):
    bound=1e-6*float(np.sum(np.abs(v)))+1e-8*float(np.sum(np.abs(tref*v)))
    gates.append(dict(kind='virtual_power_W',label=label,abs_error=abs(float(a)-float(b)),bound=bound))
    check(math.isfinite(float(a))and math.isfinite(float(b))and abs(float(a)-float(b))<=bound,label)
class CountedModel(mod.NominalModel):
    def __init__(self):
        counts['models']+=1;check(counts['models']<=1,'one model object');self.active_name='none';super().__init__(fd_rad=1e-5,directional_dt_s=5e-4)
    def fk(self,q4,check_limits=True):
        check(counts['FK_attempted']<27,'27 FK maximum before call')
        counts['FK_attempted']+=1;q=np.array(q4,float,copy=True)
        line=dict(number=counts['FK_attempted'],pose=self.active_name,q_absolute4_rad=q.tolist(),status='ATTEMPTED');fklog.append(line)
        result=super().fk(q4,check_limits=check_limits)
        counts['FK_completed']+=1;key=q.tobytes();check(key not in cache,'no duplicate/invented FK')
        cache[key]=result;line.update(status='COMPLETE',gas_slide2_m=result['joint_values'][self.gas_ids].tolist())
        return result
try:
    model=CountedModel();v=np.array(M['mixed_virtual_qd4_rad_s'],float);ids=model.gas_ids;k=model.stiffness[ids].copy();ref=model.springref[ids].copy();d=model.damping[ids].copy()
    check(len(ids)==2 and np.all(k>0)and np.all(d>=0),'two nominal gas slides')
    def energy(p):
        slide=p['joint_values'][ids]
        return .5*math.fsum(float(kk)*float(ss-rr)**2 for kk,ss,rr in zip(k,slide,ref))
    for name,src in S['poses'].items():
        model.active_name=name;start=counts['FK_completed'];q=np.array(src['reference_absolute_q4_rad'],float);old=np.array(src['original_trim_row6_Nm'],float)
        q.flags.writeable=False;old.flags.writeable=False;qbefore=q.tobytes();oldbefore=old.tobytes()
        counts['terms_calls']+=1;t=model.terms(q,np.zeros(4),np.zeros(4),np.array([0.,0.,9.81]),np.zeros(3),np.zeros(3))
        check(counts['FK_completed']-start==9,'nine internal FK per pose')
        D=t['jacobians']['Djoint'][ids,:].copy();slide=t['gas_slide2'];elastic=k*(ref-slide);tau=t['tauGas4'].copy();grad=[];u_pairs=[]
        for axis in range(4):
            qp=q.copy();qm=q.copy();qp[axis]+=1e-5;qm[axis]-=1e-5
            up=energy(cache[qp.tobytes()]);um=energy(cache[qm.tobytes()]);grad.append((up-um)/(2e-5));u_pairs.append([up,um])
        grad=np.array(grad);sdot=D@v;damp=-d*sdot;total=elastic+damp;total_tau=D.T@total
        gas6=np.array([tau[0],tau[1],0.,tau[2],tau[3],0.]);new=old.copy()
        for axis,val in zip(helper.LEGS,tau):new[axis]=old[axis]+val
        row=dict(name=name,reference_absolute_q4_rad=q.copy(),source_q7_delta=src['source_q7_delta'],gas_names=[model.joints[i]['name']for i in ids],gas_slide2_m=slide.copy(),springref2_m=ref,stiffness2_N_per_m=k,damping2_Ns_per_m=d,elastic_scalar2_N=elastic,Dgas_m_per_rad_2x4=D,tauGas4_Nm=tau,tauGas6_Nm=gas6,static_counter_compensation4_Nm=-tau,original_trim6_Nm=old.copy(),new_static_FF6_Nm=new,U_J=energy(t['jacobians']['pose']),U_plus_minus_J_4x2=u_pairs,minus_gradU_FD4_Nm=-grad,static_nominal_load4_Nm=t['load4'].copy(),static_other_passive4_Nm=t['tauOtherPassive4'].copy(),mixed_virtual_qd4_rad_s=v,mixed_gas_slide_rate2_m_s=sdot,mixed_damping_force2_N=damp,mixed_total_gas_scalar2_N=total,mixed_total_gas_tau4_Nm=total_tau,virtual_power_elastic_W=float(tau@v),virtual_power_elastic_Fslide_W=float(elastic@sdot),virtual_power_minus_gradU_W=float((-grad)@v),virtual_power_total_W=float(total_tau@v),virtual_power_damping_W=float((D.T@damp)@v),tauGas_delta_generalized4_Nm=helper.absolute_tau4_to_delta_generalized(tau),FK_completed_this_pose=9)
        rows.append(row)
        close4(tau,-grad,name+' minus gradient elastic U')
        close4(tau,D.T@elastic,name+' existing-model vs direct D.T elastic')
        close4(new[list(helper.LEGS)]-old[list(helper.LEGS)],tau,name+' add-back sign')
        close4(new[list(helper.LEGS)]-tau,old[list(helper.LEGS)],name+' keep entire original trim remainder')
        power(tau@v,elastic@sdot,name+' elastic virtual work',tau,v)
        power(tau@v,(-grad)@v,name+' independent potential virtual work',tau,v)
        power(total_tau@v,total@sdot,name+' spring+damping duality',total_tau,v)
        power((D.T@damp)@v,-np.sum(d*sdot*sdot),name+' nonpositive damping power',D.T@damp,v)
        dv=np.array([v[0],v[1]-v[0],v[2],v[3]-v[2]])
        power(np.dot(row['tauGas_delta_generalized4_Nm'],dv),tau@v,name+' delta covector virtual work',tau,v)
        check(float((D.T@damp)@v)<=0.,name+' damping not injected/removed')
        check(all(helper.bits(new[i])==helper.bits(old[i])for i in(2,5)),name+' wheels bit-exact unchanged')
        check(gas6[2]==gas6[5]==0.,name+' gas wheel increment zero')
        check(q.tobytes()==qbefore and old.tobytes()==oldbefore,name+' source arrays unchanged')
    check(counts==dict(models=1,FK_attempted=27,FK_completed=27,terms_calls=3),'exact model/FK budget')
    put('ENDPOINTS.json',dict(status='PASS_NOMINAL_ENDPOINT_SIGN_AND_FD_ONLY',source_records=S['files'],endpoints=rows,unknown='Nominal static endpoints only. Old trim internal decomposition/actual DR gas/dynamic interpolation/hardware force remain unverified.'))
    # The public helper reads only precomputed JSON and five bound source files once.
    before=counts.copy();book=helper.load_precomputed();check(book.source_reads==5,'one small-source load')
    for name,src in S['poses'].items():
        e=book.endpoint(name);ff=np.array(src['original_trim_row6_Nm']);q=np.array(src['reference_absolute_q4_rad']);s=np.array(src['source_q7_delta']+[0.]*7)
        s[10],s[11],s[12],s[13]=v[0],v[1]-v[0],v[2],v[3]-v[2];saved=[a.tobytes()for a in(ff,q,s)]
        aq,av=helper.delta14_to_absolute_q4_qd4(s)
        check(np.max(np.abs(np.array(aq)-q))<=1e-14 and np.max(np.abs(np.array(av)-v))<=1e-14,name+' state14 absolute q/rate mapping')
        mapped=helper.absolute_q4_into_delta14(q,s);back,_=helper.delta14_to_absolute_q4_qd4(mapped)
        check(np.max(np.abs(np.array(back)-q))<=1e-14,name+' delta roundtrip')
        for phase in('approach','timed_push','predicted_flight','timed_capture'):
            disabled=book.timed_push_ff6(name,ff,q,phase=phase)
            check(all(helper.bits(a)==helper.bits(b)for a,b in zip(disabled,ff)),name+' default disabled '+phase)
            active=book.timed_push_ff6(name,ff,q,phase=phase,enabled=True)
            expected=e.new_static_FF6_Nm if phase=='timed_push'else tuple(ff)
            check(all(helper.bits(a)==helper.bits(b)for a,b in zip(active,expected)),name+' only timed_push '+phase)
            check(not np.shares_memory(np.asarray(active),ff),name+' returned no mutable array alias')
        check([a.tobytes()for a in(ff,q,s)]==saved,name+' helper input arrays immutable')
        try:e.name='MUTATE'
        except AttributeError:check(True,'frozen endpoint')
        else:check(False,'endpoint mutation')
    e=book.endpoint('pushend');ff=np.array(e.original_trim6_Nm);q=np.array(e.reference_absolute_q4_rad)
    bad=[('q3',[0.]*3),('q5',[0.]*5),('matrix',np.zeros((4,1))),('nan',[math.nan,0.,0.,0.]),('inf',[math.inf,0.,0.,0.]),('bool',[True,0.,0.,0.]),('text',['0',0.,0.,0.]),('complex',[1j,0.,0.,0.]),('bytes',b'0123'),('overflow',[2**4000,0,0,0])]
    for label,x in bad:
        try:book.timed_push_ff6('pushend',ff,x,phase='timed_push',enabled=True)
        except ValueError:guard_tests.append(label);check(True,label+' rejected before any FK')
        else:check(False,label)
    for label,fn in[
        ('state7not14',lambda:helper.delta14_to_absolute_q4_qd4([0.]*7)),
        ('overflow_state',lambda:helper.delta14_to_absolute_q4_qd4([0.,0.,0.,1e308,1e308]+[0.]*9)),
        ('wrong_absolute_semantics',lambda:book.timed_push_ff6('pushend',ff,[q[0],.2,q[2],.2],phase='timed_push',enabled=True)),
        ('badFFshape',lambda:book.timed_push_ff6('pushend',[0.]*5,q,phase='timed_push',enabled=True)),
        ('badFFnan',lambda:book.timed_push_ff6('pushend',[math.nan]*6,q,phase='timed_push',enabled=True)),
        ('trim_mismatch',lambda:book.timed_push_ff6('pushend',[0.]*6,q,phase='timed_push',enabled=True)),
        ('notBool',lambda:book.timed_push_ff6('pushend',ff,q,phase='timed_push',enabled=1))]:
        try:fn()
        except ValueError:guard_tests.append(label);check(True,label+' typed guard')
        else:check(False,label)
    z=ff.copy();z[2]=-0.;z[5]=-0.;zz=book.timed_push_ff6('pushend',z,q,phase='timed_push')
    check(helper.bits(zz[2])==helper.bits(-0.)and helper.bits(zz[5])==helper.bits(-0.),'inactive signed-zero wheels preserved')
    check(counts==before,'runtime helper/negative tests do not call model/FK')
    check(not any(n=='mujoco'or n.startswith('mujoco.')or n.startswith('physics_bridge')for n in sys.modules),'no SDK/plant imported')
    outcome='PASS_NEW_NOMINAL_STATIC_DECOMPOSITION_ONLY';error=None
except Exception:
    outcome='FAILED_PREFIX_PRESERVED_NO_RETRY';error=traceback.format_exc()
result=dict(status=outcome,checks=checks,error=error,counts=counts,NumPy_version=np.__version__,source_before=pre,poses_completed=len(rows),gates=gates,typed_expected_errors=guard_tests,FK_log=fklog,rows=rows,MuJoCo_imported=any(n=='mujoco'or n.startswith('mujoco.')for n in sys.modules),physics_steps=0,hardware_confidence=False,automatic_physics=False,preexecution_sources=[record(A/n)for n in('SOURCE.json','METHOD.json','spring_push.py','run_once.py')])
put('RESULT.json',result)
print(json.dumps(dict(status=outcome,checks=checks,counts=counts,typed_errors=len(guard_tests),max_torque_FD_error_Nm=max((g['max_abs_error']for g in gates if g['kind']=='torque_Nm'and 'gradient'in g['label']),default=None),endpoints=[dict(name=r['name'],tauGas4_Nm=serial(r['tauGas4_Nm']),oldLegFF=[float(r['original_trim6_Nm'][i])for i in helper.LEGS],newLegFF=[float(r['new_static_FF6_Nm'][i])for i in helper.LEGS])for r in rows],error=error),indent=2))
if error:raise SystemExit(1)
