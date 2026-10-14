"""Readonly single metadata-stage completion collection. No GPU or dispatcher import."""
from pathlib import Path
import hashlib, json, sys, time, traceback, zipfile

D = Path(__file__).resolve().parent
R = D / 'reports'
sys.path.insert(0, str(D.parent / 'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
ROOT = 'D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_QUERY_METADATA_V7_20261014'
CASE = 'native_plane_metadata160_zero_requested_controls_v7'
t.ROOT = ROOT
CODE = r'''
from pathlib import Path
import json,hashlib,time,psutil,msvcrt,zipfile
R=Path(ROOT);A=R/'attempts'/CASE;O=A/'output'
J=lambda p:json.loads(p.read_bytes()) if p.exists() else None
top={n:J(R/(CASE+'_'+n+'.json')) for n in ('START_INTENT','PARENT_PID','LAUNCH_EXIT')}
states={n:J(A/n) for n in ('DISPATCH_RECEIPT.json','GUARDIAN_CURRENT.json','PARENT_EXIT_RECEIPT.json')}
outputs={n:J(O/n) for n in ('STARTED.json','COMPLETE_ACTUAL.json','ORIGINAL_ERROR.json','EXIT_NATURAL.json')}
identities=[]
for row in (top['START_INTENT'],top['PARENT_PID'],states['DISPATCH_RECEIPT.json']):
 if not row:continue
 for pk,ck in (('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')):
  if pk not in row:continue
  try:
   p=psutil.Process(row[pk]);identities.append(dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),cwd=p.cwd(),expected_creation=row.get(ck),actual_alive=True))
  except psutil.NoSuchProcess:identities.append(dict(pid=row[pk],actual_alive=False))
free=False
try:
 with Path('D:/MOD4_async_eval/worker.lock').open('r+b') as f:
  f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 free=True
except OSError:pass
complete=states['PARENT_EXIT_RECEIPT.json'] is not None
collection=None;files=[]
if complete:
 assert all(not v['actual_alive'] for v in identities) and free
 z=R/(CASE+'_ACTUAL_BOUNDARY_COLLECTION.zip');assert not z.exists()
 candidates=sorted(p for p in A.rglob('*') if p.is_file())
 candidates+=sorted(p for p in R.iterdir() if p.is_file() and p.suffix!='.zip')
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED) as archive:
  for p in candidates:
   b=p.read_bytes();relative=p.relative_to(R).as_posix();archive.writestr(relative,b)
   files.append(dict(path=str(p),relative=relative,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 collection=dict(path=str(z),bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest())
log=A/'worker.log';tail=log.read_bytes()[-2400:].decode(errors='replace') if log.exists() else ''
print(json.dumps(dict(epoch=time.time(),root=str(R),case=CASE,top=top,states=states,outputs=outputs,
 actual_PID_identities=identities,shared_OS_lock_free=free,actual_parent_absent=all(not v['actual_alive'] for v in identities),
 actual_child_absent=all(not v['actual_alive'] for v in identities),complete=complete,collection=collection,files=files,worker_tail=tail,readonly=True)))
'''

def main():
    stamp = str(time.time_ns())
    boundary_path = R / 'PLANE_METADATA_V7_INDEPENDENT_BOUNDARY.json'
    assert not boundary_path.exists()
    c = t.connect()
    sf = None
    try:
        v = t.py(c, 'ROOT=' + repr(ROOT) + '\nCASE=' + repr(CASE) + '\n' + CODE, 60)
        if v['complete']:
            dest = D / 'metadata_actual_collections' / stamp
            dest.mkdir(parents=True)
            z = dest / 'ACTUAL_BOUNDARY_COLLECTION.zip'
            sf = c.open_sftp()
            sf.get_channel().settimeout(60)
            sf.get(v['collection']['path'].replace('\\', '/'), str(z), max_concurrent_prefetch_requests=16)
            assert z.stat().st_size == v['collection']['bytes'] and hashlib.sha256(z.read_bytes()).hexdigest() == v['collection']['sha256']
            with zipfile.ZipFile(z) as f:
                for name in f.namelist():
                    assert (dest / name).resolve().is_relative_to(dest.resolve())
                f.extractall(dest)
            for row in v['files']:
                p = dest / row['relative']
                assert p.stat().st_size == row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
                row['local_path'] = str(p)
                row['two_host_byteSHA_exact'] = True
            boundary_path.write_text(json.dumps({k: v[k] for k in ('epoch', 'actual_parent_absent', 'actual_child_absent', 'shared_OS_lock_free', 'actual_PID_identities', 'states', 'outputs')}, indent=2), encoding='utf8')
            v['local_attempt'] = str(dest / 'attempts' / CASE)
            v['local_boundary'] = str(boundary_path)
        out = R / ('PLANE_METADATA_V7_CURRENT_ACTUAL_' + stamp + '.json')
        out.write_text(json.dumps(v, indent=2), encoding='utf8')
        print(json.dumps(dict(report=str(out), complete=v['complete'], parent_exit=v['states']['PARENT_EXIT_RECEIPT.json'], original_error=v['outputs']['ORIGINAL_ERROR.json'], natural=v['outputs']['EXIT_NATURAL.json'] is not None, data_complete=v['outputs']['COMPLETE_ACTUAL.json'] is not None, boundary=v.get('local_boundary'), attempt=v.get('local_attempt'), lock_free=v['shared_OS_lock_free'], worker_tail=v['worker_tail'])))
    except BaseException:
        (R / ('PLANE_METADATA_V7_ORIGINAL_COLLECTOR_ERROR_' + stamp + '.json')).write_text(json.dumps(dict(error=traceback.format_exc(), readonly=True, unknown_outcome_requires_readonly_recovery=True), indent=2), encoding='utf8')
        raise
    finally:
        if sf:
            sf.close()
        t.close(c)

if __name__ == '__main__':
    main()
