"""Read completed paired qualification and rate8 rejection, without simulations."""
import hashlib,json,shlex,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
C='/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004';P='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
code=r'''import json,sys,time
from pathlib import Path
C=Path('/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004');P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');sys.path.insert(0,str(C));import supervise_scut_style_continue_v2 as v
v.repair.verify();s=v.read(C/'reports/SCUT_STYLE_V2_STATE.json');a=v.read(v.ctl.STATE_PATH);b=v.base.budget_state()
assert s['phase']=='repair_hold' and not a.get('active_training') and not b['active_segment'] and not v.base.trainers()
ck=v.base.checkpoint(Path(s['last_paired_mature']['checkpoint']))
print(json.dumps(dict(epoch=time.time(),checkpoint=ck,state=s,autonomy_state=a,source_count=len(v.read(C/'reports/SOURCE_FREEZE.json')['sha256']),source_hashes_match=True,read_only=True)))'''
c=connect();sf=c.open_sftp();dest=D/'completed_outcomes';dest.mkdir(exist_ok=True)
try:
    with sf.open(B,'rb') as f:before=f.read()
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
    raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err+raw;x=json.loads(raw)
    files={}
    for root in [C+'/reports',P+'/reports']:
        for name in sf.listdir(root):
            wanted=(name.startswith(('auto_0072_','auto_0073_','auto_0074_')) and name.endswith('.json')) or name in ['SCUT_STYLE_V2_STATE.json','SCUT_STYLE_V2_RATE6_MATURE_ACCEPTED.json']
            if not wanted:continue
            with sf.open(root+'/'+name,'rb') as f:data=f.read()
            (dest/name).write_bytes(data);files[name]=dict(remote=root+'/'+name,sha256=hashlib.sha256(data).hexdigest())
    with sf.open(B,'rb') as f:after=f.read()
    assert before==after,'Unexpected active ledger change during planned hold'
    x.update(files=files,whole_frozen_ledger_bytes_exact=True,budget=json.loads(after))
    (D/'COMPLETED_V2_OUTCOMES.json').write_text(json.dumps(x,indent=2),encoding='utf8')
    print(json.dumps(dict(phase=x['state']['phase'],checkpoint=x['checkpoint'],rate_rejected=x['autonomy_state']['rate_rejected'],files=list(files),source_count=x['source_count'],whole_frozen_ledger_bytes_exact=True),ensure_ascii=False))
finally:sf.close();c.close()
