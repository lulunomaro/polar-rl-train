"""Run final shared-player acceptance sequentially with exactly two CPU workers."""
from argparse import ArgumentParser
from datetime import datetime,timezone
from pathlib import Path
import json
import subprocess
import sys
import time
from fsm_paths import HERE,ROOT
from fsm_io import put,sha256


def main():
    p=ArgumentParser(description=__doc__);p.add_argument('--resume',action='store_true');args=p.parse_args()
    candidate=json.loads((HERE/'CANDIDATE.json').read_text(encoding='utf-8'))
    checkpoint=HERE/candidate['checkpoint']
    folder=HERE/'evidence/stage2_final';folder.mkdir(parents=True,exist_ok=True)
    identity={n:sha256(HERE/n) for n in ('CANDIDATE.json','DETECTOR.json','E0_CALIBRATION.json',
        'manual_fsm_model.py','manual_fsm_core.py','manual_fsm_runtime.py','fsm_evaluation.py')}
    identity['checkpoint']=sha256(checkpoint)
    state_path=folder/'RUN.json'
    state=json.loads(state_path.read_text()) if args.resume and state_path.is_file() else dict(identity=identity,steps=[])
    if state['identity']!=identity:raise RuntimeError('Resume inputs differ from the recorded selected controller')
    def run(name,command):
        if any(r['name']==name and r['exit_code']==0 for r in state['steps']):return
        log=folder/(name+'.log');start=time.monotonic()
        print('START',name,flush=True)
        with log.open('w',encoding='utf-8') as output:
            result=subprocess.run([str(v) for v in command],cwd=HERE,stdout=output,stderr=subprocess.STDOUT)
        state['steps'].append(dict(name=name,exit_code=result.returncode,seconds=time.monotonic()-start,
            log=str(log.relative_to(HERE)),utc=datetime.now(timezone.utc).isoformat()))
        put(state_path,state)
        print('END',name,result.returncode,flush=True)
        if result.returncode:raise RuntimeError(f'{name} failed; see {log}')
    py=[sys.executable,'-B','-X','utf8']
    for suite in ('flat60','flat','premature','stair'):
        run(suite,py+[HERE/'eval_manual_fsm_all.py','--suite',suite,'--checkpoint',checkpoint,
            '--workers','2','--out',folder/suite])
    run('holdout',py+[HERE/'eval_detector_holdout.py','--tag','stage2_final/holdout','--seed','919',
        '--checkpoint',checkpoint,'--workers','2'])
    run('rm_diagnosis',py+[HERE/'diagnose_stage2_rm27.py'])
    run('window_audit',py+[HERE/'audit_stage2_windows.py',folder/'stair'])
    run('jump',py+[HERE/'eval_fsm_jump.py','--checkpoint',checkpoint,'--workers','2','--out',folder/'jump'])
    run('video_cases',py+[HERE/'select_stage2_video_cases.py'])
    run('videos',py+[HERE/'render_fsm_evidence.py','--checkpoint',checkpoint,'--out',HERE/'evidence/videos_final',
        '--case-file',folder/'VIDEO_CASES.json'])
    run('video_verify',py+[HERE/'verify_fsm_videos.py','--folder',HERE/'evidence/videos_final'])
    run('smoke',['cmd.exe','/d','/c',str(ROOT/'Run_MOD4v3_ManualFSM_Unified_WASD.bat'),'--smoke'])
    run('assets',py+[HERE/'audit_assets.py','--verify'])
    run('report',py+[HERE/'build_stage2_report.py'])


if __name__=='__main__':main()
