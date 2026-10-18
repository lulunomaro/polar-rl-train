"""Read-only download of the current trainer's complete checkpoint; no GPU or ledger writes."""
from pathlib import Path
import hashlib, json, shlex, sys, time
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / 'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect

REMOTE_CODE = r'''
from pathlib import Path
import json, hashlib, os, time, torch
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(pid):
    p=Path('/proc')/str(pid)
    if not p.exists():return None
    raw=(p/'stat').read_text().split(') ',1)[1].split()
    return dict(pid=pid,start_ticks=int(raw[19]),state=raw[0],cwd=os.readlink(p/'cwd'),argv=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
st=read(D/'reports/D5_STATE.json');child=identity(st['child']['pid']) if st.get('child') else None
runs=[]
if child and child['state']!='Z' and child['start_ticks']==st['child']['start_ticks']:
    for run in (D/'learning_logs').iterdir():
        if (run/'latest_complete.json').exists() and read(run/'latest_complete.json')['pid']==child['pid']:runs.append(run)
    assert len(runs)==1, 'Active trainer must have one own complete receipt'
    run=runs[0];role='active_periodic_complete_not_behavior_reviewed'
else:
    blocks=[read(D/'reports'/('d5_stable_block'+str(n)+'_PASSED.json')) for n in (1,2,3) if (D/'reports'/('d5_stable_block'+str(n)+'_PASSED.json')).exists()]
    assert blocks, 'No current own checkpoint or completed block'
    run=Path(blocks[-1]['run']);role='last_completed_D5_block'
rec=read(run/'latest_complete.json');manifest=read(run/'run_manifest.json');freeze=read(D/'reports/SOURCE_FREEZE.json')
assert manifest['source_map']==freeze['sha256']==read(run/'rolling_source_freeze.json')['sha256']
for name,digest in manifest['src_sha256'].items():assert sha(run/'src_snapshot'/name)==digest, name
ck=Path(rec['checkpoint']);cksha=sha(ck)
obj=torch.load(ck,map_location='cpu',weights_only=False)
state=obj['actor_state_dict']
assert tuple(state['mlp.0.weight'].shape)==(256,35)
assert tuple(state['mlp.6.weight'].shape)==(6,64)
assert 'optimizer_state_dict' in obj
def count(v):
    if torch.is_tensor(v):
        assert not v.is_floating_point() or torch.isfinite(v).all(), 'Nonfinite saved tensor'
        return int(v.is_floating_point())
    if isinstance(v,dict):return sum(count(x) for x in v.values())
    if isinstance(v,(list,tuple)):return sum(count(x) for x in v)
    return 0
finite=count(obj)
assert sha(ck)==cksha
v=dict(epoch=time.time(),root=str(D),role=role,phase=st['phase'],actual_child=child,run=str(run),checkpoint=str(ck),checkpoint_sha256=cksha,checkpoint_bytes=ck.stat().st_size,latest=rec,manifest=manifest,snapshot_count=len(manifest['src_sha256']),floating_tensors_finite=finite,checkpoint_keys=list(obj),actor_keys=list(state),no_training_interruption=True,no_GPU_or_budget_write=True)
print(json.dumps(v))
'''

def main():
    BASE.mkdir(exist_ok=True)
    c=connect()
    try:
        _,out,err=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(REMOTE_CODE),timeout=90)
        raw=out.read();error=err.read();code=out.channel.recv_exit_status()
        assert code==0,(raw+error).decode(errors='replace')
        v=json.loads(raw);s=c.open_sftp();files={}
        def get(remote,name):
            target=BASE/name;target.parent.mkdir(parents=True,exist_ok=True)
            s.get(remote,str(target));files[name]=hashlib.sha256(target.read_bytes()).hexdigest()
            return target
        ck=get(v['checkpoint'],Path(v['checkpoint']).name)
        assert files[ck.name]==v['checkpoint_sha256']
        for name in ('run_manifest.json','latest_complete.json','rolling_source_freeze.json'):
            get(v['run']+'/'+name,name.replace('.json','.remote.json'))
        for name in v['manifest']['src_sha256']:
            get(v['run']+'/src_snapshot/'+name,'src_snapshot/'+name)
            assert files['src_snapshot/'+name]==v['manifest']['src_sha256'][name]
        get(v['root']+'/reports/SOURCE_FREEZE.json','SOURCE_FREEZE.remote.json')
        get(v['root']+'/train/deploy/contract_rm2025_later.json','contract_rm2025_later.json')
        # Keep remote receipt data private to this local delivery. Credentials are never serialized.
        v['local_checkpoint']=str(ck);v['files']=files
        (BASE/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
        print(json.dumps({k:v[k] for k in ('checkpoint','checkpoint_sha256','checkpoint_bytes','role','phase','actual_child','snapshot_count','floating_tensors_finite','local_checkpoint')},ensure_ascii=False))
    finally:c.close()
if __name__=='__main__':main()
