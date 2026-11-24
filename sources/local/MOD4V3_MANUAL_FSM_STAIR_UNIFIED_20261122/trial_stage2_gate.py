"""A bounded diagnostic of pitch-impulse gating on the six complete-map starts."""
from concurrent.futures import ProcessPoolExecutor
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from eval_manual_fsm_all import cases
from fsm_evaluation import run_case


def worker(job):
    case,config,folder=job
    row,trace=run_case(case,checkpoint=HERE/'weights/E_stair_r9_009m_selected.pt',detector=config)
    put(folder/'cases'/(case['id']+'.json'),row)
    (folder/'traces').mkdir(parents=True,exist_ok=True)
    np.savez_compressed(folder/'traces'/(case['id']+'.npz'),**trace)
    return row


def main():
    config=json.loads((HERE/'DETECTOR.json').read_text())['config']
    config['clean_impulse_pitch_min']=-.1
    jobs=[r for r in cases('stair') if r['course'] in ('rm27_west','rm27_east') and not r['dr']]
    folder=HERE/'evidence/stage2_gate_pitch_impulse_trial'
    rows=[]
    with ProcessPoolExecutor(2) as pool:
        for row in pool.map(worker,[(r,config,folder) for r in jobs]):
            rows.append(row);print(row['id'],row['passed'],row['physical_crossed'],row['failure'],
                row['precontact_active_samples'],row['trigger_delay_ms'],flush=True)
    put(folder/'RESULT.json',dict(config=config,rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows),
        precontact_active_samples=sum(r['precontact_active_samples'] for r in rows)))


if __name__=='__main__':main()
