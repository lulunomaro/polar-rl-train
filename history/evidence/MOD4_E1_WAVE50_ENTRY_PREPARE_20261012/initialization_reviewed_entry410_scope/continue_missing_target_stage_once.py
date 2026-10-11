"""Only continue unexecuted remote stage; templates exist on the actual target."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'stage_entry_and_target_cpu_once.py').read_text()
a="assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),new_entry_axis_only=True,no_old_once_replay=True))"
assert s.count(a)==1
s=s.replace(a,"assert (R/'STAGE_STARTED.json').exists() and not (R/'SOURCE_FREEZE.json').exists()")
a="jobs=json.loads((PRIOR/'reports/WAVE50_FOUR_CASE_TEMPLATES.json').read_bytes())['jobs']"
assert s.count(a)==1;s=s.replace(a,'jobs=None')
s=s.replace('  checks=[]',"  with n.open_sftp() as fs:\n   with fs.open(BASE+'/reports/WAVE50_FOUR_CASE_TEMPLATES.json','rb') as src:jobs=json.loads(src.read())['jobs']\n  checks=[]",1)
exec(compile(s,'<continue-unexecuted-remote-stage>','exec'),{'__file__':str(D/'stage_entry_and_target_cpu_once.py'),'__name__':'__main__'})
