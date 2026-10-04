import argparse,ast,copy,hashlib,json,math,sys
from pathlib import Path
D=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--gate-dir',required=True);p.add_argument('--reports',required=True);a=p.parse_args()
    sys.path.insert(0,a.gate_dir)
    from scut_curriculum_gate_v4 import VERSION,assess,assess_flat,evidence,target_evidence
    from scut_fine_rate_policy import LEVELS,validate_limit,next_limit
    checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    def load(name):return json.loads((Path(a.reports)/name).read_text(encoding='utf8'))
    check('10 -> 11 -> 12 -> 4pi only',next_limit(10)==11 and next_limit(11)==12 and next_limit(12)==4*math.pi and next_limit(4*math.pi) is None)
    check('no higher target or rate jump registered',max(LEVELS)==4*math.pi and all(b-a<=1.00000001 for a,b in zip(LEVELS[6:],LEVELS[7:])))
    for bad in (float('nan'),float('inf'),0,10.5,13):
        try:validate_limit(bad)
        except ValueError:check('unregistered or nonfinite rate rejects '+str(bad),True)
        else:raise AssertionError('accepted '+str(bad))
    old=ast.parse((D/'before/supervise_scut_curriculum_v4.py').read_text(encoding='utf8'))
    new=ast.parse((D/'supervise_scut_fine_rate_continue.py').read_text(encoding='utf8'))
    def fn(tree,name):return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    for name in ('status','phase','freeze_run','gate','decision','pairs','fullscale','hold','finish'):
        check('unchanged v4 function AST '+name,ast.dump(fn(old,name))==ast.dump(fn(new,name)))
    old_pre=copy.deepcopy(fn(old,'preflight'));new_pre=copy.deepcopy(fn(new,'preflight'))
    for node in ast.walk(new_pre):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):node.value=node.value.replace('SCUT_FINE_RATE','SCUT_CURRICULUM_V4')
    check('same actual preflight contract with unique receipt namespace',ast.dump(old_pre)==ast.dump(new_pre))
    while_old=next(n for n in ast.walk(fn(old,'controller')) if isinstance(n,ast.While))
    while_new=next(n for n in ast.walk(fn(new,'controller')) if isinstance(n,ast.While))
    check('unchanged deployed v4 bounded qualification loop AST',ast.dump(while_old)==ast.dump(while_new))
    short=load('auto_0107_scut_v4_short_cap12.5664_white_v2.json');before=copy.deepcopy(short)
    check('actual target task failure still denies entry',not evidence(short,'spin',3)['pass_'] and 'actual_task_termination' in evidence(short,'spin',3)['reasons'])
    check('actual failure report immutable',short==before and sum(short['alive'])==19)
    r=load('auto_0104_scut_v4_paired_regression_cap10_white_v2_spin_white_v2_20261002.json')
    f=load('auto_0104_scut_v4_paired_regression_cap10_white_v2_flat_white_v2_20261002.json')
    check('exact 10 source real spin passes v4',assess(r)['pass_'])
    check('exact 10 source real flat passes v4',assess_flat(f)['pass_'])
    check('old spin booleans remain diagnostic',r['spin_skill_pass'] is False)
    for key in ('spin_translation_speed','left_slip','peak_tilt','maximum_gap_m','yaw_error','wheel_rating_clip'):
        x=copy.deepcopy(r);x['per_environment'][key]=[20.]*len(x['alive'])
        check('finite quality remains diagnostic '+key,assess(x)['pass_'])
    x=copy.deepcopy(r);x['alive'][0]=False
    check('actual task failure rejects',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['max_closure_m']=.003
    check('model integrity rejects',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['per_environment']['left_slip'][0]=float('nan')
    check('nonfinite diagnostics reject',not assess(x)['pass_'])
    x=copy.deepcopy(r);x['substep_contact_readback']['callbacks']=1
    check('incomplete capture rejects',not assess(x)['pass_'])
    check('10 or target registration does not claim 2rps',not target_evidence(r,4*math.pi)['pass_'])
    print(json.dumps(dict(pass_=True,count=len(checks),checks=checks,acceptance_version=VERSION,
        controller_sha256=hashlib.sha256((D/'supervise_scut_fine_rate_continue.py').read_bytes()).hexdigest())))

if __name__=='__main__':main()
