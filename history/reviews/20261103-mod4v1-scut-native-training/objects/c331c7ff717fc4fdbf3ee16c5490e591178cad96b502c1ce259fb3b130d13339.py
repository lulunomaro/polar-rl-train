"""Inspect the human-selected forwarded4090 and its Windows data disks."""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import time
import traceback

N=Path(__file__).resolve().parent
A=N/'env20000_jump200_1h_20261104'
R=A/'reports'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def put(name,value):
    with(R/name).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2)


def inspect210():
    """Human-requested independent host read; no72 connection or budget I/O."""
    import hashlib
    local=load('jump200_210_local_context',N/'run.py');rows=local.local_rows()
    put('WINDOWS210_LOCAL_CONTEXT.json',dict(epoch=time.time(),rows=rows,
        human_scope='端口转发的单4090主机可以在Windows盘放数据',
        independent_host210_read_only=True,no72connection_or_original_ledger_access=True))
    base=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/control/archived_connectors')
    wrapper=load('jump200_210_same_compressed',base/'same_authorized_session_compressed_transport_v227.py')
    wrapper.W=Path('C:/Users/lulu/Desktop/claude/mjcf')
    transport=previous=client=None
    code='''from pathlib import Path
import os,json,subprocess,shutil,time
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=25);return dict(rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
mounts=Path('/proc/mounts').read_text();disks={}
for line in mounts.splitlines():
 a=line.split();path=a[1].replace('\\040',' ')
 if a[2]in('9p','drvfs','fuseblk','ntfs','ntfs3')or path.startswith('/mnt/'):
  try:
   d=shutil.disk_usage(path);disks[path]=dict(source=a[0],filesystem=a[2],total=d.total,used=d.used,free=d.free,writable=os.access(path,os.W_OK))
  except OSError:pass
mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()if line.startswith(('MemAvailable:','MemTotal:'))}
print(json.dumps(dict(epoch=time.time(),gpu=cmd(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits']),compute_apps=cmd(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),ram=mem,home_disk=dict(zip(['total','used','free'],shutil.disk_usage(Path.home()))),windows_disks=disks,mounts=mounts,kernel=cmd(['uname','-r']),filesystem_writes=0,SDK=0,PT_reads=0,physics=0,canonical_access=0)))'''
    try:
        transport,previous=wrapper.install()
        route=load('jump200_pinned_210',base/'strict_user_forwarded_original210_transport_v1.py');route.W=wrapper.W
        client=route.connect()
        i,o,e=client.exec_command(shlex.quote(route.PY)+' -B -c '+shlex.quote(code),timeout=80);i.close()
        raw=o.read().decode();error=e.read().decode();rc=o.channel.recv_exit_status()
        assert rc==0,(rc,error)
        value=json.loads(raw)
        put('WINDOWS210_MOUNTS_MEMORY_GPU_ACTUAL.json',dict(epoch=time.time(),actual=value,
            route='Existing pinned original210 through authorized4090port',
            raw_bytes=len(raw.encode()),raw_SHA=hashlib.sha256(raw.encode()).hexdigest()))
        print(json.dumps(value,ensure_ascii=False,indent=2))
    finally:
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('WINDOWS210_SSH_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,
            SESSION_restored=transport is None or transport.SESSION is previous,serial='FREE'))


def inspect():
    target=R/('FOUR_GPU_WINDOWS_'+str(time.time_ns()));target.mkdir()
    m=load('jump200_windows_original_four',N/'check_four_gpu.py');m.R=target
    needle='print(json.dumps(result))'
    assert m.READ.count(needle)==1
    extra='''
import os,hashlib
result['windows_disks']={}
for drive in ('c','d','e','f','g','h'):
 p=Path('/mnt')/drive
 if p.is_dir():
  d=shutil.disk_usage(p);result['windows_disks'][str(p)]=dict(mounted=os.path.ismount(p),total=d.total,used=d.used,free=d.free)
result['mounted_filesystems']=Path('/proc/mounts').read_text()
result['memory_limit']={}
for name in ('/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory/memory.limit_in_bytes'):
 p=Path(name)
 if p.is_file():result['memory_limit'][name]=p.read_text().strip()
result['target_python']=dict(executable=__import__('sys').executable,version=__import__('sys').version)
result['exact_source_text']={}
base=Path('/home/lc01/Zonglin Li/zonglin2')
for name in ('tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_1h/owner.py',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/control/three_slot_common_v1.py',
 'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400/control/single_writer72_authority_V85M_source.py'):
 p=base/name
 if p.is_file():
  raw=p.read_bytes();result['exact_source_text'][name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'))
'''
    m.READ=m.READ.replace(needle,extra+'\n'+needle)
    m.main()
    actual=json.loads((target/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json').read_bytes())
    assert actual['all_clients_closed']and actual['SESSION_restored']
    summary={}
    for host,row in actual['hosts'].items():
        value=row.get('actual',{})
        summary[host]={key:value.get(key)for key in('epoch','gpu','compute_apps','canonical','locks','ram','disk','windows_disks','memory_limit','target_python')}
        summary[host].update(passed=row['passed'],error=row.get('error'))
    receipt=dict(epoch=time.time(),human_quote='端口转发的单4090主机可以在Windows盘放数据',
        report=str(target/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'),summary=summary,
        model_reads=0,SDK=0,physics=0,canonical_writes=0,all_clients_closed=True,SESSION_restored=True)
    with(R/'FORWARDED_WINDOWS_DISK_ACTUAL.json').open('x',encoding='utf8',newline='\n')as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return target,actual


def bind():
    assert not(R/'WINDOWS_ROUTE_RESUME_BIND_ONCE.json').exists()
    assert not(R/'LAUNCH_ONCE.json').exists()and not(A/'INDEX_SOURCE_FROZEN.json').exists()
    local=load('jump200_windows_bind_local',N/'run.py');rows=local.local_rows()
    others=[row for row in rows if row['ProcessId']!=os.getpid()]
    assert not any('jump200_training_control.py'in(row.get('CommandLine')or'')or
        'jump200_forwarded_windows.py'in(row.get('CommandLine')or'')for row in others)
    put('WINDOWS_ROUTE_RESUME_BIND_ONCE.json',dict(epoch=time.time(),human='端口转发的单4090主机可以在Windows盘放数据',
        sole_local_wait=True,foreign_controller_rows=others,pre_network=True,old67488once_preserved=True))
    with(R/'WINDOWS_ROUTE_RESUME_STDOUT.log').open('xb')as out,(R/'WINDOWS_ROUTE_RESUME_STDERR.log').open('xb')as err:
        process=subprocess.Popen([CONTROL,'-B','-X','utf8',str(Path(__file__)),'resume'],cwd=N,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(process.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    result=subprocess.run(['pwsh','-NoProfile','-NonInteractive','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put('WINDOWS_ROUTE_RESUME_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(result.stdout)))
    print(json.dumps(dict(bound=True,PID=process.pid,wait='Only existing local controller, then actual original locks; no fixed20:57 delay',training_GO=False)))


def resume():
    put('WINDOWS_ROUTE_RESUME_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),pre_network=True))
    local=load('jump200_windows_serial_wait',N/'run.py');local.R=R
    started=time.time()
    while any(row['ProcessId']!=os.getpid()for row in local.local_rows()):
        if time.time()-started>10800:raise RuntimeError('Existing local serial controller did not exit within3h')
        time.sleep(10)
    target,actual=inspect()
    host=actual['hosts']['72']['actual'];active=host['canonical']['active']
    wait=json.loads((A/'RESOURCE_WAIT_FROZEN.json').read_bytes())
    if active is not None and active['owner_run_id']!=wait['peer_GO']['run_id']:
        put('WINDOWS_ROUTE_OTHER_CANONICAL_OWNER_BLOCKED.json',dict(epoch=time.time(),active=active,report=str(target)))
        return
    # Keep the already authorized producer and its original accounting. An idle
    # forwarded card is not a second canonical writer. Its disk evidence is
    # retained independently from the currently ready production destination.
    code='''from pathlib import Path
import json,time,fcntl
b=Path('/home/lc01/Zonglin Li/zonglin2');C=b/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes());peer=Path(v['peer_root']);s=json.loads((peer/'OWNER_STARTED.json').read_bytes())['identity'];p=peer/'OWNER_EXIT.json';e=json.loads(p.read_bytes())if p.is_file()else None
same=all(s.get(k)==v['peer_identity'].get(k)for k in('pid','creation','exe','argv','root'))
ready=same and e is not None and all(e.get(k,False)for k in('all_own_waited','original_cost_settled','original_leases_released'))and c['active_segment']is None
locks={}
if ready:
 for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
  try:
   with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   locks[str(p)]=True
  except BlockingIOError:locks[str(p)]=False
 ready=all(locks.values())and c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),ready=bool(ready),canonical_active=c['active_segment'],remaining=c['remaining_training_seconds'],peer_identity_matches=same,peer_exit=e,locks=locks,PT_reads=0,physics=0,canonical_writes=0)))'''
    with local.connection('JUMP200_WINDOWS_ROUTE_RELEASE')as(client,d):
        for tick in range(31):
            value=d.code(client,d.PY72,code,wait,timeout=40)
            if value['ready']:break
            if not value['peer_identity_matches']:break
            if value['canonical_active']and value['canonical_active']['owner_run_id']!=wait['peer_GO']['run_id']:break
            if tick<30:time.sleep(30)
        put('WINDOWS_ROUTE_RELEASE_ACTUAL.json',value)
        if not value['ready']:return
    controller=load('jump200_windows_same_authorized_train',N/'jump200_training_control.py')
    # Reuse the fresh all-four read while within the producer's120s admission.
    import shutil
    dest=R/('FOUR_GPU_WINDOWS_READY_'+str(time.time_ns()));dest.mkdir()
    for name in ('FOUR_GPU_HUMAN_REQUEST_ACTUAL.json','FOUR_GPU_HUMAN_REQUEST_LOCAL_CIM.json'):
        shutil.copyfile(target/name,dest/name)
    controller.launch()
    put('WINDOWS_ROUTE_RESUME_COMPLETED.json',dict(epoch=time.time(),LAUNCH_consumed=(R/'LAUNCH_ONCE.json').exists(),
        postround_bound=(R/'POSTROUND_BIND_ONCE.json').exists(),FIRST_not_skill=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['inspect','inspect210','bind','resume'],nargs='?',default='inspect');a=p.parse_args()
    try:globals()[a.mode]()
    except BaseException:
        with(R/('WINDOWS_ROUTE_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8',newline='\n')as f:
            json.dump(dict(epoch=time.time(),error=traceback.format_exc()),f,indent=2)
        raise
