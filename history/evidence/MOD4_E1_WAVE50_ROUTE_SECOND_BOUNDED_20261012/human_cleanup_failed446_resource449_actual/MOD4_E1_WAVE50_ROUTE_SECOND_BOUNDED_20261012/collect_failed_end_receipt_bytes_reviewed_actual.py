from route_second_io import *

def main():
    n,w=io.connect_both()
    try:
        with n.open_sftp() as f:
            path=ROOT+'/reports/HUMAN_AUTHORIZED_FAILED_STARTUP_END_ACTUAL.json'
            raw=f.open(path,'rb').read()
            local=D/'restore_diagnosis_sources/HUMAN_END_ORIGINAL_PARTIAL_RECEIPT.json'
            assert not local.exists();local.write_bytes(raw)
        v=run(n,r'''import json,time,hashlib,os,fcntl
from pathlib import Path
def ident(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 s=(p/'stat').read_text();f=s[s.rfind(')')+2:].split();return dict(pid=pid,state=f[0],ppid=int(f[1]),start_ticks=int(f[19]),argv=(p/'cmdline').read_bytes().replace(bytes([0]),b' ').decode())
ROOT=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012');B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
raw=(ROOT/'reports/HUMAN_AUTHORIZED_FAILED_STARTUP_END_ACTUAL.json').read_bytes();child=ident(3340979);parent=ident(3340858);guardian=ident(3340947)
assert not child or child['start_ticks']!=94499270 or child['state']=='Z'
b=json.loads(B.read_bytes());locks=[]
for path in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:free=False
 locks.append(dict(path=str(path),actual_fcntl_free=free))
v=dict(epoch=time.time(),passed=True,original_receipt_partial_byte_SHA=hashlib.sha256(raw).hexdigest(),original_receipt_bytes=len(raw),original_partial_receipt_preserved=True,receipt_JSON_serialization_error_after_signal_not_control_or_PPO_fault=True,child=child,parent=parent,guardian=guardian,failed_child_ended=True,source_checkpoint_unchanged=True,no_more_signals_sent=True,no_budget_write=True,active_segment=b['active_segment'],completed_own_segments=[x for x in b['completed_segments'] if x['pid']==3340979],two_locks=locks,remaining=b['remaining_training_seconds'])
p=ROOT/'reports/HUMAN_FAILED_END_BYTE_REVIEWED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
''')
        save('FAILED_END_BYTE_REVIEWED_ACTUAL.json',v);print(json.dumps(v))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('END_RECEIPT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_new_signal_no_blind_replay=True));raise
