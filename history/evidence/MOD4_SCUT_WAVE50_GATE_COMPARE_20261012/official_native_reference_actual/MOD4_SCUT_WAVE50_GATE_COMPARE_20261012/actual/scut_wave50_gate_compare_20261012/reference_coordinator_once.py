"""Human-requested oneoff reference replay; borrow only an actually idle owned slot."""
from pathlib import Path
import json,time,subprocess,hashlib,os,base64,traceback,msvcrt
D=Path(__file__).resolve().parent;W=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');TASK='MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review';PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'
def write(p,v):
    assert not p.exists(),p;p.write_text(json.dumps(v,indent=2),encoding='utf8')
def ps(code):
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(code.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
    assert r.returncode==0,r.stderr;return json.loads(r.stdout) if r.stdout.strip() else None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (D/'REFERENCE_COORDINATOR_STARTED.json').exists()
write(D/'REFERENCE_COORDINATOR_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),new_human_requested_SCUT_frozen_reference_only=True,old_probe_and_worker_once_not_replayed=True,no_4090_PPO_or_canonical_authority=True))
assert json.loads((D/'TARGET_CPU_ADMITTED.json').read_text())['passed']
assert sha(W/'eval_worker_closure2500.py')=='0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1'
before={p.name:sha(p) for p in (W/'eval_worker_closure2500.py',W/'eval_worker_e1_wave50_query_review.py')};parked=False;lock=None;active=None
try:
    deadline=time.time()+2400
    while True:
        started=json.loads((W/'E1_WAVE50_QUERY_REVIEW_WORKER_STARTED.json').read_text());state=json.loads((W/'E1_WAVE50_QUERY_REVIEW_WORKER_STATE.json').read_text())
        assert not (W/'E1_WAVE50_QUERY_REVIEW_WORKER_ATTENTION.json').exists()
        pending=[j for j in state['jobs'] if not (W/'jobs'/j/'complete.json').exists()]
        pid=started['pid']
        identity=ps("$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$all=@(Get-CimInstance Win32_Process);[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=@($all|Where-Object {$_.ParentProcessId -eq "+str(pid)+"}|Select-Object ProcessId,CommandLine);task=(Get-ScheduledTask -TaskName '"+TASK+"').Actions|Select-Object Execute,Arguments}|ConvertTo-Json -Depth 6 -Compress")
        assert identity['process'] and abs(identity['process']['creation_epoch']-started['epoch'])<2 and 'eval_worker_e1_wave50_query_review.py' in identity['process']['CommandLine']
        assert TASK.split('v15_')[1] in identity['task']['Arguments']
        if not pending and not identity['children'] and state['phase']=='polling' and time.time()-state['epoch']<90:break
        if time.time()>deadline:raise RuntimeError('Existing planned evaluations still active; no worker/GPU takeover attempted.')
        (D/'WAITING_FOR_OWNED_SLOT.json').write_text(json.dumps(dict(epoch=time.time(),pending=pending,children=identity['children'],no_worker_or_GPU_mutation=True),indent=2));time.sleep(15)
    write(D/'IDLE_WORKER_BORROW_ACTUAL.json',dict(epoch=time.time(),identity=identity,source_SHA=before,all_current_queue_jobs_completed=True,healthy_worker_idle_no_GPU_children=True,reason='Latest direct human explicitly requests an original-SCUT reference on3060; existing pinned MOD4 asset guard cannot honestly execute a SCUT robot. Reversible oneoff idle demand-slot borrow, restore same unchanged worker source after own reference.',no_training_or_old_eval_replay=True))
    ps("Stop-ScheduledTask -TaskName '"+TASK+"'");parked=True
    for _ in range(40):
        q=ps("@(Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"')|Select-Object ProcessId,CommandLine|ConvertTo-Json -Compress")
        if not q:break
        time.sleep(.25)
    else:raise RuntimeError('Idle demand worker did not release its own slot; no probe launched.')
    lock=(W.parent/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    write(D/'SHARED_GPU_LOCK_ACTUAL_ACQUIRED.json',dict(epoch=time.time(),path=str(W.parent/'worker.lock'),actual_msvcrt_exclusive=True,no_competing_GPU_child=True))
    for name in ('2026-07-23_16-23-21','2026-07-30_09-16-27'):
        folder=D/'runs'/name;folder.mkdir(parents=True);assert not (folder/'ACTIVE.json').exists()
        argv=[PY,'-X','utf8',str(D/'scut_wave50_placement_reviewed_probe.py'),'--headless','--device','cuda:0','--model_name',name,'--output',str(folder/'probe.json'),'--steps','750','--num_envs','80']
        env={k:v for k,v in os.environ.items() if not k.startswith('RM_')};env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',TMP=str(D/'cache'),TEMP=str(D/'cache'))
        (D/'cache').mkdir(exist_ok=True)
        with (folder/'probe.log').open('xb') as f:
            active=subprocess.Popen(argv,cwd=D/'original',env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
            write(folder/'ACTIVE.json',dict(epoch=time.time(),pid=active.pid,argv=argv,probe_SHA=sha(D/'scut_wave50_placement_reviewed_probe.py'),original_model=name,no_learning=True,shared_OS_GPU_lock_held=True))
            rc=active.wait();active=None
        errors=list(folder.glob('*.error.txt'));result=json.loads((folder/'probe.json').read_text()) if (folder/'probe.json').exists() else None
        write(folder/'RESULT.json',dict(epoch=time.time(),exit_code=rc,result_present=result is not None,error_files=[p.name for p in errors],phase='complete' if rc==0 and result and not errors else 'retained_failed',all_saved_files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file()]))
        if rc or errors or result is None:raise RuntimeError('Independent SCUT reference failed; original error/raw preserved, no automatic replay or second model launch.')
    write(D/'REFERENCE_ALL_COMPLETE.json',dict(epoch=time.time(),two_original_models_complete=True,no_learning=True,no_training_budget_write=True))
except BaseException:
    write(D/'REFERENCE_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_GPU_job_replay=True,own_child_pid=active.pid if active else None));raise
finally:
    # Never release a GPU slot while this coordinator still has an active child.
    if active is not None:active.wait()
    if lock:
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
    if parked:
        assert all(sha(W/n)==h for n,h in before.items())
        ps("Start-ScheduledTask -TaskName '"+TASK+"'")
        write(D/'UNCHANGED_WORKER_RESTORE_REQUESTED.json',dict(epoch=time.time(),task=TASK,same_worker_and_baseguard_source_SHA_exact=before,original_queue_results_jobs_preserved=True,no_old_evaluation_relaunch=True))
