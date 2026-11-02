"""Retrieve only four known actual446 recordedpose files; no checkpoint/SDK/physics/account writes."""
from pathlib import Path
import argparse
import base64
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback

C=Path(__file__).resolve().parent;T=C.parent;W=T.parent;R=C/'reports'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(name,value):
    with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value

REMOTE=r'''from pathlib import Path
import base64,fcntl,hashlib,json,time,traceback
task=v['task'];locks=[];packets=[];admission=None;error=None
try:
 for path in('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'):
  f=Path(path).open('rb+')
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BaseException:f.close();raise
  locks.append(f)
 canonical=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();authority=json.loads(canonical)
 assert authority['active_segment']is None and authority['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
 assert authority['authorized_training_seconds']==2268000 and authority['new_authority_budget_extensions']==[]
 admission=dict(epoch=time.time(),freshCNone=True,canonicalSHA=hashlib.sha256(canonical).hexdigest(),private_shared_EX_acquired=True,canonical_writes=0,SDK=0,modelreads=0,physics=0)
 root=Path(task['source_evaluation_job'])/'actual_capture'
 for row in task['cases']:
  path=Path(row['path']);assert path.resolve().is_relative_to(root.resolve())and path.name==('REPLAY446_env'+str(row['env'])+'.npz')
  data=path.read_bytes();assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['SHA']
  packets.append(dict(env=row['env'],bytes=len(data),SHA=row['SHA'],b64=base64.b64encode(data).decode('ascii')))
except BaseException:error=traceback.format_exc()
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
print(json.dumps(dict(passed=error is None,epoch=time.time(),error=error,admission=admission,packets=packets,all_own_children_waited=True,children_created=0,all_owned_locks_released=True,modelreads=0,SDK=0,physics=0,account_writes=0)))'''

def main():
    assert sys.version_info[:2]==(3,14)
    parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
    index=C/'INDEX451_SOURCE_TASK_FROZEN.json';assert H(index)==args.caller_index_SHA
    for row in read(index)['files']:
        path=Path(row['path']);assert path.stat().st_size==row['bytes']and H(path)==row['SHA']
    assert not(R/'ROOT451_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
    task=read(C/'TASK451_FROZEN.json')
    assert H(Path(task['source_result']))==task['source_resultSHA']
    pattern='MOD4_H1|RMPOLAR|watch|run_once_after_resume|E1collect|prepare_archive|single_gpu|collect_nine|collect_generic|collect_actual|PAIR|postround|stage_new|dispatch|retention'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
    result=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    assert not result.stderr.strip()
    rows=json.loads(result.stdout)if result.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    own=[row for row in rows if row['ProcessId']==os.getpid()];other=[row for row in rows if row['ProcessId']!=os.getpid()]
    assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()
    put('ROOT451_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,serialFREE=not other))
    assert not other,'Known controller still holds serialscope; no network'
    put('ROOT451_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),taskSHA=H(C/'TASK451_FROZEN.json'),known_recordedpose_files=4,modelreads=0,SDK=0,physics=0,account_writes=0))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    transport=previous=client=secret=None
    try:
        transport,previous=module('replay451_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('replay451_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        result=d.code(client,d.PY72,REMOTE,dict(task=task),timeout=90)
        receipt={key:value for key,value in result.items()if key!='packets'}
        receipt['packet_metadata']=[{key:row[key]for key in('env','bytes','SHA')}for row in result.get('packets',[])]
        put('ROOT451_ACTUAL_PARENT_READONLY_TRANSFER_RETURNED.json',receipt)
        assert result['passed']and not result['error']and result['all_owned_locks_released']
        dest=C/'replay_actual446';dest.mkdir(exist_ok=False);transfers=[]
        assert len(result['packets'])==len(task['cases'])==4
        for row,packet in zip(task['cases'],result['packets']):
            assert row['env']==packet['env']and row['bytes']==packet['bytes']and row['SHA']==packet['SHA']
            data=base64.b64decode(packet['b64'],validate=True);assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['SHA']
            path=dest/Path(row['path']).name
            with path.open('xb')as stream:stream.write(data)
            transfers.append(dict(row,local_path=str(path),transfers=1,two_host_SHA_equal=True,actual446_not_oldcopied437=True))
        put('ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json',dict(epoch=time.time(),passed=True,model_SHA=task['source_modelSHA'],cases=transfers,actual_physics_source='saved446bodyposes',modelreads=0,SDK=0,physics=0))
        print(json.dumps(dict(passed=True,knownactual446cases=4,bytes=sum(row['bytes']for row in transfers),modelSHA=task['source_modelSHA'],modelreads=0,SDK=0,physics=0)),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT451_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))

if __name__=='__main__':
    try:main()
    except BaseException:
        put('ROOT451_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True));raise
