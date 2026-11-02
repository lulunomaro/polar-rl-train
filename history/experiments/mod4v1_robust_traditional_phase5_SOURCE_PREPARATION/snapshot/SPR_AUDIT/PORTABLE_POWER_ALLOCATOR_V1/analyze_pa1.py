"""Grade saved C outputs against independent exact reference; no executable rerun."""
from pathlib import Path
from fractions import Fraction as F
import csv,hashlib,json,math,re,struct,sys
from pa1_reference import metrics,limits,inside_box,feasible,line,q
HERE=Path(__file__).resolve().parent
AX=['K','Cbus','drive','regen','Ical','Wcal','TcalLo','TcalHi','reserve','request','lo','hi','wlo','whi','Tlo','Thi','Imax']
SCAL=['Vlo','Vhi','Pe','Pmax','Gmax','Idis','Ichg','VcalLo','VcalHi']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(x):return struct.pack('<d',float(x))
def main():
    attempt=int(sys.argv[1]);budget=json.loads((HERE/'NUMERICAL_BUDGET.json').read_bytes());prereg=json.loads((HERE/'PREREGISTRATION_RECEIPT.json').read_bytes())
    assert sha(HERE/'NUMERICAL_BUDGET.json')==prereg['budget_SHA']
    cases=json.loads((HERE/'CASES.json').read_bytes());refs=json.loads((HERE/'REFERENCE.json').read_bytes());build=json.loads((HERE/f'HOST_BUILD_{attempt:02d}.json').read_bytes())
    raw=[json.loads(x)for x in(HERE/f'C_RUNS_{attempt:02d}.jsonl').read_bytes().splitlines()];env=raw[0];rows=raw[1:]
    assert env['kind']=='HOST_ENVIRONMENT'and env['DBL_MANT_DIG']==53 and env['FLT_EVAL_METHOD']==0 and env['RN_no_FTZ_DAZ']
    assert len(rows)==len(cases)==219
    checks=0;errors=[];comparisons=[];invalid=[];statuses={};maxgap=0.;maxline=0.;well=0;validn=0;full=0
    def check(value,case,gate,detail=None):
        nonlocal checks
        checks+=1
        if not bool(value):errors.append(dict(case=case,gate=gate,detail=detail))
    for index,(d,ref,r)in enumerate(zip(cases,refs,rows)):
        name=d['name'];status=r['status'];statuses[str(status)]=statuses.get(str(status),0)+1
        check(r['index']==index and r['name']==name,name,'identity')
        flat=[float(v)for a in AX for v in d[a]]+[float(d[s])for s in SCAL]
        check(len(r['actual_input111'])==111,name,'actual_input_count')
        for j,(a,b)in enumerate(zip(flat,r['actual_input111'])):check(bits(a)==bits(b),name,'actual_input_bit_exact',j)
        result=dict(index=index,name=name,cohort=d['cohort'],status=status,valid=r['valid'],s=r['s'],reference_s=None,s_gap=None,well_conditioned=ref.get('well_conditioned',False))
        if r['valid']:
            validn+=1;check(status==0,name,'valid_status');check(0.<=r['s']<=r['hi']<=1.,name,'s_range')
            check(q(r['hi'])-q(r['s'])<=F(1,2**40),name,'bisection_width')
            check(r['iterations']==(0 if r['s']==1. else 40),name,'fixed_iteration_count')
            check(inside_box(r['tau'],d),name,'actual_torque_box_zero_tolerance')
            true_metrics=metrics(r['tau'],d);cap=limits(d)
            real_line=line(d,q(r['s']));line_metrics=metrics(real_line,d)
            for j,(actual,real,limit)in enumerate(zip(true_metrics,line_metrics,cap)):
                check(actual<=limit,name,'actual_electrical_constraint_zero_tolerance',j)
                check(real<=limit,name,'true_continuous_endpoint_zero_tolerance',j)
                low=q(r['accepted'][2*j]);high=q(r['accepted'][2*j+1])
                check(low<=actual<=high and low<=real<=high,name,'outward_certificate_encloses_exact_actual_and_affine',j)
                check(high<=limit,name,'accepted_upper_within_limit',j)
            for j,(a,b,t,exact)in enumerate(zip(d['reserve'],d['request'],r['tau'],real_line)):
                error=abs(q(t)-exact);bound=F(8)*q(sys.float_info.epsilon)*q(max(1.,abs(a),abs(b)))
                maxline=max(maxline,float(error));check(error<=bound,name,'affine_representation_budget',j)
            check(ref['reserve_feasible'],name,'reserve_exact_feasible')
            if ref['reserve_feasible']:
                lo=F(ref['s_lo']);hi=F(ref['s_hi']);gap=max(F(0),lo-q(r['s']));maxgap=max(maxgap,float(gap))
                check(q(r['s'])<=hi,name,'parameter_not_above_exact_oracle')
                result.update(reference_s=float(lo),s_gap=float(gap))
                if ref['well_conditioned']:
                    well+=1;check(abs(q(r['s'])-(lo+hi)/2)<=q(budget['well_conditioned_s_absolute_error_maximum']),name,'well_conditioned_s_gap_budget')
            if r['s']==1.:
                full+=1
                for j,(actual,requested)in enumerate(zip(r['tau'],d['request'])):check(bits(actual)==bits(requested),name,'full_request_bit_exact',j)
        else:
            invalid.append(r);check(status in (1,2),name,'fixture_expected_invalid_status')
            check(r['s']==0. and all(x==0. for x in r['tau'])and all(x==0. for x in r['accepted']),name,'invalid_zero_request')
            if status==1:check(not feasible(d['reserve'],d),name,'reserve_infeasible_not_a_false_proof')
            if status==2:check(r['proven_mask']==0 and r['not_certified_mask']!=0,name,'reserve_uncertified_not_reported_proven')
        if r['reserve_evaluated']:
            exact=metrics(d['reserve'],d)
            for j,m in enumerate(exact):check(q(r['reserve_diagnostic'][2*j])<=m<=q(r['reserve_diagnostic'][2*j+1]),name,'reserve_diagnostic_enclosure',j)
        comparisons.append(result)
    native=(HERE/f'native_run_{attempt:02d}.log').read_text();m=re.search(r'PA1_NATIVE checks=(\d+) failures=(\d+)',native);assert m
    clock=list(csv.DictReader((HERE/f'NATIVE_CLOCK_CASES_{attempt:02d}.csv').open(newline='')));assert len(clock)==36
    for row in clock:
        check(int(row['status'])==(3 if row['mode']=='1'else 4)and row['valid']=='0'and row['logical_clock_only']=='1','native_clock','all_36_insertion_statuses')
    cpp=HERE/f'cpp_run_{attempt:02d}.log'
    summary=dict(kind='SAVED_NATIVE_OUTPUT_EXACT_REFERENCE_COMPARISON',attempt=attempt,numerical_checks=checks,numerical_failures=len(errors),errors=errors,cases=len(rows),valid_cases=validn,statuses=statuses,well_conditioned_valid_cases=well,maximum_s_gap_all_valid=maxgap,maximum_affine_representation_error_Nm=maxline,full_s1_cases=full,independent_actual_input_components=len(rows)*111,exact_constraint_violation_tolerance=0,native_checks=int(m[1]),native_failures=int(m[2]),clock_insertion_rows=len(clock),CPP_executed=cpp.exists(),CPP_pass=cpp.exists()and'actual_extern_C=PASS'in cpp.read_text(),build_success=build['success'],budget_SHA=sha(HERE/'NUMERICAL_BUDGET.json'),source_SHA=build['sources']['pa1_allocator.c'],raw_SHA=sha(HERE/f'C_RUNS_{attempt:02d}.jsonl'),case_SHA=sha(HERE/'CASES.json'),reference_SHA=sha(HERE/'REFERENCE.json'),physics_steps=0)
    with(HERE/f'COMPARISON_{attempt:02d}.json').open('x',encoding='utf-8')as f:json.dump(summary,f,indent=2,allow_nan=False)
    with(HERE/f'ALL_INVALID_{attempt:02d}.json').open('x',encoding='utf-8')as f:json.dump(invalid,f,indent=2,allow_nan=False)
    with(HERE/f'RUN_COMPARISON_{attempt:02d}.csv').open('x',newline='',encoding='utf-8')as f:
        writer=csv.DictWriter(f,fieldnames=list(comparisons[0]));writer.writeheader();writer.writerows(comparisons)
    print(json.dumps({k:v for k,v in summary.items()if k not in ('errors',)},indent=2));print(json.dumps(errors[:8],indent=2))
    if errors or int(m[2]):raise SystemExit(1)
if __name__=='__main__':main()
