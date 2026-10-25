"""Fresh exact original68 terminal evidence and bounded own-owner read access; no accounting writes."""
from pathlib import Path
import importlib.util, json, os, sys, time, traceback
D = Path(__file__).resolve().parent
T, W = D.parent, D.parent.parent
R = D / 'reports'
R.mkdir(exist_ok=True)
N = T / 'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
Q = T / 'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

E3 = r'''
from pathlib import Path
import hashlib,json,psutil,time
root=Path(v['root']);assert str(root)=='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_reward_sagtuck6a_2510v68/recovery'
identities={}
for label,e in v['identities'].items():
 row=dict(expected=e,exact_identity_alive=False)
 try:
  p=psutil.Process(e['pid'])
  if p.create_time()==e['creation']:
   assert p.cmdline()==e['argv'];row.update(exact_identity_alive=True,exe=p.exe())
 except psutil.Error:pass
 identities[label]=row
texts={}
for rel in ['NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','job0/production/FINAL.json']:
 p=root/rel;raw=p.read_bytes();texts[rel]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode())
terminal=json.loads(texts['NODE_TERMINAL_ACTUAL.json']['text']);ex=json.loads(texts['NODE_EXIT_ACTUAL.json']['text']);f=json.loads(texts['job0/production/FINAL.json']['text'])
assert terminal['row']['terminal_all_own_children_waited'] and terminal['row']['returncode']==0 and ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired'] and f['passed']
assert not any(x['exact_identity_alive'] for x in identities.values())
p=Path(f['final']['path']);st=p.stat();assert st.st_size==f['final']['bytes']
print(json.dumps(dict(epoch=time.time(),texts=texts,identities=identities,final_stat=dict(path=str(p),bytes=st.st_size,inode=st.st_ino,mtime_ns=st.st_mtime_ns),terminal=terminal,exit=ex,no_PT_hash_GPU_or_unknown_peer_read=True)))
'''

H1 = r'''
from pathlib import Path
import errno,hashlib,json,os,psutil,socket,subprocess,time
q=v['q'];owner=Path(q['owner_root']);root=Path(q['roots']['h1']);e=q['owner_identity'];p=psutil.Process(e['pid'])
assert p.create_time()==e['creation'] and p.cmdline()==e['argv'] and p.exe()=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
assert str(owner)=='/mnt/mod4_linux_durable_20261013/H1step270_reward_sagtuck6a_2510v68/owner'
assert str(root)=='/mnt/mod4_linux_durable_20261013/H1step270_reward_sagtuck6a_2510v68/h1'
identities={}
for label,e2 in v['identities'].items():
 row=dict(expected=e2,exact_identity_alive=False)
 try:
  p2=psutil.Process(e2['pid'])
  if p2.create_time()==e2['creation']:
   assert p2.cmdline()==e2['argv'];row.update(exact_identity_alive=True,exe=p2.exe())
 except psutil.Error:pass
 identities[label]=row
assert not any(x['exact_identity_alive'] for x in identities.values())
texts={}
for rel in ['NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','job0/production/FINAL.json']:
 path=root/rel;raw=path.read_bytes();texts[rel]=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode())
terminal=json.loads(texts['NODE_TERMINAL_ACTUAL.json']['text']);ex=json.loads(texts['NODE_EXIT_ACTUAL.json']['text']);f=json.loads(texts['job0/production/FINAL.json']['text'])
assert terminal['row']['terminal_all_own_children_waited'] and terminal['row']['returncode']==0 and ex['actual_all_own_children_waited'] and ex['validation_fcntl_released_if_acquired'] and f['passed']
listeners=[dict(ip=x.laddr.ip,port=x.laddr.port,status=x.status) for x in p.net_connections(kind='tcp') if x.status=='LISTEN']
probe=[]
for host in ['10.24.4.210','127.0.0.1']:
 row=dict(host=host,port=29754)
 try:
  with socket.create_connection((host,29754),timeout=2):row['TCP_connected']=True
 except OSError as err:row.update(TCP_connected=False,error_type=type(err).__name__,errno=err.errno)
 probe.append(row)
mem=dict(pid=p.pid,opened_readonly=False,bytes_read=0)
try:
 fd=os.open('/proc/'+str(p.pid)+'/mem',os.O_RDONLY);os.close(fd);mem['opened_readonly']=True
except OSError as err:mem.update(error_type=type(err).__name__,errno=err.errno)
sudo=None
if not mem['opened_readonly']:
 code="import os,json,psutil; p=psutil.Process("+str(p.pid)+"); assert p.create_time()=="+repr(e['creation'])+" and p.cmdline()=="+repr(e['argv'])+"; fd=os.open('/proc/"+str(p.pid)+"/mem',os.O_RDONLY);os.close(fd);print(json.dumps(dict(opened_readonly=True,bytes_read=0)))"
 try:
  out=subprocess.run(['sudo','-n','--','/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-B','-c',code],capture_output=True,text=True,timeout=8)
  sudo=dict(returncode=out.returncode,stdout=out.stdout,stderr=out.stderr,no_password_or_token_supplied=True)
 except (OSError,subprocess.TimeoutExpired) as err:sudo=dict(error_type=type(err).__name__)
c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']['owner_parent_pid']==p.pid
print(json.dumps(dict(epoch=time.time(),owner_identity=q['owner_identity'],own_children_identities=identities,texts=texts,terminal=terminal,exit=ex,owner_listeners=listeners,owner_endpoint_TCP_only=probe,own_owner_mem_read_access=mem,sudo_noninteractive_own_owner_mem_access=sudo,canonical_remaining_snapshot=c['remaining_training_seconds'],active_segment_snapshot=c['active_segment'],no_token_recovered_or_POST_or_signal_or_canonical_write=True)))
'''

put('EXACT68_OWNER_HANDOFF_CAPABILITIES_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,human='开始训练；上台阶修复和提速一起'))
try:
    q=json.loads((N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    meta=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    path=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'
    spec=importlib.util.spec_from_file_location('memory',path);memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory)
    secret=memory.recover();c=d.connect72(secret);secret=None
    try:e3=d.code(c,d.PY72,E3,dict(root=q['roots']['recovery'],identities={k:meta['source72'][k] for k in ('node','worker')}),timeout=30)
    finally:c.close()
    put('EXACT68_E3_FRESH_TERMINAL_AND_OWN_OUT_ACTUAL.json',e3)
    sys.path.insert(0,str(Q));import strict_user_forwarded_original210_transport_v1 as route
    c=route.connect()
    try:h1=d.code(c,route.PY,H1,dict(q=q,identities={k:meta['source210'][k] for k in ('H1_node','H1_worker')}),timeout=30)
    finally:c.close()
    put('EXACT68_OWNER_HANDOFF_CAPABILITIES_RETURNED_ACTUAL.json',dict(epoch=time.time(),source210=h1,target72=e3,actual_finite_returned=True))
    print(json.dumps(dict(original_owner_identity_verified=True,both_exact_workers_nodes_out=True,owner_listeners=h1['owner_listeners'],owner_endpoint_TCP_only=h1['owner_endpoint_TCP_only'],own_owner_mem_read_access=h1['own_owner_mem_read_access'],sudo_noninteractive_own_owner_mem_access=h1['sudo_noninteractive_own_owner_mem_access'],canonical_remaining_snapshot=h1['canonical_remaining_snapshot'],actual_finite_returned=True)))
except BaseException:
    put('EXACT68_OWNER_HANDOFF_CAPABILITIES_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_canonical_write_or_new_writer=True));raise
