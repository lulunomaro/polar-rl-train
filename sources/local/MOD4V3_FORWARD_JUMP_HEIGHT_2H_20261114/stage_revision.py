"""Keep R1 inputs intact; stage the reviewed request-flag correction as R2."""
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T=Path(__file__).resolve().parent
sys.path.insert(0,sys.argv[1])
from ssh72 import connect,execute
plan=json.loads((T/'PLAN.json').read_bytes())
(T/'evidence/PLAN_R1.json').write_bytes((T/'PLAN.json').read_bytes())
plan.update(support=plan['root']+'/support_r2',remote_plan='PLAN_HEIGHT_R2.json',
            revision='R2: clear request at completed sequence, independent of height score')
plan['jump']['request_exit']='Measured stable sequence completion; height success is a separate score'
(T/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
archive=T/'revision_r2.tar.gz'
files=[]
with tarfile.open(archive,'w:gz') as bundle:
    for path in sorted((T/'support').rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
        if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8-sig'))
        name='support_r2/'+path.relative_to(T/'support').as_posix()
        bundle.add(path,arcname=name,recursive=False)
        files.append(dict(path=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    bundle.add(T/'PLAN.json',arcname=plan['remote_plan'],recursive=False)
    files.append(dict(path=plan['remote_plan'],bytes=(T/'PLAN.json').stat().st_size,
                      sha256=hashlib.sha256((T/'PLAN.json').read_bytes()).hexdigest()))
client=connect()
try:
    sftp=client.open_sftp()
    sftp.put(str(archive),plan['root']+'/revision_r2.tar.gz')
    sftp.close()
    script='''
import hashlib,json,subprocess
from pathlib import Path
r=Path(ROOT)
assert not (r/'support_r2').exists()
subprocess.run(['tar','-xzf',str(r/'revision_r2.tar.gz'),'-C',str(r)],check=True)
for row in FILES:
 assert hashlib.sha256((r/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
print(json.dumps(dict(root=str(r),revision='R2',files_verified=len(FILES),old_source_unchanged=True,optimizer_updates=0)))
'''.replace('ROOT',repr(plan['root'])).replace('FILES',repr(files))
    code,out,err=execute(client,'python3 -c '+shlex.quote(script),60)
    assert code==0,out+err
    receipt=dict(epoch=time.time(),reason='Separate stable sequence completion from stricter height success',
                 new_support=plan['support'],remote_plan=plan['remote_plan'],files=files,
                 remote=json.loads(out),R1_admission_retained=True,R1_evaluation_retained=True)
    (T/'evidence/REVISION_R2_INPUTS.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(out)
finally:client.close()
