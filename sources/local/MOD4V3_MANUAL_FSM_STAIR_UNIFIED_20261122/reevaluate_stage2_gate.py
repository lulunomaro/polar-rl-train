"""Recheck affected Full-DR ranking after the measured false-trigger correction."""
from concurrent.futures import ProcessPoolExecutor
import json
import subprocess
import sys
from pathlib import Path
from fsm_paths import HERE
from fsm_io import put,sha256
from eval_manual_fsm_all import worker


def main():
    prior=json.loads((HERE/'evidence/STAGE2_CHECKPOINT_SELECTION_BEFORE_GATE_FIX.json').read_text())
    candidates=[]
    new_config=json.loads((HERE/'DETECTOR.json').read_text())['config']
    assert new_config['obstruction_ticks']==1 and new_config['obstruction_pitch']==.02
    with ProcessPoolExecutor(2) as pool:
        for meta in prior['candidates']:
            old=json.loads((HERE/meta['evidence']).read_text())
            checkpoint=HERE/meta['checkpoint']
            output=HERE/'evidence/stage2_gate_checkpoints'/f"{meta['round']}_{checkpoint.stem}"
            case_keys=('id','course','speed','height','yaw_deg','offset','seconds','settle_s','wz',
                       'task','edge_sign','armed','dr','seed','restart','force_at_s')
            jobs=[{k:r[k] for k in case_keys if k in r} for r in old['rows'] if r['dr']]
            new=[]
            for row in pool.map(worker,[(r,checkpoint,output) for r in jobs]):new.append(row)
            nominal=[r for r in old['rows'] if not r['dr']]
            rows=nominal+new
            rm=[r for r in nominal if r['course'] in ('rm27_west','rm27_east')]
            score=[-sum(bool(r['precontact_active_samples']) for r in rows if r.get('force_at_s') is None),
                sum(r['passed'] for r in rm),sum(r['passed'] for r in rows),
                sum(r['physical_crossed'] and not r['failure'] for r in rows),-sum(bool(r['failure']) for r in rows)]
            proof='For clean sensors and obstruction_ticks=1, both old -.02 and new +.02 limits are dominated by the existing clean-pitch >.025 condition. All nominal phase/action trajectories are therefore unchanged. Affected Full-DR cases are newly simulated.'
            result=dict(meta,score=score,passed=sum(r['passed'] for r in rows),rows=rows,
                detector_sha256=sha256(HERE/'DETECTOR.json'),nominal_reuse_proof=proof,
                full_dr_rerun_cases=len(new),evidence=str((output/'RESULT.json').relative_to(HERE)))
            put(output/'RESULT.json',result)
            summary={k:v for k,v in result.items() if k!='rows'}
            candidates.append(summary)
            print('FINAL GATE',meta['checkpoint'],score,flush=True)
    candidates.sort(key=lambda r:tuple(r['score']),reverse=True)
    selected=candidates[0]
    put(HERE/'evidence/STAGE2_CHECKPOINT_SELECTION.json',dict(selected=selected,candidates=candidates,
        final_checkpoint_not_automatically_selected=True,gate_correction_after_ppo=True,
        criterion='Same fixed 22-case ranking, with every affected Full-DR case newly simulated and unchanged nominal trajectories retained by the documented causal equivalence. Full final acceptance is then newly simulated.'))
    py=[sys.executable,'-B','-X','utf8']
    name=f"E_stair_stage2_gate_final_{selected['round']}_{Path(selected['package_source']).stem}.pt"
    subprocess.run(py+[str(HERE/'package_candidate.py'),'--source',str(HERE/selected['package_source']),
        '--round',selected['round'],'--name',name],cwd=HERE,check=True)
    candidate=json.loads((HERE/'CANDIDATE.json').read_text())
    subprocess.run(py+[str(HERE/'remote_manual_fsm.py'),'probe','--tag','fsm_r10d_finalgate',
        '--checkpoint',str(HERE/candidate['checkpoint'])],cwd=HERE,check=True)
    subprocess.run(py+[str(HERE/'run_stage2_acceptance.py')],cwd=HERE,check=True)


if __name__=='__main__':main()
