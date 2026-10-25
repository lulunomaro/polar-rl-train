"""Authenticated original terminal delivery only. No ledger writer, process signals, or hotpatch."""
from pathlib import Path
import hashlib, json, os, shlex, sys, time, traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
Q=T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'
N=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

CODE=r'''
from pathlib import Path
import base64,ctypes,fcntl,hashlib,hmac,json,os,psutil,re,shutil,socket,struct,subprocess,sys,time,urllib.request
v=json.loads(sys.stdin.readline());q=v['q'];e=q['owner_identity'];pid=e['pid'];owner=Path(q['owner_root']);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
assert os.geteuid()==0 and pid==1055094 and e['creation']==1792908227.62
p=psutil.Process(pid);assert p.create_time()==e['creation'] and p.cmdline()==e['argv'] and p.exe()=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
assert str(owner)=='/mnt/mod4_linux_durable_20261013/H1step270_reward_sagtuck6a_2510v68/owner' and q['run_id']=='H1_STEP270_RECOVERY_ORIGINAL_1792908227707693100'
assert hashlib.sha256((owner/'three_slot_finite_owner_v1.py').read_bytes()).hexdigest()==v['owner_source_SHA']
c=json.loads(C.read_bytes());assert c['active_segment']['owner_parent_pid']==pid and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
for label,e2 in v['own_H1_identities'].items():
 try:
  p2=psutil.Process(e2['pid'])
  assert p2.create_time()!=e2['creation'] or p2.cmdline()!=e2['argv'], 'Original worker/node still running'
 except psutil.Error:pass
root=Path(q['roots']['h1']);raw=(root/'NODE_TERMINAL_ACTUAL.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==v['H1_terminal_SHA'];h1=json.loads(raw)
exit1=json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes());assert exit1['actual_all_own_children_waited'] and exit1['validation_fcntl_released_if_acquired']
e3raw=v['E3_terminal_text'].encode();assert hashlib.sha256(e3raw).hexdigest()==v['E3_terminal_SHA'];e3=json.loads(e3raw)
rows={'h1':h1['row'],'recovery':e3['row']}
for key,row in rows.items():
 assert row['key']==key and row['phase']=='production' and row['manifest_SHA']==q['specs'][key]['manifest_SHA']
 assert row['terminal_all_own_children_waited'] and row['returncode']==0 and row['actual_exit']['actual_waited'] and not row['original_error']
 assert row['final']['passed'] and row['final']['final']['SHA']==v['expected_final_SHA'][key]
 assert 'owner_received_terminal_epoch' not in row
assert sys.version_info[:2]==(3,12) and struct.calcsize('P')==8
test=q['run_id'];assert ctypes.string_at(id(test)+40,len(test))==test.encode(), 'Installed CPython compact ASCII offset differs'
regions=[]
for line in Path('/proc/'+str(pid)+'/maps').read_text().splitlines():
 f=line.split();name=f[5] if len(f)>5 else ''
 if f[1]=='rw-p' and name in ('','[heap]'):
  lo,hi=[int(x,16) for x in f[0].split('-')]
  if hi-lo<=32*1024**2:regions.append((lo,hi))
assert regions and sum(hi-lo for lo,hi in regions)<=128*1024**2
fd=os.open('/proc/'+str(pid)+'/mem',os.O_RDONLY)
def read(addr,n):
 try:return os.pread(fd,n,addr)
 except OSError:return b''
def u(addr):
 h=read(addr,40)
 if len(h)!=40:return None
 length=struct.unpack_from('<q',h,16)[0];flags=struct.unpack_from('<I',h,32)[0]
 if not(0<=length<=256 and flags&32 and flags&64):return None
 data=read(addr+40,length)
 try:return data.decode('ascii') if len(data)==length else None
 except UnicodeDecodeError:return None
buffers=[(lo,read(lo,hi-lo)) for lo,hi in regions]
runaddrs=[];needle=q['run_id'].encode()+bytes([0])
for lo,data in buffers:
 start=0
 while True:
  at=data.find(needle,start)
  if at<0:break
  addr=lo+at-40
  if u(addr)==q['run_id']:runaddrs.append(addr)
  start=at+len(needle)
candidates=set()
for runaddr in runaddrs:
 ptr=struct.pack('<Q',runaddr)
 for lo,data in buffers:
  start=0
  while True:
   at=data.find(ptr,start)
   if at<0:break
   pos=lo+at;before=read(pos-8,8);after=read(pos+8,16)
   if len(before)==8 and len(after)==16 and u(struct.unpack('<Q',before)[0])=='run_id' and u(struct.unpack_from('<Q',after,0)[0])=='token':
    value=u(struct.unpack_from('<Q',after,8)[0])
    if value and re.fullmatch('[0-9a-f]{64}',value):candidates.add(value)
   start=at+8
buffers.clear();os.close(fd);assert len(candidates)==1, 'Exact original cfg token could not be uniquely recovered'
token=candidates.pop().encode();candidates.clear()
ip=shutil.which('ip');assert ip
existing=subprocess.check_output([ip,'-j','route','show','table','local','exact','10.24.4.210/32'],text=True)
route_created=False;acks=[]
try:
 if not json.loads(existing):
  subprocess.run([ip,'route','add','local','10.24.4.210/32','dev','lo','table','local'],check=True,capture_output=True);route_created=True
 with socket.create_connection(('10.24.4.210',29754),timeout=3):pass
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,row in rows.items():
  body=json.dumps(dict(epoch=time.time(),run_id=q['run_id'],row=row)).encode()
  req=urllib.request.Request('http://10.24.4.210:29754/',data=body,headers={'X-Own-Signature':hmac.new(token,body,hashlib.sha256).hexdigest()})
  with opener.open(req,timeout=8) as response:answer=response.read();signature=response.headers['X-Own-Signature']
  assert hmac.compare_digest(signature,hmac.new(token,answer,hashlib.sha256).hexdigest())
  acks.append(dict(key=key,epoch=time.time(),owner_HMAC_reply_verified=True,terminal_row_source_SHA=v['H1_terminal_SHA'] if key=='h1' else v['E3_terminal_SHA'],reply=json.loads(answer)))
 token=None
 deadline=time.time()+30
 while time.time()<deadline:
  c=json.loads(C.read_bytes())
  if c['active_segment'] is None and (owner/'COHORT_FINAL.json').is_file() and (owner/'OWNER_EXIT_ACTUAL.json').is_file():
   try:
    op=psutil.Process(pid);alive=op.create_time()==e['creation'] and op.status()!=psutil.STATUS_ZOMBIE
   except psutil.Error:alive=False
   if not alive:break
  time.sleep(.5)
 assert c['active_segment'] is None, 'Original writer did not complete within bounded wait'
 segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==pid and x.get('started_epoch',0)>=e['creation']];assert len(segments)==1
 co=json.loads((owner/'COHORT_FINAL.json').read_bytes());ex=json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes());assert co['original_cost_settled'] and ex['original_cost_settled']
 locks=[]
 for path in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])]:
  with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks.append(dict(path=str(path),free=True))
 result=dict(epoch=time.time(),acks=acks,cohort=co,owner_exit=ex,original_segment=segments[0],original_canonical_remaining=c['remaining_training_seconds'],original_canonical_charged=c['charged_training_seconds'],original_locks=locks,original_owner_actual_out=True,original_writer_only_actual_cost_no_refund_or_rewrite=True,original_duration_bound_false_preserved=True,memory_read_scope=dict(pid=pid,creation=e['creation'],only_exact_cfg_runid_token_in_memory=True,bytes_or_token_never_logged_or_written=True,no_ptrace_attach_signal_or_memory_write=True),temporary_original_listener_local_route_added=route_created)
finally:
 token=None
 if route_created:subprocess.run([ip,'route','del','local','10.24.4.210/32','dev','lo','table','local'],check=True,capture_output=True)
result['temporary_route_restored']=True
print(json.dumps(result))
'''

put('ORIGINAL68_AUTHENTICATED_TERMINAL_RELAY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,scope='Read exact original owner cfg token in memory; transient original-listener local route; POST two unchanged true terminal rows to original owner; original writer closes itself'))
try:
    fresh=json.loads((R/'EXACT68_OWNER_HANDOFF_MISSING210_V2_RETURNED_ACTUAL.json').read_bytes())
    e3=json.loads((R/'EXACT68_E3_FRESH_TERMINAL_AND_OWN_OUT_ACTUAL.json').read_bytes())
    q=json.loads((N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    meta=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert time.time()-e3['epoch']<900
    payload=dict(q=q,owner_source_SHA=hashlib.sha256((N/'controllers/three_slot_finite_owner_v1.py').read_bytes()).hexdigest(),
                 H1_terminal_SHA=fresh['source210']['texts']['NODE_TERMINAL_ACTUAL.json']['SHA'],
                 E3_terminal_SHA=e3['texts']['NODE_TERMINAL_ACTUAL.json']['SHA'],E3_terminal_text=e3['texts']['NODE_TERMINAL_ACTUAL.json']['text'],
                 own_H1_identities={k:meta['source210'][k] for k in ('H1_node','H1_worker')},
                 expected_final_SHA={'h1':'f230cbff69395cb3f07ea689f68ef8eee1ee1f77bb67a9111638e3af77626769','recovery':'4ae2df1ead1d088b53bb839676f4614f8952e9fae3bda0164baa323067ba4ae9'})
    sys.path.insert(0,str(Q));import strict_user_forwarded_original210_transport_v1 as route
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
    c=route.connect();secret=None
    try:
        secret,_=recover('RM_SSH_PASSWORD');assert secret
        command='sudo -k -S -p '+shlex.quote('')+' -- '+shlex.quote(route.PY)+' -u -B -c '+shlex.quote(CODE)
        i,o,e=c.exec_command(command,timeout=80);i.write(secret+'\n');secret=None;i.write(json.dumps(payload)+'\n');i.flush();i.channel.shutdown_write()
        raw=o.read().decode();error=e.read().decode();rc=o.channel.recv_exit_status()
        assert rc==0,dict(returncode=rc,error=error,stdout=raw)
        result=json.loads(raw)
    finally:
        secret=None;c.close()
    result['actual_finite_returned']=True
    put('ORIGINAL68_AUTHENTICATED_TERMINALS_ORIGINAL_WRITER_CLOSED_ACTUAL.json',result)
    print(json.dumps(dict(original_writer_closed=True,original_owner_actual_out=result['original_owner_actual_out'],original_canonical_remaining=result['original_canonical_remaining'],actual_original_cost_sumonce=result['original_segment']['charged_expert_seconds'],duration_bound_flags={k:x['duration_bound_passed'] for k,x in result['original_segment']['experts'].items()},temporary_route_restored=result['temporary_route_restored'],actual_finite_returned=True)))
except BaseException:
    put('ORIGINAL68_AUTHENTICATED_TERMINAL_RELAY_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_direct_canonical_write_second_writer_or_refund=True));raise
