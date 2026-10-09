"""Collect only completed E1 block2 evidence. No dispatch, GPU or ledger writes."""
from pathlib import Path
import base64, hashlib, json, os, shlex, sys, time, traceback

D=Path(__file__).resolve().parent; W=D.parent; R=D/'block2'
R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_REVIEWED_STABLE_20261009'
CENTRAL='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15'
def digest(b):return hashlib.sha256(b).hexdigest()
def save(path,b):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==b,('Do not overwrite evidence',str(path))
    else:path.write_bytes(b)
def main():
    assert not (R/'COLLECTED.json').exists(),'Already collected; use existing immutable evidence'
    for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
        secret,_=recover(name); assert secret,'Authorized task transport unavailable'
        os.environ[name]=secret
    n=connect(); w=connect_eval(); files=[]; cases={}
    try:
        with n.open_sftp() as nf,w.open_sftp() as wf:
            def get(remote,local):
                raw=nf.open(remote).read();save(R/local,raw)
                files.append(dict(source=remote,local=local,bytes=len(raw),sha256=digest(raw)))
                return json.loads(raw)
            passed=get(ROOT+'/reports/e1_gentle_stable_block2_PASSED.json','block2/PASSED.json')
            exited=get(ROOT+'/reports/e1_gentle_stable_block2_SAVED_EXIT.json','block2/SAVED_EXIT.json')
            assert passed==exited
            pub=get(ROOT+'/reports/E1_116-e1-gentle-b2_ASYNC_PUBLISHED.json','block2/ASYNC_PUBLISHED.json')
            freeze=get(ROOT+'/reports/SOURCE_FREEZE.json','block2/SOURCE_FREEZE.json')
            assert len(freeze['sha256'])==313
            run=passed['run']; ck=passed['checkpoint']; receipt=passed['own_PID_bound_receipt']
            assert pub['source']['sha256']==ck['sha256'] and ck['finite_tensors']==96
            assert receipt['checkpoint']==ck['path'] and receipt['pid']==passed['health']['pid']
            manifest=get(run+'/run_manifest.json','block2/run_manifest.json')
            rolling=get(run+'/rolling_source_freeze.json','block2/rolling_source_freeze.json')
            latest=get(run+'/latest_complete.json','block2/latest_complete.json')
            assert rolling['sha256']==manifest['source_map']==freeze['sha256'] and latest==receipt
            for name in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED','CHASSIS_PD_RESUME_STARTUP_VERIFIED','GAS_DAMPING_RESUME_STARTUP_VERIFIED','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED','ACTION_DELAY_RESUME_STARTUP_VERIFIED','CLOCK_TRAINING_HEALTH'):
                get(run+'/'+name+'.json','block2/'+name+'.json')
            # Recheck only static completed source/checkpoint/snapshots and unique settlement.
            code="""from pathlib import Path
import hashlib,json
root=Path(ROOT);run=Path(RUN);ck=Path(CK);j=lambda p:json.loads(p.read_text())
f=j(root/'reports/SOURCE_FREEZE.json')['sha256'];m=j(run/'run_manifest.json')
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in f.items())
assert all(hashlib.sha256((run/'e1_source_snapshot'/p).read_bytes()).hexdigest()==h for p,h in f.items())
assert all(hashlib.sha256((run/'src_snapshot'/p).read_bytes()).hexdigest()==h for p,h in m['src_sha256'].items())
sha=hashlib.sha256(ck.read_bytes()).hexdigest();budget=j(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
segments=[s for s in budget['completed_segments'] if s['pid']==PID]
assert len(segments)==1
print(json.dumps(dict(checkpoint_sha256=sha,source_count=len(f),snapshot_count=len(m['src_sha256']),unique_completed_segment=segments,canonical_total_seconds=budget['authorized_training_seconds'],budget_not_modified=True)))
"""
            code=code.replace('ROOT',repr(ROOT)).replace('RUN',repr(run)).replace('CK',repr(ck['path'])).replace('PID',str(receipt['pid']))
            _,out,err=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60)
            raw=out.read();error=err.read();assert out.channel.recv_exit_status()==0,(raw+error).decode(errors='replace')
            proof=json.loads(raw);assert proof['checkpoint_sha256']==ck['sha256'] and proof['snapshot_count']==57
            assert proof['unique_completed_segment']==passed['unique_completed_segment']
            save(R/'block2/STATIC_OWN_SOURCE_VERIFIED.json',json.dumps(proof,indent=2).encode())
            receipts={}
            for name in ('STARTED','STATE','ATTENTION','ADMITTED'):
                remote=WIN+'/E1_CURRICULUM_INTERFACE_WORKER_'+name+'.json'
                try:raw=wf.open(remote).read()
                except FileNotFoundError:receipts[name]=None;continue
                save(R/'evaluator'/('WORKER_'+name+'.json'),raw);receipts[name]=json.loads(raw)
            assert not receipts['ATTENTION']
            ps="$ErrorActionPreference='Stop';[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
            _,out,err=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45)
            raw=out.read();error=err.read();assert out.channel.recv_exit_status()==0,(raw+error).decode(errors='replace')
            processes=json.loads(raw)['processes']; started=receipts['STARTED']
            worker=next(p for p in processes if p['ProcessId']==started['pid'] and 'eval_worker_e1_curriculum_interface_review.py' in p['CommandLine'])
            assert abs(worker['creation_epoch']-started.get('creation_epoch',started['epoch']))<2
            source=wf.open(WIN+'/eval_worker_e1_curriculum_interface_review.py').read()
            save(R/'evaluator/ACTUAL_IDENTITY.json',json.dumps(dict(epoch=time.time(),worker=worker,processes=processes,source_sha256=digest(source)),indent=2).encode())
            for job in pub['jobs']:
                jid=job['job_id']; row={'manifest':job}; folder=R/'cases'/jid
                save(folder/'manifest.json',json.dumps(job,indent=2).encode())
                for name in ('probe.json','result.json'):
                    original=wf.open(WIN+'/jobs/'+jid+'/'+name).read()
                    returned=nf.open(CENTRAL+'/eval_results/'+jid+'/'+name).read()
                    assert original==returned,(jid,name,'bridge bytes differ')
                    save(folder/name,original);row[name[:-5]]=json.loads(original)
                    files.append(dict(source=WIN+'/jobs/'+jid+'/'+name,returned_source=CENTRAL+'/eval_results/'+jid+'/'+name,local=str(folder.relative_to(R)/name),bytes=len(original),sha256=digest(original),bridge_bytes_exact=True))
                result=row['result'];assert result['phase']=='complete' and result['exit_code']==0 and not result['errors'] and not result['error_files']
                if 'full_route_raw' in row['probe']:
                    rawinfo=row['probe']['full_route_raw'];path=folder/rawinfo['name']
                    original=WIN+'/jobs/'+jid+'/'+rawinfo['name']
                    # Download the already completed immutable original. No GPU re-run.
                    if not path.exists():wf.get(original,str(path))
                    raw=path.read_bytes();assert digest(raw)==rawinfo['sha256']
                    row['raw_SHA_exact']=True
                    files.append(dict(source=original,local=str(path.relative_to(R)),bytes=len(raw),sha256=digest(raw),large_artifact_SHA_only_in_Git=True))
                cases[jid]=row
            v=dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK2-MATCHED-20261009',passed=passed,publication=pub,cases=cases,files=files,worker_identity_verified=True,current_attention=None,no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0)
            save(R/'COLLECTED.json',json.dumps(v,indent=2).encode())
            print(json.dumps(dict(collected_complete_cases=len(cases),source=ck,source_count=313,snapshot_count=57,large_raw=[x for x in files if x.get('large_artifact_SHA_only_in_Git')],no_GPU_PPO_queue_or_canonical_write=True),ensure_ascii=True))
    finally:
        n.close();w.close()
        for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
    try:main()
    except Exception:
        error=dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK2-COLLECTOR-01',error=traceback.format_exc(),production_unchanged=True)
        save(R/'COLLECTOR_01_ERROR.json',json.dumps(error,indent=2).encode());raise
