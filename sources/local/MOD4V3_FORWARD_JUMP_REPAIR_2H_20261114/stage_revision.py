"""Retain rejected 40ms teacher evidence and stage the original 80ms ramp."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import shlex
T=Path(__file__).resolve().parent
sys.path.insert(0,sys.argv[1])
from ssh72 import connect,execute
plan=json.loads((T/'PLAN.json').read_bytes())
(T/'evidence/PLAN_ADMISSION_R1.json').write_text(json.dumps(plan,indent=2)+'\n')
result=json.loads((T/'evidence/teacher_demos/RESULT.json').read_bytes())
nominal=[e for e in result['episodes'] if e['nominal']]
report=dict(trial='admission_teacher_40ms',optimizer_updates=0,nominal_tuck=sum(e['retracted'] for e in nominal),
    nominal_complete=sum(e['success'] and not e['terminated'] for e in nominal),nominal_requested=len(nominal),
    rejected_as_final_teacher=True,reason='Faster teacher ramp introduced pitch excess in14nominal cases; restore original80ms',
    reader_error='finalize_admission initially required all51teacher successes, an unnecessary launch-only condition. Runtime and fixed evaluation criteria remain unchanged.')
(T/'evidence/TEACHER_R1_REPAIR.json').write_text(json.dumps(report,indent=2)+'\n')
plan['jump']['teacher_tuck_ramp_s']=.08
plan['jump_bc']['dataset']=plan['root']+'/teacher_demos_r2/successful_demos.pt'
plan['jump_bc']['dataset_sha256']='pending_native_demonstration_collection'
plan['revision']='Measured tuck precedes landing extension; original80ms teacher ramp'
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
with tarfile.open(T/'revision_inputs.tar.gz','w:gz') as bundle:
    bundle.add(T/'support',arcname='support');bundle.add(T/'PLAN.json',arcname='PLAN.json')
files=[dict(path=str(p.relative_to(T)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (T/'support').rglob('*.py')]
(T/'evidence/REVISION_INPUTS.json').write_text(json.dumps(dict(files=files,optimizer_updates=0),indent=2)+'\n')
c=connect()
try:
    s=c.open_sftp();s.put(str(T/'revision_inputs.tar.gz'),plan['root']+'/revision_inputs.tar.gz');s.close()
    command='cd '+shlex.quote(plan['root'])+' && cp -a support source_admission_r1 && cp PLAN.json PLAN_ADMISSION_R1.json && tar -xzf revision_inputs.tar.gz'
    status,out,err=execute(c,command,30);assert status==0,out+err
finally:c.close()
print(json.dumps(report))
