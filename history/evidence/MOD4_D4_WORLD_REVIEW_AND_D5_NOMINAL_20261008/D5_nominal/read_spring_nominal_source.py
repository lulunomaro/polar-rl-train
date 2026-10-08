"""Read the actual frozen D4 asset and spring implementation. No GPU or writes to runtime."""
from pathlib import Path
import sys,json,shlex,hashlib,base64
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,zipfile,hashlib,time,base64
D=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
pack=read(D/'reports/D4_FROZEN_BEHAVIOR_PACKAGE.json');assert sha(Path(pack['path']))==pack['sha256']=='74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18'
with zipfile.ZipFile(pack['path']) as z:
    m=json.loads(z.read('SOURCE_MANIFEST.json'))
    assert hashlib.sha256(z.read('assets/robot.usd')).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
    names=[n for n in z.namelist() if n.endswith('import_contract.json')];assert len(names)==1
    raw=z.read(names[0]);assert hashlib.sha256(raw).hexdigest()==m['files'][names[0]]
    contract=json.loads(raw)
    files={}
    for n in ('isaac/mod4/mod4_task.py','isaac/mod4/skills_isaac.py','isaac/mod4/mild_dr.py'):
        p=D/n;assert sha(p)==read(D/'reports/SOURCE_FREEZE.json')['sha256'][n]
        files[n]=dict(sha256=sha(p),raw_b64=base64.b64encode(p.read_bytes()).decode())
print(json.dumps(dict(epoch=time.time(),read_only=True,package=pack,actual_USD_sha256='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87',contract_path=names[0],contract_sha256=hashlib.sha256(raw).hexdigest(),contract=contract,files=files,approval=a,tracks=read(E/'reports/EXECUTION_TRACKS.json'),current=read(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json'),work_order=read(E/'reports/NEXT_D5_FORCE_STROKE_WORK_ORDER.json'))))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw)
    src=D/'reviewed_sources';src.mkdir(exist_ok=True)
    for n,row in v.pop('files').items():
        p=src/Path(n).name;p.write_bytes(base64.b64decode(row['raw_b64']))
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    for key in ('approval','tracks','current','work_order'):
        (R/('ACTUAL_'+key.upper()+'.json')).write_text(json.dumps(v.pop(key),ensure_ascii=False,indent=2),encoding='utf8')
    (R/'ACTUAL_FROZEN_SPRING_SOURCE.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],package=v['package'],contract_sha256=v['contract_sha256'],gas_springs=v['contract']['gas_springs'],gas_joints={n:v['contract']['joints'][n] for n in v['contract']['gas_springs']},no_GPU_or_budget_write=True)))
finally:c.close()
