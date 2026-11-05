"""One existing-canonical launch, FIRST receiver and subsequent formal collector."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, time, traceback

HERE=Path(__file__).resolve().parent
SOURCE_ROOT=HERE
REPORTS=HERE/'reports'
ADMISSION_REPORTS=None
OLD=HERE.parent/'mod4v1_scut_step270_2h_20261103'
REPO=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE=REPO/'project/isaac/mod4v2_scut'
HARDWARE=Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package')
PYTHON='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe'
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def put(name,value):
    with(REPORTS/name).open('x',encoding='utf8')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)


def local(reports=None):
    from types import SimpleNamespace
    from shared_control_access import connection
    return SimpleNamespace(connection=lambda label: connection(reports or REPORTS, label))


READ_RESOURCE=r'''
from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,time
b=Path('/home/lc01/Zonglin Li/zonglin2')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
print(json.dumps(dict(epoch=time.time(),gpu=gpu,apps=apps,ram=psutil.virtual_memory().available,disk=shutil.disk_usage(b).free,canonical_reads=0,canonical_writes=0,human_direct=True)))
'''


def stage_rows():
    rows=[]
    def add(path,relative):
        raw=path.read_bytes();rows.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    prepared=read(HERE/'SOURCE_ONLY_PREPARED.json')
    for row in prepared['files']:add(Path(row['path']),row['relative'])
    for name in ['PLAN.json','entry.py','owner.py']:add(HERE/name,name)
    return rows


def launch():
    assert not(REPORTS/'LAUNCH_ONCE.json').exists()
    plan=read(HERE/'PLAN.json');job=plan['remote_root']
    review=read(plan['previous_native_review'])
    assert review['all_actual_images_reviewed'] and review['complete_all80_review']
    assert review['decision']=='REPLACE_SAMPLER_WITH_WARP_AS_HUMAN_REQUESTED'
    assert review['checkpoint_SHA']==plan['source_checkpoint']['SHA']
    admission_reports=ADMISSION_REPORTS or REPORTS
    peer=read(admission_reports/'RELEASED_PEER_CONTEXT.json')if (admission_reports/'RELEASED_PEER_CONTEXT.json').exists()else {}
    with local(admission_reports).connection('MOD4V2_FRESH_TRAIN_LAUNCH')as(client,transport):
        resource=transport.code(client,transport.PY72,READ_RESOURCE,peer,timeout=45)
        with(admission_reports/'FRESH_RESOURCE_ADMISSION.json').open('x',encoding='utf8')as stream:json.dump(resource,stream,indent=2)
        assert plan['human_direct_no_ledger_admission']
        assert resource['ram']>64*1024**3 and resource['disk']>50*1024**3
        candidates=[]
        for line in resource['gpu'].splitlines():
            row=[s.strip()for s in line.split(',')]
            if row[2]!='NVIDIA GeForce RTX 4090':continue
            free,used,util=map(int,row[4:7]);busy=row[1]in resource['apps']
            if free>15669 and(not busy or(used<=4096 and util<=30)):
                candidates.append((not busy,free,row[1]))
        assert candidates,'No admissible original-host4090'
        plan['GPU_UUID']=max(candidates)[2];plan.pop('pending_actual_resource_selection')
        (HERE/'PLAN.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
        rows=stage_rows()
        # Every fallback source is referenced once; assets remain the released package.
        shared=read(HERE/'SOURCE_ONLY_PREPARED.json')['shared_text']
        bypath={row['path']:row for row in shared};shared=list(bypath.values())
        index=dict(epoch=time.time(),files=rows,shared_text=shared,source_only=True,
                   fresh_training=False,full_state_continuation=True,old_v1_policy_loaded=False,source_model_copies=0)
        with(HERE/'INDEX_SOURCE_FROZEN.json').open('x',encoding='utf8')as f:json.dump(index,f,indent=2)
        create="from pathlib import Path; import json; p=Path(v['job']);p.mkdir(exist_ok=False);print(json.dumps(dict(created=str(p))))"
        transport.code(client,transport.PY72,create,dict(job=job),timeout=30)
        put('LAUNCH_ONCE.json',dict(epoch=time.time(),index_SHA=sha(HERE/'INDEX_SOURCE_FROZEN.json'),remote=job))
        sf=client.open_sftp()
        try:
            def upload(relative,raw):
                cursor=job
                for part in relative.split('/')[:-1]:
                    cursor+='/'+part
                    try:sf.mkdir(cursor)
                    except OSError:sf.stat(cursor)
                with sf.file(job+'/'+relative,'wx')as stream:stream.write(raw);stream.flush()
            for row in rows:upload(row['relative'],Path(row['path']).read_bytes())
            manifest=dict(files=[{k:r[k]for k in ['relative','bytes','SHA']}for r in rows],shared_text=shared)
            upload('INSTALL_MANIFEST.json',json.dumps(manifest,indent=2).encode())
            put('INSTALL_MANIFEST_LOCAL.json',manifest)
        finally:sf.close()
        start=r'''
from pathlib import Path
import json,subprocess,psutil,time
j=Path(v['job'])
with(j/'OWNER.log').open('xb')as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(j/'owner.py')],cwd=j,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 q=psutil.Process(p.pid)
 print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())))
'''
        owner=transport.code(client,transport.PY72,start,dict(job=job),timeout=30)
        put('OWNER_LAUNCH.json',owner);print(json.dumps(dict(owner=owner)),flush=True)
        put('FIRST_ONCE.json',dict(epoch=time.time(),owner=owner,max_seconds=900))
        for tick in range(60):
            code=r'''
from pathlib import Path
import json,time,hashlib
j=Path(v['job']);out={}
for rel in ['GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','OWNER_CURRENT.json','WORKER_IDENTITY.json','OWNER_ERROR.json','OWNER_EXIT.json','TRAIN_CLOSED.json','production/MOD4V2_PREIMPORT_BINDING.json','production/MOD4V2_NATIVE_HARDWARE.json','production/FRESH_INITIALIZATION.json','production/FUDAN_REWARD_RECIPE.json','production/WARP_SAMPLING.json','production/WARP_NATIVE_PARITY.json','production/FULL_STATE_RESTORE.json','production/STARTUP.json','production/FIRST_UPDATED.json','production/ERROR.json','production/FINAL.json']:
 p=j/rel
 if p.is_file():
  try:out[rel]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
for rel in ['OWNER.log','WORKER.log']:
 p=j/rel
 if p.is_file():
  raw=p.read_bytes();out[rel]=raw[-16000:].decode('utf8','replace')
  if rel=='WORKER.log' and ('production/FIRST_UPDATED.json'in out or 'OWNER_EXIT.json'in out):
   out['WORKER_COMPLETE.log']=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
print(json.dumps(dict(epoch=time.time(),files=out)))
'''
            result=transport.code(client,transport.PY72,code,dict(job=job),timeout=30)
            files=result['files']
            if 'production/FIRST_UPDATED.json'in files or 'OWNER_EXIT.json'in files:
                put('FIRST_ACTUAL_RETURNED.json',result);break
            if tick%4==0:print(json.dumps(dict(wait=tick,files=list(files),tail=files.get('WORKER.log','')[-600:])),flush=True)
            time.sleep(15)
        else:
            put('FIRST_PENDING_OR_ERROR.json',result)
            raise RuntimeError('First result pending; original owner remains responsible')
    files=result['files'];first=files.get('production/FIRST_UPDATED.json')
    log=files.get('WORKER_COMPLETE.log',{})
    errors=[line for line in log.get('text','').splitlines()if any(term in line.lower()for term in
        ['[error]','traceback (most recent call last)','cooking failure','failed to cook','patch buffer overflow','outofmemoryerror','dropped pair'])]
    restore=files.get('production/FULL_STATE_RESTORE.json')or{}
    valid=bool(first and first['iteration']==plan['source_checkpoint']['iteration']+1 and first['actual_onpolicy_samples']==480000
        and first['gradient']['steps']==20 and first['gradient']['actor_norm']>0
        and first['gradient']['critic_norm']>0 and not errors
        and 'production/ERROR.json'not in files and files.get('production/FRESH_INITIALIZATION.json')
        and files.get('production/MOD4V2_NATIVE_HARDWARE.json')
        and files.get('production/FUDAN_REWARD_RECIPE.json',{}).get('family')=='FUDAN_JUMP'
        and files.get('production/FUDAN_REWARD_RECIPE.json',{}).get('SCUT_reward_terms_active')is False
        and files.get('production/WARP_SAMPLING.json',{}).get('cuda_graphs') is True
        and files.get('production/WARP_NATIVE_PARITY.json',{}).get('passed') is True
        and restore.get('source_iteration')==plan['source_checkpoint']['iteration'] and restore.get('optimizer_state_entries')==17
        and restore.get('optimizer_step_min')==restore.get('optimizer_step_max')==plan['source_optimizer_step']
        and not restore.get('task_changed') and restore.get('command_profile_adaptation')==[])
    put('FIRST_FULL_LOG_VALIDATION.json',dict(epoch=time.time(),valid=valid,FIRST=first,errors=errors,
        restore=restore,hardware=files.get('production/MOD4V2_NATIVE_HARDWARE.json'),fresh=files.get('production/FRESH_INITIALIZATION.json')))
    assert valid,'Newv2FIRST not validated; inspect actual error, never auto relaunch'
    bind()
    print(json.dumps(dict(valid_FIRST=first,collector=read(REPORTS/'POSTROUND_EXACT_CIM.json'))),flush=True)


def bind():
    assert not(REPORTS/'POSTROUND_BIND_ONCE.json').exists()
    put('POSTROUND_BIND_ONCE.json',dict(epoch=time.time(),sole_receiver=True))
    with(REPORTS/'POSTROUND_STDOUT.log').open('xb')as out,(REPORTS/'POSTROUND_STDERR.log').open('xb')as err:
        p=subprocess.Popen([PYTHON,'-B','-X','utf8',str(Path(__file__)),'collect','--root',str(HERE)],cwd=HERE,
            stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    query='Get-CimInstance Win32_Process -Filter "ProcessId = '+str(p.pid)+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    row=subprocess.run(['pwsh','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    put('POSTROUND_EXACT_CIM.json',dict(epoch=time.time(),row=json.loads(row.stdout)))


def collect():
    put('POSTROUND_ONCE.json',dict(epoch=time.time(),pid=os.getpid()))
    go=read(REPORTS/'FIRST_ACTUAL_RETURNED.json')['files']['GO_PRODUCTION.json']
    while time.time()<go['save_deadline']+45:time.sleep(min(10,go['save_deadline']+45-time.time()))
    receiver=load('v2_original_collector',OLD/'postround.py')
    receiver.A=HERE;receiver.R=REPORTS;receiver.m.R=REPORTS;receiver.put=put
    receiver.m.connection=lambda label: local().connection(label)
    original_code=receiver.m.connection
    from contextlib import contextmanager
    @contextmanager
    def direct_receive_connection(label):
        with local().connection(label)as(client,transport):
            original=transport.code
            class DirectTransport:
                PY72=transport.PY72
                @staticmethod
                def code(client,python,source,value,**kwargs):
                    begin=source.find("c=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')")
                    if begin>=0:
                        end=source.index('for rel in ',begin)
                        source=source[:begin]+"files['direct_no_canonical_access']=dict(human_direct=True,canonical_reads=0,canonical_writes=0)\n"+source[end:]
                    return original(client,python,source,value,**kwargs)
            yield client,DirectTransport
    receiver.m.connection=direct_receive_connection
    receiver.receive(read(HERE/'PLAN.json')['remote_root'],'MOD4V2_POSTROUND_RETURN')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['launch','collect'])
    p.add_argument('--root',type=Path);p.add_argument('--admission-receipt-subdir');a=p.parse_args()
    if a.root:
        HERE=a.root.resolve();assert HERE.is_relative_to(SOURCE_ROOT)
        REPORTS=HERE/'reports'
        HARDWARE=Path(read(HERE/'PLAN.json').get('hardware_local',str(HERE/'hardware')))
    if a.admission_receipt_subdir:
        ADMISSION_REPORTS=(REPORTS/a.admission_receipt_subdir).resolve();assert ADMISSION_REPORTS.is_relative_to(REPORTS)
        assert ADMISSION_REPORTS.is_dir()and not(ADMISSION_REPORTS/'FRESH_RESOURCE_ADMISSION.json').exists()
    try:globals()[a.mode]()
    except BaseException:
        put('CONTROL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
        raise
