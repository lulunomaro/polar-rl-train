"""Finalize an already closed native run; never launch or replay training."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

T=Path(__file__).resolve().parent;R=T.parents[2]
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
closed=json.loads((T/'evidence/train7200/SAFE_CLOSED.json').read_bytes())
assert closed['outcome']=='complete'
assert all(json.loads(p.read_bytes())['outcome']=='complete' for p in (T/'evidence').glob('eval_*/SAFE_CLOSED.json'))
def run(name,args,log):
    p=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=T,capture_output=True,text=True,encoding='utf8')
    (T/'evidence'/log).write_text(p.stdout+p.stderr,encoding='utf8')
    print(p.stdout+p.stderr,flush=True)
    assert p.returncode==0,log
run('summarize_results.py',['--outputs',str(out),'--final'],'summary_final.log')
run('analyze_selected.py',[],'margins_final.log')
run('render_selected.py',['--outputs',str(out)],'render_final.log')
shutil.copy2(out/'checkpoint_results.csv',T/'evidence/checkpoint_results.csv')
summary=json.loads((T/'evidence/RESULTS_SUMMARY.json').read_bytes())
render=json.loads((T/'evidence/RECORDED_POLICY_RENDER.json').read_bytes())
assert render['checkpoint_sha256']==summary['selected']['sha256']
assert render['accepted_complete_case'] and render['teacher_executed'] is False
weights=[]
plan=json.loads((T/'PLAN.json').read_bytes())
expected={'parent_r3_080m.pt':plan['parent_sha256'],'root_five_minute.pt':plan['teacher_sha256']}
for name in ('teacher_demos','teacher_demos_r2'):
    expected[name+'__successful_demos.pt']=json.loads((T/'evidence'/name/'RESULT.json').read_bytes())['dataset_sha256']
receipts=[json.loads(p.read_bytes()) for p in (T/'evidence/train7200').glob('PERIODIC_*M.json')]
for name in ('FIRST_UPDATE.json','FINAL.json'):
    receipts.append(json.loads((T/'evidence/train7200'/name).read_bytes())['checkpoint'])
for receipt in receipts:
    expected['train7200__'+Path(receipt['path']).name]=receipt['sha256']
for p in sorted((T/'weights').glob('*.pt')):
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest==expected[p.name],p.name+' does not match the native full-save receipt'
    weights.append(dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=digest,native_save_SHA_verified=True))
assert {p.name for p in (T/'weights').glob('*.pt')}==set(expected)
(T/'evidence/ARCHIVE_INPUT_CHECK.json').write_text(json.dumps(dict(complete_PT_bodies_required=True,weights=weights),indent=2)+'\n')
print(json.dumps(dict(ready_for_final_Git_archive=True,PT_count=len(weights),summary=summary['selected'],budget=summary['budget']),indent=2))
