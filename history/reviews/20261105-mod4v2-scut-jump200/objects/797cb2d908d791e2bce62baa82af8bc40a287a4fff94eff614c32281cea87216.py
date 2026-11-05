"""Fresh local gate, one repaired evaluator, complete evidence and pose return."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, time, traceback

N = Path(__file__).resolve().parent
A = N/'attempt03'; R = A/'eval_mesh01/reports'
R.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('v2_eval_mesh_control', N/'control.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.REPORTS = R
read = m.read
def put(name, value):
    with (R/name).open('x', encoding='utf8') as stream: json.dump(value, stream, indent=2)

def main():
    put('CONTROLLER_ONCE.json', dict(epoch=time.time(), PID=os.getpid(), repaired_evaluation_only=True))
    while time.time() < args.not_before:
        time.sleep(min(10, args.not_before-time.time()))
    gate = m.local(); started = time.time()
    while any(row['ProcessId'] != os.getpid() for row in gate.local_rows()):
        assert time.time()-started < 10800, 'Local controller remains busy; no network admission'
        time.sleep(10)
    plan = read(A/'PLAN.json'); final = read(A/'reports/POSTROUND_FULL_RETURNED.json')['files']['production/FINAL.json']
    job = plan['remote_root']; remote = job+'/eval_mesh01'
    assert not list((A/'eval_mesh01/reports').rglob('LAUNCH_ONCE.json')), 'Evaluator launch already consumed'
    checkpoint = final['checkpoint']
    cpu = read(A/'reports/MESH_BINDING_CPU.json'); assert cpu['passed']
    sdk = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut/sdk.py')
    rows = [('overlay/sdk.py', sdk.read_bytes()), ('owner_eval.py', (N/'eval_mesh_owner.py').read_bytes())]
    evalplan = dict(closed_root=job, GPU_UUID=plan['GPU_UUID'], checkpoint=checkpoint,
        repair='Synchronize exported MESH after shared configure selects actual jump200 mesh',
        no_training_replay=True, optimizer_operations=0, ledger_writes=0)
    rows.append(('PLAN.json', json.dumps(evalplan, indent=2).encode()))
    manifest = [dict(relative=name, bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()) for name, raw in rows]
    rows.append(('INSTALL_MANIFEST.json', json.dumps(manifest, indent=2).encode()))
    put('SOURCE_FROZEN.json', dict(epoch=time.time(), files=manifest, CPU=cpu,
        source_checkpoint=checkpoint, original_evaluation_error_preserved=True))
    with gate.connection('MOD4V2_EVAL_MESH01') as (client, d):
        before = d.code(client, d.PY72, m.READ_RESOURCE, {}, timeout=45)
        put('FRESH_RESOURCE_ACTUAL.json', before)
        assert before['active'] is None and all(before['locks'].values()), 'Original canonical/locks busy'
        assert before['remaining'] > 86412.86069250107+3900
        assert before['ram'] > 64*1024**3 and before['disk'] > 50*1024**3
        for line in before['gpu'].splitlines():
            gpu = [s.strip() for s in line.split(',')]
            if gpu[1] == plan['GPU_UUID']:
                assert int(gpu[4]) > 15669 and gpu[1] not in before['apps']
                break
        else: raise RuntimeError('Original GPU not present')
        prepare = "from pathlib import Path;import json;p=Path(v['root']);p.mkdir(exist_ok=False);(p/'overlay').mkdir();print(json.dumps(dict(created=str(p))))"
        d.code(client, d.PY72, prepare, dict(root=remote), timeout=30)
        sf = client.open_sftp()
        try:
            for name, raw in rows:
                with sf.file(remote+'/'+name, 'wx') as stream: stream.write(raw); stream.flush()
        finally: sf.close()
        put('LAUNCH_ONCE.json', dict(epoch=time.time(), root=remote, model_SHA=checkpoint['SHA']))
        start = '''from pathlib import Path
import subprocess,json,psutil,time
r=Path(v['root'])
with (r/'OWNER.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(r/'owner_eval.py')],cwd=r,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 q=psutil.Process(p.pid)
 print(json.dumps(dict(epoch=time.time(),pid=p.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline())))'''
        owner = d.code(client, d.PY72, start, dict(root=remote), timeout=30)
        put('OWNER_LAUNCH.json', owner); print(json.dumps(dict(owner=owner)), flush=True)
        for tick in range(90):
            code = '''from pathlib import Path
import hashlib,json,psutil,time
r=Path(v['root']);files={}
for name in ['GPU_ADMISSION.json','WORKER_IDENTITY.json','WORKER_WAITED.json','ERROR.json','RELEASE.json','evaluation/NATIVE_STARTUP.json','evaluation/RESULT.json','evaluation/ALL80.json','evaluation/CONTROL_CURVES.json','evaluation/ERROR.json','evaluation/APP_CLOSE_INTENT.json']:
 p=r/name
 if p.is_file():
  try:files[name]=json.loads(p.read_bytes())
  except json.JSONDecodeError:pass
if 'RELEASE.json' in files:
 for name in ['OWNER.log','WORKER.log']:
  p=r/name
  if p.is_file():
   raw=p.read_bytes();files[name]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
alive=psutil.pid_exists(v['pid']) and psutil.Process(v['pid']).create_time()==v['creation']
print(json.dumps(dict(epoch=time.time(),files=files,exact_owner_alive=alive)))'''
            result = d.code(client, d.PY72, code, dict(root=remote, **owner), timeout=45)
            if 'RELEASE.json' in result['files'] and not result['exact_owner_alive']: break
            if tick % 6 == 0: print(json.dumps(dict(wait=tick, files=list(result['files']))), flush=True)
            time.sleep(10)
        else:
            put('PENDING.json', result); raise RuntimeError('Original evaluator still responsible; do not relaunch')
        put('FULL_RETURNED.json', result)
        files = result['files']; value = files.get('evaluation/RESULT.json')
        assert value and not files['RELEASE.json']['error'] and value['passed_execution'], 'Repaired evaluation failed'
        target = A/'eval_mesh01/evaluation'; target.mkdir(exist_ok=False)
        sf = client.open_sftp(); transfers = []
        try:
            for key in ['all80_manifold', 'actual_poses']:
                row = value[key]; path = target/Path(row['path']).name
                sf.get(row['path'], str(path))
                with path.open('rb') as stream: digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                assert path.stat().st_size == row['bytes'] and digest == row['SHA']
                transfers.append(dict(row, local_path=str(path), SHA_verified=True))
        finally: sf.close()
        put('FORMAL_TRANSFERS.json', dict(epoch=time.time(), files=transfers, model_reads=0, physics=0))
    put('COMPLETED.json', dict(epoch=time.time(), actual_result=value, release=files['RELEASE.json'],
        actual_visual_review_pending=True))
    print(json.dumps(dict(result=value, release=files['RELEASE.json'])), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume-admission', action='store_true')
    parser.add_argument('--not-before', type=float, default=0.)
    args = parser.parse_args()
    if args.resume_admission:
        assert (R/'FRESH_RESOURCE_ACTUAL.json').exists()
        assert not list(R.rglob('LAUNCH_ONCE.json'))
        R = R/'admission_resume01'; R.mkdir(exist_ok=False)
        m.REPORTS = R
    try: main()
    except BaseException:
        put('CONTROL_ERROR_'+str(time.time_ns())+'.json', dict(epoch=time.time(), error=traceback.format_exc()))
        raise
