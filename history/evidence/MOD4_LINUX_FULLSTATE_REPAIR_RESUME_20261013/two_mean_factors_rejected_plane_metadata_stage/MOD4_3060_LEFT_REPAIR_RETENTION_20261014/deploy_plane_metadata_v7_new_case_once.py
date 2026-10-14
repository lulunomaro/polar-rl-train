"""Root-only unique 3060 metadata admission; sequential transport, no old replay."""
from pathlib import Path
import hashlib, json, sys, time, traceback

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
P = D / 'payload'
sys.path.insert(0, str(W / 'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t

ROOT = 'D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_QUERY_METADATA_V7_20261014'
SHARED = 'D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
CASE = 'native_plane_metadata160_zero_requested_controls_v7'
TASK = 'MOD4_PlaneMetadata160_NoControls_V7_20261014'
t.ROOT = ROOT
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(name, value):
    p = R / name
    assert not p.exists()
    p.write_text(json.dumps(value, indent=2), encoding='utf8')

def main():
    receipt = R / 'PLANE_METADATA_V7_DISPATCH_ACTUAL.json'
    assert not receipt.exists()
    z = D / 'RETENTION_PLANE_METADATA_CPU_PREPARED_V7.zip'
    assert z.stat().st_size == 146068 and H(z) == '6632c8e778ef15920a78567cf8db88f529493e8296be5dfeb10451d735eddb99'
    m = json.loads((P / 'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json').read_bytes())
    assert m['approved_GPU'] is False and m['target_namespace'] == ROOT.rsplit('/', 1)[-1]
    for row in m['package_files']:
        assert H(P / row['relative']) == row['sha256']
    c = t.connect()
    sf = None
    try:
        guard = t.py(c, t.guard_code())
        assert guard['new_root_unused']
        task = t.ps(c, "$t=Get-ScheduledTask -TaskName '" + TASK + "' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null -ne $t)}|ConvertTo-Json -Compress")
        assert not task['exists']
        staged = t.py(c, 'ROOT=' + repr(ROOT) + '\n' + "from pathlib import Path\nimport json\nR=Path(ROOT);assert not R.exists();R.mkdir();(R/'payload').mkdir();(R/'leases').mkdir();print(json.dumps(dict(new_root_created=True,no_GPU=True)))\n")
        save('PLANE_METADATA_V7_NEW_ROOT_ACTUAL.json', dict(epoch=time.time(), resource_guard=guard, staged=staged))
        sf = c.open_sftp()
        sf.get_channel().settimeout(60)
        with sf.open(ROOT + '/' + z.name, 'wx') as f:
            f.write(z.read_bytes())
            f.flush()
        code = """from pathlib import Path
import json,hashlib,zipfile,importlib.metadata as metadata,torch,time
R=Path(ROOT);P=R/'payload';S=Path(SHARED);z=R/ZIP
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==ZIP_SHA and not (R/'attempts'/CASE).exists()
with zipfile.ZipFile(z) as f:
 for n in f.namelist():
  dst=P/n;assert dst.resolve().is_relative_to(P.resolve())
  if n.endswith('/'):dst.mkdir(parents=True,exist_ok=True);continue
  assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb') as out:out.write(f.read(n))
m=json.loads((P/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json').read_bytes())
for row in m['package_files']:assert H(P/row['relative'])==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
stub=m['actual_primary_stub'];assert H(stub['actual_installed_stub_path'])==stub['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,value in sdk['versions'].items():
 if value is not None:assert metadata.version(name)==value,name
for row in sdk['files']:assert H(row['path'])==row['sha256'],row['path']
assert not torch.cuda.is_initialized()
positions=P/'FAILED_V6_FULL1500_FIRST_LAST_XY80_ACTUAL.json';assert H(positions)==m['source_positions']['sha256']
print(json.dumps(dict(epoch=time.time(),target_CPU_source_package_SDK_exact=True,no_GPU=True,no_PPO=True,manifest_sha256=H(P/'RETENTION_PLANE_METADATA_CPU_MANIFEST_V7.json'),source_positions_sha256=H(positions))))
"""
        prefix = 'ROOT=' + repr(ROOT) + '\nSHARED=' + repr(SHARED) + '\nZIP=' + repr(z.name) + '\nZIP_SHA=' + repr(H(z)) + '\nCASE=' + repr(CASE) + '\n'
        cpu = t.py(c, prefix + code)
        save('PLANE_METADATA_V7_TARGET_CPU_ACTUAL.json', cpu)
        fresh = t.py(c, t.guard_code())
        assert not fresh['new_root_unused']
        lease = dict(epoch=time.time(), case_id=CASE, target_host='10.24.4.249',
                     namespace=m['target_namespace'], GPU_lease_granted_by_root=True,
                     actual_shared_slot_idle_verified=True, actual_resource_boundary=fresh,
                     worker_sha256=H(P / 'retention_plane_metadata_worker_v7.py'),
                     shared_payload_target=SHARED,
                     source_positions_path=ROOT + '/payload/FAILED_V6_FULL1500_FIRST_LAST_XY80_ACTUAL.json',
                     source_positions_sha256=m['source_positions']['sha256'],
                     case_parameters=dict(num_envs=80, seed=20261002, requested_controls=0, headless=True, device='cuda:0'),
                     no_PPO=True, no_policy_or_checkpoint_read=True,
                     original_failed_V6_grade_unchanged=True)
        save('PLANE_METADATA_V7_ROOT_LEASE_INTENT_ACTUAL.json', lease)
        with sf.open(ROOT + '/leases/' + CASE + '.json', 'wx') as f:
            f.write(json.dumps(lease, indent=2).encode())
            f.flush()
        launch = """from pathlib import Path
import sys,subprocess,json,time,os,psutil
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/retention_plane_metadata_parent_v7.py'),'--lease',str(R/'leases'/(case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 child=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT)
 (R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=argv)))
 rc=child.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)))
sys.exit(rc)
""".replace('CASE', repr(CASE))
        script = D / 'demand_native_plane_metadata160_v7_once.py'
        assert not script.exists()
        compile(launch, str(script), 'exec')
        script.write_text(launch, encoding='utf8')
        with sf.open(ROOT + '/' + script.name, 'wx') as f:
            f.write(launch.encode())
            f.flush()
        setup = t.ps(c, "$ErrorActionPreference='Stop';$name='" + TASK + "';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '" + t.PY + "' -Argument '\"" + ROOT + '/' + script.name + "\"' -WorkingDirectory '" + ROOT + "';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $name;$t=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
        assert setup['triggers'] == 0
        save(receipt.name, dict(epoch=time.time(), lease=lease, task=setup, actual_result_pending=True, no_old_GPU_case_replayed=True))
        print(json.dumps(dict(new_metadata_dispatch=True, task=setup, requested_controls=0, PPO=False)))
    except BaseException:
        save('PLANE_METADATA_V7_ORIGINAL_DEPLOY_ERROR_' + str(time.time_ns()) + '.json', dict(error=traceback.format_exc(), unknown_outcome_readonly_recovery_required=True))
        raise
    finally:
        if sf:
            sf.close()
        t.close(c)

if __name__ == '__main__':
    main()
