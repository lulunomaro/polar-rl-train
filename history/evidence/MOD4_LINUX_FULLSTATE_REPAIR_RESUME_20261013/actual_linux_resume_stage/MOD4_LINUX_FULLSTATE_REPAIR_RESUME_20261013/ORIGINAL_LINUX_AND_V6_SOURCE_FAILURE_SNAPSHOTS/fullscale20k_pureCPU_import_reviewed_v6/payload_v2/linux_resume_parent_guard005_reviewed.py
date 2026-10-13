"""New parent wrapper validates original applied seven-extension authority."""
import sys,json
import linux_resume_parent as original
original_budget=original.budget
def budget(*args,**kwargs):
    d=json.loads(original.B.read_bytes());records=d['budget_extensions']
    assert len(records)==7 and all(x['state']=='applied' for x in records)
    assert 36000+sum(x['additional_training_seconds'] for x in records)==1188000==d['authorized_training_seconds']
    assert records[-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert records[-1]['authorized_seconds_after']==1188000 and records[-1]['authorized_seconds_before']==828000
    return original_budget(*args,**kwargs)
original.budget=budget
if __name__=='__main__':
    if '--guardian' in sys.argv:original.guardian(int(sys.argv[-1]))
    else:original.main()
