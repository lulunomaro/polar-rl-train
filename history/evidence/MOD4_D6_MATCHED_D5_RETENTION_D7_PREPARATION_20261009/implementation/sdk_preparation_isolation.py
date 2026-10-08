"""Only short, immutable D7 preparation SDK failures can be held per job."""
PREFIX='clk2500-closure-episode-d3-'
def can_hold_preparation(job,manifest,result):
    return (isinstance(job,str) and any(job.startswith(PREFIX+label+'-d7-') for label in ('90','91','92'))
            and isinstance(manifest,dict) and isinstance(result,dict)
            and manifest.get('job_id')==job and result.get('job_id')==job
            and manifest.get('num_envs')==10 and manifest.get('steps')==300
            and manifest.get('no_learning') is True and manifest.get('canonical_write_authority') is False
            and result.get('phase')=='retained_failed' and result.get('new_learning') is False
            and bool(result.get('errors') or result.get('error_files')))
def tests():
    import copy
    job=PREFIX+'90-d7-chassis-pd-frame-sdk'
    m=dict(job_id=job,num_envs=10,steps=300,no_learning=True,canonical_write_authority=False)
    r=dict(job_id=job,phase='retained_failed',new_learning=False,errors=['actual error'])
    assert can_hold_preparation(job,m,r)
    changes=[('manifest','num_envs',88),('manifest','steps',1500),('manifest','no_learning',False),
             ('manifest','canonical_write_authority',True),('result','phase','complete'),('result','new_learning',True)]
    for where,key,value in changes:
        a,b=copy.deepcopy(m),copy.deepcopy(r);(a if where=='manifest' else b)[key]=value
        assert not can_hold_preparation(job,a,b)
    assert not can_hold_preparation(PREFIX+'86-d6-gas-b1-world',m,r)
    assert not can_hold_preparation(job,None,r)
    return dict(CPU_cases=9,short_preparation_failure_held_without_pass=True,normal_skill_or_learning_failures_not_exempted=True)
if __name__=='__main__':
    import json
    print(json.dumps(tests()))
