"""Verify this live child's published full checkpoint on CPU, without learning/CUDA/ledger mutation."""
from pathlib import Path
import sys,os,json,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
    assert not (R/'OWN_CPU_VERIFIED.json').exists();secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        code="""from pathlib import Path
import sys,torch,json,time,hashlib
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1);import supervise_e1_G2_matched_continuation as m
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(D/'reports/E1_STATE.json');assert state['phase']=='bounded_E1_G2_retention_repair_learning';pid=state['child']['pid'];runs=[r for r in (D/'learning_logs').glob('*') if (r/'latest_complete.json').exists()];assert len(runs)==1
run=runs[0];rec=read(run/'latest_complete.json');assert rec['pid']==pid;path=Path(rec['checkpoint']);info=m.fullsave(path);assert info['finite_tensors']==96
f=read(D/'reports/SOURCE_FREEZE.json')['sha256'];mf=read(run/'run_manifest.json');rolling=read(run/'rolling_source_freeze.json');assert len(f)==330 and rolling['sha256']==mf['source_map']==f
for n,h in f.items():assert H(D/n)==H(run/'e1_source_snapshot'/n)==h,n
for n,h in mf['src_sha256'].items():assert H(run/'src_snapshot'/n)==h,n
assert mf['init_checkpoint_sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b'
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-OWN-CPU-01',checkpoint=info,bytes=path.stat().st_size,own_PID_bound_receipt=rec,source_count=len(f),snapshot_count=len(mf['src_sha256']),own_rollingfreeze_snapshot_source_SHA_exact=True,source32058_actual_match=True,CPU_only_no_CUDA_initialized=True,no_new_learning_or_canonical_write=True,activity_save_not_formal_final_or_graduation=True)))
""".replace('ROOT',repr(ROOT))
        _,o,e=c.exec_command(PY+' -c '+shlex.quote(code),timeout=120);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');v=json.loads(b);(R/'OWN_CPU_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/'OWN_CPU_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-OWN-CPU-01',error=traceback.format_exc(),no_training_runtime_or_ledger_mutation=True),indent=2),encoding='utf8');raise
