"""Fixed named + 192 independent mathematical fixtures; exact rational oracle."""
from pathlib import Path
import copy,hashlib,json,math,random,shutil
from pa1_reference import metrics,oracle
HERE=Path(__file__).resolve().parent
AX=['K','Cbus','drive','regen','Ical','Wcal','TcalLo','TcalHi','reserve','request','lo','hi','wlo','whi','Tlo','Thi','Imax']
SCAL=['Vlo','Vhi','Pe','Pmax','Gmax','Idis','Ichg','VcalLo','VcalHi']
def base(name):
    return dict(name=name,cohort='named',K=[2.]*6,Cbus=[.2]*6,drive=[.8]*6,regen=[.5]*6,Ical=[1e6]*6,Wcal=[1e6]*6,TcalLo=[-100.]*6,TcalHi=[200.]*6,reserve=[0.]*6,request=[0.]*6,lo=[-10.]*6,hi=[10.]*6,wlo=[0.]*6,whi=[0.]*6,Tlo=[20.]*6,Thi=[30.]*6,Imax=[1000.]*6,Vlo=20.,Vhi=24.,Pe=1.,Pmax=10000.,Gmax=10000.,Idis=10000.,Ichg=10000.,VcalLo=1.,VcalHi=1000.)
def main():
    budget=json.loads((HERE/'NUMERICAL_BUDGET.json').read_bytes());assert budget['random_oracle_cases']==192
    cases=[]
    def add(name,**changes):
        d=base(name);d.update(changes);cases.append(d);return d
    add('full_request_all_six',reserve=[.1,-.1,.2,-.2,.3,-.3],request=[1.,2.,-3.,4.,-5.,6.])
    d=add('stall_nonzero_torque_copper',request=[4.,0.,0.,0.,0.,0.],Pe=0.,Pmax=3.);d['K'][0]=1.;d['Cbus'][0]=1.
    add('zero_power_zero_torque',Pe=0.,Pmax=0.)
    add('zero_power_nonzero_request',Pe=0.,Pmax=0.,request=[1.,0.,0.,0.,0.,0.])
    add('fixed_electronics_exact_budget',Pe=3.,Pmax=3.)
    add('fixed_electronics_over_budget',Pe=3.,Pmax=2.)
    d=add('regen_nonzero_forced_braking_box',reserve=[-.5,0.,0.,0.,0.,0.],request=[-4.,0.,0.,0.,0.,0.],Gmax=3.);d['lo'][0]=-5.;d['hi'][0]=-.25;d['wlo'][0]=10.;d['whi'][0]=12.
    d=copy.deepcopy(d);d['name']='zero_reserve_illegal_overspeed_box';d['reserve'][0]=0.;cases.append(d)
    d=add('regen_not_motoring_credit',request=[2.,-2.,0.,0.,0.,0.],Pmax=5.);d['wlo'][:2]=[10.,10.];d['whi'][:2]=[10.,10.]
    d=add('reachable_speed_crosses_zero',request=[3.,0.,0.,0.,0.,0.],Pmax=5.,Gmax=2.);d['wlo'][0]=-6.;d['whi'][0]=8.
    d=add('reserve_positive_power_infeasible',reserve=[2.,0.,0.,0.,0.,0.],request=[3.,0.,0.,0.,0.,0.],Pmax=1.,Pe=0.);d['K'][0]=1.;d['Cbus'][0]=1.
    d=add('reserve_axis_current_infeasible',reserve=[2.,0.,0.,0.,0.,0.],request=[3.,0.,0.,0.,0.,0.]);d['Imax'][0]=.5
    d=add('reserve_charge_power_infeasible',reserve=[-2.,0.,0.,0.,0.,0.],request=[-3.,0.,0.,0.,0.,0.],Gmax=.5);d['wlo'][0]=d['whi'][0]=10.
    d=add('reserve_discharge_bus_current_infeasible',reserve=[2.,0.,0.,0.,0.,0.],request=[3.,0.,0.,0.,0.,0.],Idis=.01);d['wlo'][0]=d['whi'][0]=10.
    d=add('reserve_charge_bus_current_infeasible',reserve=[-2.,0.,0.,0.,0.,0.],request=[-3.,0.,0.,0.,0.,0.],Ichg=.01);d['wlo'][0]=d['whi'][0]=10.
    # Abstract lossless axis0 is a mathematical reserve test, NOT hardware data.
    d=add('preserve_nonzero_reserve_at_s_zero',reserve=[1.,0.,0.,0.,0.,0.],request=[1.,1.,0.,0.,0.,0.],Pmax=0.,Pe=0.);d['Cbus'][0]=0.;d['lo'][0]=.5
    add('fixed_box_exact_request',reserve=[1.]*6,request=[1.]*6,lo=[1.]*6,hi=[1.]*6)
    d=add('reserve_arithmetic_uncertified',reserve=[1.,0.,0.,0.,0.,0.],request=[2.,0.,0.,0.,0.,0.],Pe=0.,Pmax=1.);d['K'][0]=1.;d['Cbus'][0]=1.
    d=add('request_boundary_round_inward',request=[1.,0.,0.,0.,0.,0.],Pe=0.,Pmax=1.);d['K'][0]=1.;d['Cbus'][0]=1.
    d=add('reserve_current_boundary_uncertified',reserve=[1.,0.,0.,0.,0.,0.],request=[2.,0.,0.,0.,0.,0.]);d['K'][0]=1.;d['Imax'][0]=1.
    d=add('subnormal_loss_zero_budget',request=[1.,0.,0.,0.,0.,0.],Pe=0.,Pmax=0.);d['K'][0]=1.;d['Cbus'][0]=math.ulp(0.)
    d=add('nextafter_torque_box_endpoint',request=[math.nextafter(1.,0.),0.,0.,0.,0.,0.]);d['lo'][0]=0.;d['hi'][0]=1.
    d=add('negative_speed_regeneration',request=[2.,0.,0.,0.,0.,0.],Gmax=2.);d['wlo'][0]=-8.;d['whi'][0]=-6.
    d=add('zero_regen_efficiency_no_charge_credit',request=[-2.,0.,0.,0.,0.,0.],Gmax=0.);d['regen'][0]=0.;d['wlo'][0]=d['whi'][0]=10.
    d=add('voltage_lower_drives_bus_current',request=[4.,0.,0.,0.,0.,0.],Idis=.4,Vlo=4.,Vhi=40.);d['wlo'][0]=d['whi'][0]=5.
    d=add('six_axis_mixed_stall_motoring_braking',reserve=[.1]*6,request=[2.,-2.,3.,-3.,4.,-4.],Pmax=20.,Gmax=10.);d['wlo']=[0.,0.,2.,2.,-2.,-2.];d['whi']=d['wlo'].copy()
    add('signed_negative_zero_full_endpoint',request=[-0.,0.,-0.,0.,-0.,0.])
    rng=random.Random(budget['random_seed'])
    for i in range(192):
        d=base('random_%03d'%i);d['cohort']='independent_random_%d'%(i%6)
        d['K']=[rng.uniform(.5,4.)for _ in range(6)];d['Cbus']=[rng.uniform(.05,2.)for _ in range(6)]
        d['drive']=[rng.uniform(.5,1.)for _ in range(6)];d['regen']=[rng.uniform(0.,1.)for _ in range(6)]
        d['reserve']=[rng.choice([-1.,1.])*rng.uniform(.05,.5)for _ in range(6)]
        d['request']=[rng.choice([-1.,1.])*rng.uniform(2.,8.)for _ in range(6)]
        d['wlo']=[rng.uniform(-15.,15.)for _ in range(6)];d['whi']=[a+rng.uniform(.1,6.)for a in d['wlo']]
        d['Pe']=rng.uniform(0.,10.);d['Vlo']=rng.uniform(5.,40.);d['Vhi']=d['Vlo']+rng.uniform(0.,10.)
        a=metrics(d['reserve'],d);b=metrics(d['request'],d)
        caps=[float(max(x,y)*2+1)for x,y in zip(a,b)]
        d['Pmax'],d['Gmax'],d['Idis'],d['Ichg']=caps[:4];d['Imax']=caps[4:]
        mode=i%6
        if mode in (1,2,4,5):
            j={1:0,2:1,4:2,5:3}[mode]
            if b[j]>a[j]:
                value=float(a[j]+(b[j]-a[j])*rng.uniform(.2,.8));d[['Pmax','Gmax','Idis','Ichg'][j]]=value
            else:mode=3
        if mode==3:
            j=i%6;d['Imax'][j]=float((a[4+j]+b[4+j])/2)
        cases.append(d)
    out=HERE/'reference_attempt_01';out.mkdir(exist_ok=False)
    for n in ('make_pa1_cases.py','pa1_reference.py','NUMERICAL_BUDGET.json','MODEL_CONTRACT.json'):shutil.copy2(HERE/n,out/n)
    refs=[]
    for i,d in enumerate(cases):
        o=oracle(d);r=dict(index=i,name=d['name'],cohort=d['cohort'],reserve_feasible=o['reserve_feasible'])
        if o['reserve_feasible']:
            r.update(s_lo=str(o['s_lo']),s_hi=str(o['s_hi']),s_approx=float(o['s_lo']),well_conditioned=o['well_conditioned'],normalized_slope=o['slope'])
        refs.append(r)
    with(HERE/'CASES.json').open('x',encoding='utf-8')as f:json.dump(cases,f,indent=2,allow_nan=False)
    with(HERE/'REFERENCE.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2,allow_nan=False)
    header=['/* Synthetic fixtures only: no real motor/calibration data. */','#ifndef PA1_CASES_H','#define PA1_CASES_H',f'#define PA1_CASE_COUNT {len(cases)}u','#define PA1_CASE_COLUMNS 111u',f'static const char *const pa1_case_names[{len(cases)}]={{'+','.join(json.dumps(d['name'])for d in cases)+'};',f'static const double pa1_case_data[{len(cases)}][111]={{']
    for d in cases:
        row=[float(x)for key in AX for x in d[key]]+[float(d[k])for k in SCAL];assert len(row)==111 and all(math.isfinite(x)for x in row)
        header.append(' {'+','.join(x.hex()for x in row)+'},')
    header+=['};','#endif','']
    with(HERE/'pa1_cases.h').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(header))
    receipt=dict(cases=len(cases),named=len(cases)-192,random=192,seed=budget['random_seed'],oracle_bisections=80,well_conditioned=sum(r.get('well_conditioned',False)for r in refs),reserve_feasible=sum(r['reserve_feasible']for r in refs),physics_imported=False,case_SHA=hashlib.sha256((HERE/'CASES.json').read_bytes()).hexdigest(),reference_SHA=hashlib.sha256((HERE/'REFERENCE.json').read_bytes()).hexdigest())
    with(HERE/'REFERENCE_RECEIPT.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
