"""Independent before-use repair; preserve V1's unused signal path/source/index."""
from pathlib import Path
import hashlib,json,time,traceback

N=Path(__file__).resolve().parent
V1=N.parent/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V1_20261101'


def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,b):
 with p.open('xb') as f:f.write(b)


def main():
 purpose=json.loads((N/'reports/DERIVE_V2_PURPOSE_FROZEN.json').read_bytes())
 for row in purpose['inputs']:assert ref(Path(row['path']))==row
 name='run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py'
 source=(V1/name).read_text(encoding='utf8')
 old='''  except subprocess.TimeoutExpired:
   timed_out=True;child.terminate()
   try:stdout,stderr=child.communicate(timeout=30)
   except subprocess.TimeoutExpired:child.kill();stdout,stderr=child.communicate()'''
 new='''  except subprocess.TimeoutExpired:
   timed_out=True
   put(J/'E2_FROM226_METADATA_TIMEOUT_ORIGINAL_FALSE.json',dict(
    epoch=time.time(),passed=False,purpose_id=a.purpose_id,original_Popen_PID=child.pid,
    declared_timeout_seconds=a.timeout_seconds,actual_waited=False,all_own_children_waited=False,
    original_child_still_requires_communicate_and_wait=True,no_signal_sent=True,
    FREE_or_EX_release_claimed=False,no_automatic_retry=True))
   # Preserve the original child. Continue its original pipe collection/wait;
   # the timeout remains false even if it later returns0. No FREE claim here.
   stdout,stderr=child.communicate()'''
 assert source.count(old)==1
 write(N/name,source.replace(old,new).encode())
 for name in ('contract_e2_from226.py','finalize_e2_from226_actual_evidence_ROOT_ONLY.py'):
  write(N/name,(V1/name).read_bytes())
 put(N/'reports/BEFORE_USE_V2_ORIGINAL_TIMEOUT_SIGNAL_REJECTION_AND_REPAIR.json',dict(
  epoch=time.time(),V1_INDEX=ref(V1/'INDEX_E2_FROM226_FROZEN.json'),V1_executed=False,
  original_before_use_blocker='V1 TimeoutExpired branch called terminate then kill,outside the current no-automatic-signal boundary',
  correction='Timeout writes originalfalse/actual_waited=false/FREE=false,then continues original child communicate/wait with zero signals;final passed remainsfalse for timeout',
  changes_scope='Only runner TimeoutExpired block;contract/finalizer byte-identical;original226 probe and213 ABI/read contracts unchanged',
  V1_source_and_INDEX_overwritten=False,old_probe_or_fixture_replays=0,model_asset_raw_SDK_GPU_network_Git_calls=0))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/DERIVE_V2_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
