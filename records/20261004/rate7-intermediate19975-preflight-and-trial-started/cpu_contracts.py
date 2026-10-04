"""Admission and progression contracts for the explicit intermediate transition."""
import copy,math
from transition7_policy import validate_context,validate_limit,next_limit,progress

def run(context):
    rows=[]
    def check(name,ok):
        assert ok,name;rows.append(name)
    check('fixed actual mature context admitted',validate_context(context))
    changes=[('phase','training'),('current_cap',8.),('active_training',{'pid':1}),
             ('active_segment',{'pid':1}),('live_children',[1]),('chosen_checkpoint','other'),
             ('source_hashes_match',False),('acceptance_routes_verified',False),('only_rate_changes',False)]
    nested=[('checkpoint','sha256','wrong'),('checkpoint','iteration_stored',19976),
            ('checkpoint','finite_tensors',67),('mature','cap',5.),('mature','profile','white_v3'),
            ('accepted6','cap',5.),('accepted6','acceptance_version','old'),
            ('accepted6','fresh_latest_policy_flat_spin_and_two_seed_nominal_DR_pair',False),
            ('budget','authorized',324000),('budget','charged',-1),('budget','remaining',3600),
            ('old8_rejected','source','wrong'),('old8_rejected','cap',7.),
            ('old8_rejected','physical_smoke_pass',True),('old8_rejected','ppo_performed',True)]
    for key,value in changes:
        x=copy.deepcopy(context);x[key]=value
        try:validate_context(x)
        except (AssertionError,ValueError):check('reject '+key,True)
        else:raise AssertionError('admitted '+key)
    for key,sub,value in nested:
        x=copy.deepcopy(context);x[key][sub]=value
        try:validate_context(x)
        except (AssertionError,ValueError):check('reject '+key+'.'+sub,True)
        else:raise AssertionError('admitted '+key+'.'+sub)
    for bad in (0.,6.5,9.,13.,float('nan'),float('inf')):
        try:validate_limit(bad)
        except ValueError:check('reject unregistered rate '+str(bad),True)
        else:raise AssertionError('admitted rate '+str(bad))
    check('finer6->7->8 and unchanged10->4pi',next_limit(6.)==7. and next_limit(7.)==8. and next_limit(8.)==10. and next_limit(10.)==4*math.pi and next_limit(4*math.pi) is None)
    check('same weight cannot add second success',progress(True,False,1,0)==(1,0))
    check('different passing policy adds success',progress(True,True,1,0)==(2,0))
    check('failure resets success count',progress(False,True,2,0)==(0,1))
    check('three failures trigger bounded fallback count',progress(False,True,0,2)==(0,3))
    check('passing skill clears consecutive failed blocks',progress(True,True,0,2)==(1,0))
    return dict(pass_=True,count=len(rows),contracts=rows)

