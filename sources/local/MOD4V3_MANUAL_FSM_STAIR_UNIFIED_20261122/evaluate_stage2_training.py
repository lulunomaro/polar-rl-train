"""Collect the one bounded round, screen snapshots sequentially, then finalize."""
from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
import sys
import time
from fsm_paths import HERE
from fsm_io import put
from remote_manual_fsm import connect,collect


def main():
    p=ArgumentParser(description=__doc__);p.add_argument('--tag',default='fsm_r10c')
    p.add_argument('--finalize',action='store_true');args=p.parse_args()
    # A manually started first screen owns the two workers until its receipt appears.
    first=HERE/'evidence/stage2_screen_r10_003m/RESULT.json'
    while not first.is_file():time.sleep(5.)
    py=[sys.executable,'-B','-X','utf8']
    folder=HERE/'evidence'/args.tag
    while True:
        with connect('host72') as ssh:collect(ssh,args.tag,'train')
        snapshots=[p for p in sorted((folder/'train').glob('model_*.pt')) if p.name!='model_first_complete.pt']
        for checkpoint in snapshots:
            label=checkpoint.stem.removeprefix('model_')
            output=HERE/'evidence'/f'stage2_screen_r10_{label}'
            if (output/'RESULT.json').is_file():continue
            with (HERE/'evidence'/f'stage2_screen_r10_{label}.log').open('w',encoding='utf-8') as log:
                subprocess.run(py+[str(HERE/'screen_stage2_checkpoints.py'),'--checkpoint',str(checkpoint),
                    '--out',str(output),'--workers','2'],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,check=True)
            result=json.loads((output/'RESULT.json').read_text())
            print('CHECKPOINT',label,result['score'],flush=True)
        exit_path=folder/'train_EXIT.json'
        if exit_path.is_file() and exit_path.stat().st_size:
            exit_record=json.loads(exit_path.read_text())
            if 'exit_code' in exit_record and 'own_gpu_process_released' in exit_record:break
        time.sleep(20.)
    candidates=[]
    for output in [HERE/'evidence/stage2_screen_r9',*sorted((HERE/'evidence').glob('stage2_screen_r10_*'))]:
        if not output.is_dir() or not (output/'RESULT.json').is_file():continue
        result=json.loads((output/'RESULT.json').read_text())
        result['evidence']=str((output/'RESULT.json').relative_to(HERE))
        result.pop('rows')
        result['round']='fsm_r9' if output.name=='stage2_screen_r9' else args.tag
        result['package_source']='evidence/fsm_r9/train/model_009m.pt' if result['round']=='fsm_r9' else result['checkpoint']
        candidates.append(result)
    candidates.sort(key=lambda r:tuple(r['score']),reverse=True)
    selected=candidates[0]
    put(HERE/'evidence/STAGE2_CHECKPOINT_SELECTION.json',dict(selected=selected,candidates=candidates,
        criterion='Fixed 22-case causal closed-loop comparison: zero unforced preactivation, complete-map nominal RM strict passes, all strict passes, physical no-fall crossings, fewer falls. Final 320-case acceptance is independent.',
        final_checkpoint_not_automatically_selected=True))
    print('SELECTED',selected['checkpoint'],selected['score'],flush=True)
    if args.finalize:
        subprocess.run(py+[str(HERE/'package_candidate.py'),'--source',str(HERE/selected['package_source']),
            '--round',selected['round']],cwd=HERE,check=True)
        subprocess.run(py+[str(HERE/'run_stage2_acceptance.py')],cwd=HERE,check=True)


if __name__=='__main__':main()
