import json,os,shlex,sys
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
STAGE='/home/egde/rl_candidates/MOD4_BUDGET_ADD20H_20261004_4TH';C='/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
c=connect();s=c.open_sftp()
try:
    if '--retry-cpu1' in sys.argv:
        assert not (D/'LAUNCHED.json').exists()
        for name in ['PROGRESS.json','LAUNCHED.json']:
            try:s.stat(STAGE+'/'+name)
            except FileNotFoundError:pass
            else:raise AssertionError('Transaction already began; inspect instead')
    else:s.mkdir(STAGE)
    for name in ['PREPARED.json','supervise_rolling_repair_budget_dynamic.py','supervise_rate7_budget90_continue.py','apply_fourth20h.py']:
        s.put(str(D/name),STAGE+'/'+name)
    test=r'''import json,sys,ast,copy
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_BUDGET_ADD20H_20261004_4TH');C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004')
sys.path.insert(0,str(D));import apply_fourth20h as m
before=m.CANONICAL.read_bytes();prep=m.read(D/'PREPARED.json');m.verify_prepared(prep)
b=m.read(m.CANONICAL);assert m.validate_budget(b)==252000
new=copy.deepcopy(b);new['budget_extensions'].append(dict(extension_id=m.ID,additional_training_seconds=72000,state='applied',authorization_basis='explicit_user_request'));new['authorized_training_seconds']=324000
assert m.validate_budget(new)==324000
for kind in range(6):
    x=copy.deepcopy(new)
    if kind==0:x['budget_extensions'].append(copy.deepcopy(x['budget_extensions'][-1]))
    elif kind==1:x['authorized_training_seconds']=396000
    elif kind==2:x['charged_training_seconds']=-1
    elif kind==3:x['budget_extensions'][-1]['state']='pending'
    elif kind==4:x['budget_extensions'][-1]['authorization_basis']='automatic'
    elif kind==5:x['budget_extensions'][-1]['additional_training_seconds']=-72000
    try:m.validate_budget(x)
    except AssertionError:pass
    else:raise AssertionError(kind)
assert before==m.CANONICAL.read_bytes()
result=dict(pass_=True,contracts=prep['CPU'],target_loop_AST_equal=True,only_verify_AST_changed=True,whole_ledger_bytes_exact=True)
m.atomic(D/'CPU_TARGET.json',result);print(json.dumps(result))'''
    _,o,e=c.exec_command(PY+' -c '+shlex.quote(test),timeout=40)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
    (D/'CPU_TARGET.json').write_text(raw,encoding='utf8');print(raw.strip())
    launch=r'''import json,sys,subprocess
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_BUDGET_ADD20H_20261004_4TH');sys.path.insert(0,str(D));import apply_fourth20h as m
assert m.read(D/'CPU_TARGET.json')['pass_'] and not m.PROGRESS.exists() and not m.APPLIED.exists() and not (D/'LAUNCHED.json').exists()
secret=sys.stdin.readline().rstrip(chr(10))
with (D/'worker.log').open('x') as log:
    p=subprocess.Popen([m.PY,str(D/'apply_fourth20h.py')],cwd=m.ROOT,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,text=True)
p.stdin.write(secret+chr(10));p.stdin.close();secret=None
receipt=dict(worker=m.identity(p.pid),extension_id=m.ID);m.atomic(D/'LAUNCHED.json',receipt);print(json.dumps(receipt))'''
    # Correct real newline characters; keep the credential transient in stdin.

    i,o,e=c.exec_command(PY+' -c '+shlex.quote(launch),timeout=40)
    i.write(os.environ['RM_SSH_PASSWORD']+chr(10));i.flush();i.channel.shutdown_write()
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw
    (D/'LAUNCHED.json').write_text(raw,encoding='utf8');print(raw.strip())
finally:s.close();c.close()
