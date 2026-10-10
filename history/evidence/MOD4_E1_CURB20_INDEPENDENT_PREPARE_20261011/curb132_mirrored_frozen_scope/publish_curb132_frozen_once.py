"""Publish one new independent CURB frozen scope to the unchanged healthy worker."""
from curb_io import *
import ast, base64, traceback

def worker_actual(w,wf):
    try:attention=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
    except FileNotFoundError:attention=None
    assert attention is None,attention
    source=wf.open(WIN+'/eval_worker_e1_g3_package_review.py').read()
    assert source==(W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/eval_worker_e1_g3_package_review.py').read_bytes()
    base=wf.open(WIN+'/eval_worker_closure2500.py').read()
    assert any(isinstance(x,ast.Assert) and "manifest['steps'] in [300, 1500]" in ast.unparse(x) for x in ast.walk(ast.parse(base.decode())))
    started=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json').read())
    ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
    _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    procs=json.loads(raw)['rows']
    own=[p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_g3_package_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2]
    assert len(own)==1
    return dict(worker=own,processes=procs,source_SHA=H(source),base_SHA=H(base),attention=None,healthy_worker_not_restarted=True)

def main():
    save('CURB132_PUBLISH_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-MIRRORED-FROZEN-PUBLISH-01',once=True,no_learning=True))
    prepared=json.loads((R/'CURB_FROZEN_PREPARED.json').read_bytes())
    pkg=prepared['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
    n,w=connect_both()
    try:
        authority=boundary(n)
        with n.open_sftp() as nf,w.open_sftp() as wf:
            actual=worker_actual(w,wf)
            budget=nf.open(B).read();assert H(budget)==authority['canonical_SHA']
            job=prepared['jobs'][0];jid=job['job_id']
            assert jid+'.json' not in nf.listdir(E+'/eval_queue') and jid not in wf.listdir(WIN+'/jobs')
            remote=job['artifacts']['runtime']['path'];assert Path(remote).name not in nf.listdir(E+'/artifacts')
            cp=job['artifacts']['checkpoint'];raw=nf.open(cp['path']).read()
            assert len(raw)==17615538==cp['bytes'] and H(raw)==SHA==cp['sha256']
            approval=nf.open(E+'/reports/MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json').read()
            job.update(published_epoch=time.time(),revision004_approval_SHA=H(approval),
                frozen_only_source_fullstate_not_restored=True,previous_Wave_candidate_not_selected=True)
            # Only artifact delivery and one new frozen queue item are mutated.
            nf.put(pkg['path'],remote+'.partial')
            assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
            raw=json.dumps(job,indent=2).encode();path=E+'/eval_queue/'+jid+'.json'
            with nf.open(path+'.partial','wbx') as f:f.write(raw)
            assert nf.open(path+'.partial').read()==raw;nf.rename(path+'.partial',path)
            assert nf.open(path).read()==raw and nf.open(B).read()==budget
            save('CURB132_PUBLISHED.json',dict(epoch=time.time(),trial_id='E1-CURB20-MIRRORED-FROZEN-PUBLISH-01',
                jobs=[job],actual_authority=authority,actual_worker=actual,package=pkg,
                canonical_SHA=H(budget),canonical_bytes_preserved=True,no_learning_or_4090_launch=True,
                complete_results_pending_not_passed=True,new_budget_seconds=0))
            print(json.dumps(dict(job_id=jid,source_SHA=SHA,package_SHA=pkg['sha256'],worker=actual['worker'],
                published=True,actual_completion_pending=True,no_learning=True,canonical_preserved=True)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB132_PUBLISH_ERROR.json',dict(epoch=time.time(),trial_id='E1-CURB20-MIRRORED-FROZEN-PUBLISH-01',error=traceback.format_exc(),original_partial_retained=True,do_not_blind_retry=True));raise
