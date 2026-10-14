"""Root-only new yaw-pi factor admission and single native120 dispatch.

Copies an existing admitted payload byte-exact into a new namespace. No old
task or GPU case runs, no PPO, no Linux connection, no retry after uncertainty.
"""
from pathlib import Path
import sys, json, time, hashlib, traceback, os

P = Path(__file__).resolve().parent
W = P.parent
R = P / 'reports'
sys.path.insert(0, str(W / 'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t

ROOT = 'D:/MOD4_async_eval/MOD4_E3_YAWPI_FRAME_FACTOR_20261014'
BASE = 'D:/MOD4_async_eval/MOD4_3060_LEFT_SECOND_FULL80_20261014/payload'
CASE = 'e3_yawpi_same_world_native120_v2'
TASK = 'MOD4_E3_YawPi_SameWorld_Native120_v2_20261014'
SHA = 'e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
t.ROOT = ROOT
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(name, value):
    p = R / name
    assert not p.exists()
    with p.open('xb') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2).encode())
        f.flush()
        os.fsync(f.fileno())
    return p


def main():
    assert not (R / 'YAWPI_NATIVE120_DEPLOY_INTENT.json').exists(), 'Read actual outcome; do not re-dispatch'
    hand = json.loads((R / 'YAWPI_FRAME_FACTOR_CPU_HANDOFF_COMPLETE.json').read_bytes())
    assert hand['CPU_only_complete'] and hand['source_E3'] == SHA
    components = hand['active_components']
    assert len(components) == 4
    for row in components:
        assert H(row['path']) == row['sha256']
        assert Path(row['path']).stat().st_size == row['bytes']
        compile(Path(row['path']).read_text(encoding='utf-8-sig'), row['path'], 'exec')
    c = sf = None
    try:
        c = t.connect()
        guard = t.py(c, t.guard_code())
        assert guard['new_root_unused']
        exists = t.ps(c, "$x=Get-ScheduledTask -TaskName '" + TASK + "' -ErrorAction SilentlyContinue;[PSCustomObject]@{present=($null -ne $x)}|ConvertTo-Json -Compress")
        assert not exists['present']
        save('YAWPI_NATIVE120_DEPLOY_INTENT.json', dict(epoch=time.time(), root=ROOT, case=CASE, task=TASK, guard=guard, components=components, no_GPU_started_yet=True, no_PPO=True))
        code = '''from pathlib import Path
import json,shutil,hashlib,importlib.metadata as metadata,torch,time
root=Path(ROOT);base=Path(BASE);assert not root.exists();root.mkdir()
p=root/'payload';shutil.copytree(base,p)
H=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
m=p/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';assert H(m)==MANIFESTSHA
manifest=json.loads(m.read_bytes())
for row in manifest['file_rows']:
 q=p/row['relative'];assert q.stat().st_size==row['bytes'] and H(q)==row['sha256']
sdk=json.loads((p/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,v in sdk['versions'].items():
 if v is not None:assert metadata.version(name)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
ck=p/'source/model_32635_left_repair.pt';assert H(ck)==SOURCESHA
source=torch.load(ck,map_location='cpu',weights_only=False)
counts=[0,0]
def walk(v):
 if isinstance(v,torch.Tensor):
  assert v.device.type=='cpu';counts[0]+=1
  if v.is_floating_point():assert torch.isfinite(v).all();counts[1]+=1
 elif isinstance(v,dict):
  for x in v.values():walk(x)
 elif isinstance(v,(list,tuple)):
  for x in v:walk(x)
walk(source)
assert counts==[195,107] and source['E1_terrain_state']['num_envs']==20000
assert len(source['actor_state_dict'])==9 and not torch.cuda.is_initialized()
report=dict(epoch=time.time(),original_shared_files=len(manifest['file_rows']),original_shared_files_byteexact=True,checkpoint_SHA=H(ck),whole195_float107_N20000=True,source_manifest_SHA=H(m),installed_backend_files=len(sdk['files']),no_GPU_or_PPO=True)
(root/'TARGET_SHARED_FULLSOURCE_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
'''
        code = code.replace('ROOT', repr(ROOT)).replace('BASE', repr(BASE)).replace('MANIFESTSHA', repr(hand['original_shared_reference_manifest']['sha256'])).replace('SOURCESHA', repr(SHA))
        target = t.py(c, code)
        save('YAWPI_NATIVE120_TARGET_SHARED_CPU_ACTUAL.json', target)
        sf = c.open_sftp()
        for row in components:
            sf.put(row['path'], ROOT + '/payload/' + row['relative'])
        verify = "from pathlib import Path\nimport json,hashlib\nroot=Path(" + repr(ROOT) + ");rows=" + repr(components) + "\nfor row in rows:\n p=root/'payload'/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']\nprint(json.dumps(dict(new_components_byteexact=True,rows=rows)))"
        save('YAWPI_NATIVE120_NEW_COMPONENTS_TARGET_ACTUAL.json', t.py(c, verify))
        fresh = t.py(c, t.guard_code())
        assert not fresh['new_root_unused']
        byname = {r['relative']: r for r in components}
        lease = dict(epoch=time.time(), case_id=CASE, target_host='10.24.4.249', namespace=P.name,
                     GPU_lease_granted_by_root=True, actual_shared_slot_idle_verified=True, resource_boundary=fresh,
                     checkpoint_path=ROOT+'/payload/source/model_32635_left_repair.pt', checkpoint_sha256=SHA,
                     worker_sha256=byname['paired_full80_yawpi_same_world_v2.py']['sha256'],
                     factor_runtime_sha256=byname['full80_yawpi_same_world_runtime_v2.py']['sha256'],
                     new_factor_components=[dict(relative=x['relative'], bytes=x['bytes'], sha256=x['sha256']) for x in components],
                     source_bundle_manifest_sha256=hand['original_shared_reference_manifest']['sha256'],
                     case_parameters=dict(steps=120,num_envs=80,seed=20260928,body_sign=-1,world_sign=1,yaw_pi_body_flip=True,feedback_current=False,headless=True,device='cuda:0'),
                     own_new_native120_required_before_full1500=True, root30_NOT_baseline_byteexact=True, no_PPO=True, no_qualification=True)
        leasepath = ROOT + '/ROOT_GPU_LEASE_NATIVE120.json'
        blob = json.dumps(lease, ensure_ascii=False, indent=2).encode()
        with sf.open(leasepath, 'wx') as f:
            f.write(blob); f.flush()
        launcher = '''from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
R=Path(__file__).resolve().parent
entered=R/'NATIVE120_LAUNCH_ENTERED.json';assert not entered.exists()
lease=R/'ROOT_GPU_LEASE_NATIVE120.json';attempt=R/'attempts/CASE';assert not attempt.exists()
with entered.open('xb') as f:
 f.write(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(R/'payload/run_full80_yawpi_same_world_parent_v2.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (R/'NATIVE120_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(R/'payload'),stdout=log,stderr=subprocess.STDOUT)
 (R/'NATIVE120_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True)))
 rc=p.wait()
(R/'NATIVE120_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),parent_pid=p.pid,exit_code=rc,no_PPO=True)))
sys.exit(rc)
'''.replace('CASE', CASE)
        local = P / 'launch_yawpi_new_native120_once.py'
        assert not local.exists(); compile(launcher,str(local),'exec'); local.write_bytes(launcher.encode())
        sf.put(str(local), ROOT+'/'+local.name)
        setup = t.ps(c, "$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$action=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+local.name+"\"' -WorkingDirectory '"+ROOT+"';$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings|Out-Null;$x=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$x.State;triggers=@($x.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
        assert setup['triggers']==0
        save('YAWPI_NATIVE120_TASK_REGISTERED_ACTUAL.json', setup)
        start = t.ps(c, "$ErrorActionPreference='Stop';$p='"+ROOT+"/NATIVE120_TASK_START_INTENT.json';if(Test-Path -LiteralPath $p){throw 'Start consumed'};[IO.File]::WriteAllText($p,'{\"single_start_requested\":true}');Start-ScheduledTask -TaskName '"+TASK+"';$x=Get-ScheduledTask -TaskName '"+TASK+"';[PSCustomObject]@{task=$x.TaskName;state=[string]$x.State;triggers=@($x.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
        save('YAWPI_NATIVE120_UNIQUE_DISPATCH_ACTUAL.json', dict(epoch=time.time(), task=start, lease=lease, lease_SHA=hashlib.sha256(blob).hexdigest(), launcher_SHA=H(local), no_old_case_replayed=True, actual_physical_result_pending=True))
        print(json.dumps(dict(unique_native120_dispatched=True, task=start, root=ROOT, no_PPO=True)),flush=True)
    except BaseException:
        save('YAWPI_NATIVE120_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(), error=traceback.format_exc(), unknown_outcome_requires_read_only=True, no_blind_retry=True))
        raise
    finally:
        if sf:sf.close()
        t.close(c)


if __name__ == '__main__':
    main()
