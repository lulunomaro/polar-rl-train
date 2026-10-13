"""Single approved temporary GPU sequence, native lock, memory ceiling, save stop."""
from pathlib import Path
import json, os, time, subprocess, hashlib, msvcrt, psutil, traceback, sys, shutil
from temporary_memory_job import MemoryJob, hard_resident_limit
P = Path(__file__).resolve().parent
T = P.parent
R = T.parent
F = T / 'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def atomic(p, v):
    p = Path(p)
    q = p.with_suffix(p.suffix + '.partial')
    with q.open('wb') as f:
        f.write(json.dumps(v, indent=2).encode())
        f.flush()
        os.fsync(f.fileno())
    os.replace(q, p)

def ident(pid):
    try:
        p = psutil.Process(pid)
        return dict(pid=pid, created=p.create_time(), argv=p.cmdline(), cwd=p.cwd())
    except (psutil.Error, OSError):
        return None

def alive(row):
    if row is None:
        return False
    x = ident(row['pid'])
    return x is not None and x['created'] == row['created']

def main():
    assert os.name == 'nt' and Path(sys.executable).resolve() == R / 'env/python.exe'
    marker = T / 'SEQUENCE_ONCE_CONSUMED.json'
    assert not marker.exists()
    m = json.loads(F.read_bytes())
    assert m['num_envs'] == 768 and m['requested_memory_limit_bytes'] == 20000000000 and (m['soft_RSS_save_stop_bytes'] == 18000000000)
    assert m['root_review_actual']['human_new20GB_temporary_scope_authorization'] and m['seed'] == 20260928
    assert json.loads(Path(m['target_CPU_receipt']['path']).read_bytes())['passed'] and H(m['target_CPU_receipt']['path']) == m['target_CPU_receipt']['sha256']
    for row in m['sourcefreeze_files']:
        assert H(row['path']) == row['sha256'], row['path']
    need = m['resource_guards']
    ram = psutil.virtual_memory().available
    durable = shutil.disk_usage(T).free
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
    gpu = int(gpu.stdout.strip().splitlines()[0]) * 1024 * 1024
    assert ram >= need['RAM_available_bytes'] and durable >= need['durable_free_bytes'] and (gpu >= need['GPU_free_bytes'])
    out = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout
    other = []
    for line in out.splitlines():
        fields = line.split(',', 1)
        if len(fields) == 2 and fields[0].strip().isdigit():
            if any((x in fields[1].lower() for x in ('python', 'kit.exe'))):
                other.append(line)
    assert not other, other
    lockpath = R / 'WINDOWS4090_GPU_EXCLUSIVE.lock'
    lock = lockpath.open('a+b')
    if lockpath.stat().st_size == 0:
        lock.write(b'0')
        lock.flush()
        os.fsync(lock.fileno())
    lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    job = MemoryJob(m['virtual_commit_limit_bytes'])
    job.assign(os.getpid())
    hard_resident_limit(os.getpid(), 134217728)
    atomic(marker, dict(epoch=time.time(), parent=ident(os.getpid()), approved_scope='Windows temporary2048 left repair', manifest_sha256=H(F), no_original20k_launch=True, job_commit_hardlimit_bytes=job.limit, no_kill_on_close=True, shared_native_lock=str(lockpath), initial_resources=dict(RAM_available_bytes=ram, GPU_free_bytes=gpu, durable_free_bytes=durable)))
    source = dict(m['source'])
    phase = None
    progress = False
    try:
        for phase in ('native', 'fullrestore', 'train'):
            A = T / 'attempts' / ('temporary2048_' + phase + '_v1')
            assert not A.exists()
            A.mkdir()
            O = A / 'output'
            O.mkdir()
            snap = A / 'source_snapshot'
            snap.mkdir()
            freezes = []
            for i, row in enumerate(m['sourcefreeze_files']):
                q = snap / (str(i) + '_' + Path(row['path']).name)
                shutil.copy2(row['path'], q)
                assert H(q) == row['sha256']
                freezes.append(dict(source=row['path'], snapshot=str(q), sha256=H(q)))
            atomic(A / 'SOURCEFREEZE_ACTUAL.json', dict(epoch=time.time(), files=freezes, source=source, manifest_sha256=H(F)))
            stage = dict(m, source=source, sourcefreeze_files=m['sourcefreeze_files'])
            mf = A / 'STAGE_MANIFEST_GRANTED.json'
            atomic(mf, stage)
            stop = A / 'STOP_AFTER_SAVE'
            started = time.time()
            known = {}
            peakrss = 0
            peakhard = job.peak()
            env = os.environ.copy()
            env['MOD4_WINDOWS_GPU_LOCK_PARENT_PID'] = str(os.getpid())
            env['MOD4_WINDOWS_PARENT_START_EPOCH'] = str(started)
            cmd = [sys.executable, str(P / 'temporary_worker.py'), '--runtime-root', str(T / 'runtime2048'), '--manifest', str(mf), '--source-checkpoint', source['path'], '--source-sha', source['sha256'], '--output', str(O), '--stop-after-save', str(stop), '--mode', phase, '--train-seconds', '3600', '--probe-controls', '120', '--headless', '--device', 'cuda:0']
            logfile = (A / 'worker_stdout.log').open('wb')
            child = subprocess.Popen(cmd, cwd=P, env=env, stdout=logfile, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            hard_resident_limit(child.pid, 19500000000)
            ci = ident(child.pid)
            assert ci
            known[ci['pid']] = ci
            atomic(A / 'DISPATCH_RECEIPT.json', dict(epoch=time.time(), parent=ident(os.getpid()), child=ci, argv=cmd, phase=phase, source=source, shared_native_OSlock_held=True, job_commit_limit_bytes=job.limit, temporary_num_envs=10 if phase == 'sdk' else 768))
            lastwrite = 0
            resource_reject = False
            while True:
                if child.poll() is None:
                    try:
                        for x in psutil.Process(child.pid).children(recursive=True):
                            row = ident(x.pid)
                            if row:
                                known[row['pid']] = row
                    except (psutil.Error, OSError):
                        pass
                live = [x for x in known.values() if alive(x)]
                rss = psutil.Process(os.getpid()).memory_info().rss
                for x in live:
                    try:
                        rss += psutil.Process(x['pid']).memory_info().rss
                    except (psutil.Error, OSError):
                        pass
                peakrss = max(peakrss, rss)
                peakhard = max(peakhard, job.peak())
                if phase == 'train' and (time.time() - started >= 3600 or rss >= m['soft_RSS_save_stop_bytes'] or peakhard >= 60000000000) and (not stop.exists()):
                    atomic(stop, dict(epoch=time.time(), reason='memory_softlimit' if rss >= 18000000000 or peakhard >= 60000000000 else 'bounded3600s', RSS_bytes=rss, job_peak_commit_bytes=peakhard, no_kill=True))
                if phase != 'train' and peakrss * 1.25 + 536870912 >= 20000000000 and (not stop.exists()):
                    atomic(stop, dict(epoch=time.time(), reason='actual_native_initial_peak_headroom_insufficient', peak_RSS_bytes=peakrss, original_25percent_plus512MiB_margin_unchanged=True, no_PPO=True, no_kill=True))
                if phase != 'train' and (rss >= 19000000000 or peakhard >= 62000000000):
                    resource_reject = True
                if time.time() - lastwrite >= 15 or child.poll() is not None:
                    lastwrite = time.time()
                    row = dict(epoch=lastwrite, parent=ident(os.getpid()), child=ident(child.pid), own_alive_processes=live, phase=phase, RSS_bytes=rss, peak_RSS_bytes=peakrss, job_peak_commit_bytes=peakhard, job_commit_limit_bytes=job.limit, STOP_AFTER_SAVE=stop.exists(), shared_OSlock_held=True)
                    atomic(A / 'GUARDIAN_CURRENT.json', row)
                    atomic(T / 'SEQUENCE_CURRENT_ACTUAL.json', row)
                    with (A / 'guardian_history.ndjson').open('ab') as f:
                        f.write(json.dumps(row).encode() + b'\n')
                        f.flush()
                        os.fsync(f.fileno())
                if child.poll() is not None and (not live):
                    break
                time.sleep(2)
            logfile.close()
            expected = 'WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json' if phase == 'train' else 'FULLRESTORE_PHYSICAL_PROBE_PASSED.json' if phase == 'fullrestore' else 'PROBE_COMPLETE.json'
            final = json.loads((O / expected).read_bytes()) if (O / expected).exists() else None
            passed = child.returncode == 0 and final is not None and final.get('passed') and (not (O / 'ORIGINAL_ERROR.json').exists()) and (peakrss < 20000000000) and (peakhard <= job.limit) and (not resource_reject)
            receipt = dict(epoch=time.time(), passed=bool(passed), parent=ident(os.getpid()), child=ci, phase=phase, worker_exitcode=child.returncode, own_child_and_descendants_actual_absent=True, parent_retains_lock_across_sequence_not_falsely_exited=True, expected_complete=expected, peak_RSS_bytes=peakrss, job_peak_commit_bytes=peakhard, job_limit_bytes=job.limit, actual_parent_phase_load_learn_save_exit_seconds=time.time() - started, no_PPO=phase != 'train', canonical_pending=phase == 'train', no_canonical_write_or_second_budget=True, raw_original_failure_retained=True)
            atomic(A / 'EXIT_RECEIPT.json', receipt)
            assert passed, receipt
            if phase != 'train':
                contract = final['complete_physical_command_DR_contract']
                sub = contract['actual_substep_readback_V6']
                assert contract['actual_ground_query_error_m'] <= 1e-06 and contract['actual_height_reward_formula_error'] <= 1e-06 and sub['passed'] and sub['motor_torque_speed_bounds_exact'] and sub['all_env_every_substep_checked']
                assert sub['contact_integral_mean_error_N'] <= 0.1 and sub['COM_world_formula_max_error_m'] < 1e-05 and (sub['COM_link_point_velocity_max_error_m_s'] <= 0.001)
                assert final['actual_callbacks'] == (300 if phase == 'sdk' else 144 if phase == 'native' else 120) * 4
                assert peakrss * 1.25 + 536870912 < 20000000000 and peakhard + 768 * 256 * 24 * 16 * 4 + 2147483648 + 33554432 < 60000000000, 'newscope actualpeak headroom insufficient; no formal launch'
            if phase == 'fullrestore':
                latest = final['latest']
                assert latest['finite_floating_tensors'] == 107 and latest['perenv_tensor_fields'] == 99
                source = dict(path=latest['path'], sha256=latest['sha256'], bytes=latest['bytes'])
                assert H(source['path']) == source['sha256']
                atomic(T / 'OWN_REPAIRED_FULLRESTORE_SOURCE_ACTUAL.json', dict(epoch=time.time(), source=source, phase_EXIT=receipt, no_PPO=True, not_fullroute_qualified=True))
        atomic(T / 'SEQUENCE_FINAL_ACTUAL.json', dict(epoch=time.time(), passed=True, formal_finished=True, no_50mm_qualification_claimed=True, own_all_children_actual_exit=True, global_lock_release_follows=True, canonical_reconciliation_pending=True))
    except BaseException:
        atomic(T / 'SEQUENCE_ORIGINAL_ERROR.json', dict(epoch=time.time(), phase=phase, error=traceback.format_exc(), original_failure_not_relabelled=True, no_automatic_replay_kill_or_oldscope_hotpatch=True))
        raise
    finally:
        if 'child' in locals():
            while child.poll() is None or any((alive(x) for x in known.values())):
                time.sleep(2)
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
        lock.close()
        job.close()
        atomic(T / 'SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json', dict(epoch=time.time(), parent=ident(os.getpid()), all_own_descendants_actual_absent=True, OSlock_released=True, persistent_lock_not_deleted=True))
if __name__ == '__main__':
    main()
