"""Early terminal reader for failed210 only, healthy original72 slots continue."""
from pathlib import Path
import sys,json,time,hashlib,base64,zlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
COST=r'''from pathlib import Path
import json,psutil,hashlib
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);a=c['active_segment'];expected=v['owner'];p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation']
assert p.exe()==expected['exe'] and p.cmdline()==expected['argv'] and p.cwd()==expected['root'] and a['owner_parent_pid']==expected['pid']
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
current=json.loads((Path(v['owner_root'])/'OWNER_CURRENT.json').read_bytes());row=current['rows']['h1_210'];g=current['go']['h1_210'];x=a['experts']['h1_210']
assert row['original_error'] and row['terminal_all_own_children_waited'] and row['final'] is None and row['returncode']==0
assert g['run_id']==v['run_id'] and x['started_epoch']==g['learning_started_epoch'] and x['ended_epoch']==row['owner_received_terminal_epoch'] and x['charged_seconds']>0
print(json.dumps(dict(passed=True,failed_slot_already_originally_settled=True,original_slot=g,original_fee=x,canonical_active_owner=expected,remaining_snapshot=c['remaining_training_seconds'],active_other_slots=[k for k,r in current['rows'].items() if k!='h1_210' and not r.get('terminal_all_own_children_waited')],canonical_SHA_snapshot=hashlib.sha256(raw).hexdigest(),canonical_None_not_required_or_claimed=True,no_account_lock_or_write=True)))'''
OUT=r'''from pathlib import Path
import json,psutil,fcntl,hashlib,zlib,base64
node=Path(v['node']);job=Path(v['job']);term=json.loads((node/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];ex=json.loads((node/'NODE_EXIT_ACTUAL.json').read_bytes())
assert term['original_error'] and term['final'] is None and term['returncode']==0 and term['terminal_all_own_children_waited'] and ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired']
stamp=json.loads((job/'production_STARTED_ACTUAL.json').read_bytes());known=[v['node_identity'],stamp];out=[]
for row in known:
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['creation'],'own process still alive'
 except psutil.NoSuchProcess:pass
 out.append(dict(pid=row['pid'],creation=row['creation'],original_owned_out=True))
with Path(v['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not (job/'job0/production/FINAL.json').exists() and not (job/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').exists()
files=[];total=0
for root in (node,job/'job0/production'):
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink() or p.suffix.lower() not in ('.json','.log','.txt') or p.stat().st_size>8*1024**2:continue
  a=p.stat();raw=p.read_bytes();b=p.stat();assert (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns);raw.decode('utf8');total+=len(raw);assert total<32*1024**2
  files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(raw,1)).decode()))
print(json.dumps(dict(passed=True,own_out=out,failed_slot_private_free=True,original_error_and_no_FINAL_preserved=True,no_new_native_policy=True,files=files,no_model_raw_GPU_or_account_action=True)))'''
def main():
 p=json.loads((R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());a=json.loads((R/'THREE93_ACTUAL_OWNER_AND_THREE_NODES_DETACHED.json').read_bytes());put('THREE93_FAILED210_EARLY_TERMINAL_READER_CONSUMED.json',dict(epoch=time.time(),not_normal_fullFINAL_collector=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('early93_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 try:
  c=d.connect72(secret);cost=d.code(c,d.PY72,COST,dict(owner=a['identities']['owner']['exact_identity'],owner_root=p['owner_root'],run_id=p['run_id']),timeout=40);c.close();c=None;secret=None
  c=route.connect();row=p['experts']['h1_210'];value=d.code(c,route.PY,OUT,dict(node=p['node_roots']['h1_210'],job=row['job_root'],private_lock=row['private_lock'],node_identity=a['identities']['h1_210']['exact_identity']),timeout=60);c.close();c=None
  target=N/'failed210_original_text';target.mkdir();rows=[]
  for item in value.pop('files'):
   raw=zlib.decompress(base64.b64decode(item.pop('zlib_base64')));assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['SHA'];path=target/(hashlib.sha256(item['path'].encode()).hexdigest()[:20]+'_'+Path(item['path']).name)
   with path.open('xb') as f:f.write(raw)
   rows.append(dict(**item,local_path=str(path)))
  put('THREE93_FAILED210_ORIGINAL_FEE_OWNOUT_ALL_TEXT_RETURNED_ACTUAL.json',dict(passed=True,actual_finite_returned=True,cost=cost,ownout=value,full_original_texts=rows,healthy_other_slots_unchanged=True,no_model_GPU_or_accountwrite=True));print(json.dumps(dict(passed=True,failed_original_fee=cost['original_fee']['charged_seconds'],healthy_other_slots=cost['active_other_slots'])))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE93_FAILED210_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_kill_refund_or_secondwriter=True));raise
