import copy
from continuation_contract import validate
source=dict(path='/exact/19078.pt',sha256='frozen-source',finite_tensors=68)
mature=dict(checkpoint='/paired/17196.pt',cap=5.,profile='white_v2')
rows=[dict(case=f'{name}_{seed}_{profile}',seed=seed,profile=profile,contact_gate=True) for name in ('latest6','mature5') for seed in (20261002,20261003) for profile in ('nominal','white_v2')]+[dict(case='passed6_20261002_white_v2',seed=20261002,profile='white_v2',contact_gate=True)]
e=dict(eligible_for_versioned_gate_review=True,ledger_bytes_exact=True,complete_15s_two_seed_profile_pairs=True,hook_and_original_behavior_exact=True,prospective_gate_version='test-v1',gate_source_sha256='gate-source',rows=rows,source_selection=dict(latest6=source,mature5=dict(path=mature['checkpoint'])))
f=dict(all_original_flat_pass=True,initial_root_q_pair_exact=True,ledger_bytes_exact=True,results={str(i):dict(pass_=True,actual_parameters_pass=True) for i in range(4)},source=source)
assert validate(e,f,source,mature,'test-v1','gate-source')
def rejects(ev=e,fl=f,src=source,mat=mature,version='test-v1',sha='gate-source'):
 try:validate(ev,fl,src,mat,version,sha)
 except AssertionError:return
 raise AssertionError('Invalid admission was accepted')
rejects(src=dict(source,path='/other/global-highest.pt'))
rejects(sha='changed-after-review')
x=copy.deepcopy(e);x['rows'][0]['profile']='white_v3';rejects(ev=x)
x=copy.deepcopy(f);x['initial_root_q_pair_exact']=False;rejects(fl=x)
x=copy.deepcopy(e);x['hook_and_original_behavior_exact']=False;rejects(ev=x)
x=copy.deepcopy(f);x['results']['0']['actual_parameters_pass']=False;rejects(fl=x)
x=copy.deepcopy(e);x['rows'][0]['contact_gate']=False;rejects(ev=x)
print('Eight continuation evidence checks passed: valid source, wrong checkpoint, changed gate, missing condition, pairing, hook equivalence, readback and individual gate rejection.')
