"""Sequential authorized GPU jobs and independent CPU checkpoint screening."""
from nav_common import HERE,PYTHON,put,sha256,donor_imports
import json
import shutil
import subprocess
import time
from pathlib import Path
donor_imports()
from remote_nav4d import ROOT,collect
from remote_e0 import connect

def run_remote(*args):
    result=subprocess.run([str(PYTHON),'-B',str(HERE/'remote_nav4d.py'),*args],cwd=HERE,capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(result.stdout,flush=True)
    if result.returncode:raise RuntimeError(result.stderr)

def remote_snapshot(job):
    result={}
    with connect('host72') as ssh,ssh.open_sftp() as sftp:
        for name in ('LATEST.json','PROBE.json','SAFE_CLOSED.json','ERROR.txt'):
            try:
                with sftp.open(str(ROOT/job/name)) as f:
                    raw=f.read().decode('utf-8');result[name]=raw if name.endswith('.txt') else json.loads(raw)
            except FileNotFoundError:pass
        try:
            with sftp.open(str(ROOT/(job+'_EXIT.json'))) as f:result['EXIT']=json.load(f)
        except FileNotFoundError:pass
    return result

def wait_closed(job):
    start=time.monotonic();last=-1
    while time.monotonic()-start<3300:
        snap=remote_snapshot(job);latest=snap.get('LATEST.json',{})
        key=latest.get('iteration',latest.get('steps',0))
        if key!=last:
            print(job,json.dumps({k:latest[k] for k in ('iteration','steps','elapsed_s','ppo_updates') if k in latest}),flush=True);last=key
        if 'EXIT' in snap:
            with connect('host72') as ssh:collect(ssh,job)
            if snap.get('ERROR.txt') or snap.get('SAFE_CLOSED.json',{}).get('error'):
                raise RuntimeError(f'{job}: '+snap.get('ERROR.txt',str(snap['SAFE_CLOSED.json'])))
            assert snap['EXIT']['exit_code']==0 and not snap['EXIT']['hard_kill'] and snap['EXIT']['own_gpu_process_released']
            assert snap.get('SAFE_CLOSED.json',{}).get('scene_closed')
            if 'PROBE.json' in snap:assert snap['PROBE.json']['passed']
            return snap
        time.sleep(15.)
    raise TimeoutError(job)

def screen_stairs(job):
    folder=HERE/'evidence'/job
    candidates=sorted(folder.glob('model_*.pt'));reports=[]
    for path in candidates:
        out=HERE/'evidence/checkpoint_screens/stair'/path.stem
        out.mkdir(parents=True,exist_ok=True)
        with (out/'eval.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(PYTHON),'-B',str(HERE/'eval_stair_nav4d.py'),'--checkpoint',str(path),'--profile','full',
                            '--workers','6','--out',str(out)],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,check=True)
        r=json.loads((out/'SUMMARY.json').read_text(encoding='utf-8'));r['screen_folder']=str(out.relative_to(HERE));reports.append(r)
        print('STAIR_SCREEN',path.name,r['passed'],r['total'],r['by_course'],flush=True)
    def score(r):
        primary=[c for c in r['cases'] if c['course']=='suite_rmul2027' and c['lift']==.2]
        single=[c for c in r['cases'] if c['course'] in ('step_20','oblique_20','oblique_20_negative')]
        rmuc=r['by_course']['suite_rmuc2027']
        return (r['single200_preserved'],sum(c['passed'] for c in primary)/max(1,len(primary)),
                sum(c['passed'] for c in single)/len(single),rmuc['passed']/rmuc['total'],r['passed']/r['total'])
    best=max(reports,key=score);dest=HERE/'weights/E_stair_nav4d_candidate.pt';shutil.copy2(best['checkpoint'],dest)
    put(HERE/'evidence/STAIR_CHECKPOINT_SELECTION.json',dict(best=best,all_checkpoints=reports,ranking='single200 gate, RMUL200 rate, single200 rate, RMUC rate, total rate'))
    put(HERE/'CANDIDATE_NAV4D.json',dict(status='experimental_pending_final_acceptance',stair=dict(checkpoint=str(dest.relative_to(HERE)),sha256=sha256(dest),source=best['checkpoint'],screen_folder=best['screen_folder'],single200_preserved=best['single200_preserved'])))
    return best

def screen_jumps(job):
    folder=HERE/'evidence'/job;reports=[]
    for path in sorted(folder.glob('model_*.pt')):
        out=HERE/'evidence/checkpoint_screens/jump'/path.stem;out.mkdir(parents=True,exist_ok=True)
        with (out/'eval.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(PYTHON),'-B',str(HERE/'eval_jump_all_regimes.py'),'--checkpoint',str(path),'--workers','6','--out',str(out)],
                           cwd=HERE,stdout=log,stderr=subprocess.STDOUT,check=True)
        r=json.loads((out/'SUMMARY.json').read_text(encoding='utf-8'));r['screen_folder']=str(out.relative_to(HERE));reports.append(r)
        print('JUMP_SCREEN',path.name,r['groups_passed'],r['groups_liftoff'],r['flips'],flush=True)
    best=max(reports,key=lambda r:(r['flips']==0 and r['groups_liftoff']>=54,r['flips']==0,r['groups_passed'],r['replays_liftoff'],-r['flips']))
    dest=HERE/'weights/E_jump_unified_candidate.pt';shutil.copy2(best['checkpoint'],dest)
    put(HERE/'evidence/JUMP_CHECKPOINT_SELECTION.json',dict(best=best,all_checkpoints=reports))
    candidate=json.loads((HERE/'CANDIDATE_NAV4D.json').read_text(encoding='utf-8'))
    candidate['jump']=dict(checkpoint=str(dest.relative_to(HERE)),sha256=sha256(dest),source=best['checkpoint'],
                           screen_folder=best['screen_folder'],groups_liftoff=best['groups_liftoff'],flips=best['flips'])
    put(HERE/'CANDIDATE_NAV4D.json',candidate);put(HERE/'CANDIDATE.json',candidate)
    return best

def main():
    try:
        wait_closed('stair_train_r1_api2')
        screen_stairs('stair_train_r1_api2')
        run_remote('probe','--job','jump_probe_r2','--script','train_jump_unified.py')
        wait_closed('jump_probe_r2')
        with connect('host72') as ssh,ssh.open_sftp() as sftp:sftp.put(str(HERE/'probe_jump_alignment.py'),str(ROOT/'probe_jump_alignment.py'))
        run_remote('probe','--job','jump_alignment_r2','--script','probe_jump_alignment.py')
        alignment=wait_closed('jump_alignment_r2')
        assert alignment['PROBE.json']['nominal_liftoff_rate']>.50
        run_remote('train','--job','jump_train_r2','--probe','jump_probe_r2','--script','train_jump_unified.py','--seconds','1050')
        wait_closed('jump_train_r2');screen_jumps('jump_train_r2')
        put(HERE/'evidence/TRAINING_PIPELINE_COMPLETE.json',dict(passed=True,stage='both_guarded_jobs_and_cpu_screening_complete',epoch=time.time()))
    except BaseException:
        import traceback
        error=traceback.format_exc();(HERE/'evidence/PIPELINE_ERROR.txt').write_text(error,encoding='utf-8');print(error,flush=True);raise

if __name__=='__main__':main()
