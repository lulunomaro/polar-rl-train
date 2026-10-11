"""Resolve actual predecessor module schema and complete still-missing admission."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'stage_entry_and_target_cpu_once.py').read_text()
s=s.replace("assert not (R/'STAGE_STARTED.json').exists();save('STAGE_STARTED.json',dict(epoch=time.time(),new_entry_axis_only=True,no_old_once_replay=True))","assert (R/'STAGE_STARTED.json').exists() and not (R/'SOURCE_FREEZE.json').exists()")
s=s.replace("jobs=json.loads((PRIOR/'reports/WAVE50_FOUR_CASE_TEMPLATES.json').read_bytes())['jobs']",'jobs=None')
s=s.replace(",(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/results')",'')
s=s.replace('  checks=[]',"  with n.open_sftp() as fs:\n   with fs.open(BASE+'/reports/WAVE50_FOUR_CASE_TEMPLATES.json','rb') as src:jobs=json.loads(src.read())['jobs']\n  checks=[]",1)
s=s.replace(";save('CANDIDATE_JOB_UNUSED_ACTUAL.json',unused)","\n  existing=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes());assert existing['number']==number\n  unused=existing")
s=s.replace('previous.m.','previous.prior.')
exec(compile(s,'<verified-predecessor-missing-stage>','exec'),{'__file__':str(D/'stage_entry_and_target_cpu_once.py'),'__name__':'__main__'})
