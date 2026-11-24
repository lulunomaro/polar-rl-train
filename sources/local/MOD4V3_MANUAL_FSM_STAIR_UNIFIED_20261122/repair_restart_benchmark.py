"""Re-run only the zero-speed setup cases; preserve all previous raw evidence."""
from concurrent.futures import ProcessPoolExecutor
from eval_manual_fsm_all import cases,worker
from fsm_paths import HERE
from fsm_io import put


def main():
    folder=HERE/'evidence/r9_009m_stationary_restart'
    jobs=[(c,HERE/'evidence/fsm_r9/train/model_009m.pt',folder) for c in cases('stair') if c.get('restart')]
    rows=[]
    with ProcessPoolExecutor(2) as pool:
        for row in pool.map(worker,jobs):
            rows.append(row);print(row['id'],row['passed'],row['longest_bilateral_support_substeps'],
                row['restart_initial_state']['root_velocity'],flush=True)
    put(folder/'RESULT.json',dict(rows=rows,total=len(rows),passed=sum(r['passed'] for r in rows),
        note='Previous fixed-duration stop prelude did not guarantee stationary initial conditions; its results remain archived.'))


if __name__=='__main__':main()
