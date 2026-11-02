"""Fresh R36 TRAIN only. R35's four consumed baseline episodes are not replayed.
Eight fresh baseline seeds204..211; gain2/4 nominal+201..208 were not started inR35.
Only seeds204..208 form three-way paired comparisons. No heldout tuning.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import time

R = Path(__file__).resolve().parent
D = R/'batches/r36b_heading26'
D.mkdir(parents=True, exist_ok=False)
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
with (D/'PREP.log').open('xb') as f:
    rc = subprocess.run([sys.executable, '-B', str(R/'prepare_r36_heading_v3.py'), '--receipt-dir', str(D/'preflight')], cwd=R, env=env, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT).returncode
if rc:
    raise RuntimeError('zero-physics R36 preflight failed; no physical cases launched')

jobs = [(0., s) for s in range(204, 212)] + [(k, s) for k in (2., 4.) for s in [0]+list(range(201, 209))]
controller = dict(position_weight=25., position_leash=1., yaw_kp=.8, yaw_ki=.5, yaw_integral_limit=15., yaw_rate_ff=.052, heading_correction_cap=.8)
protocol = dict(kind='R36_NEW_HEADING_TRAIN_NOT_C_H4', baseline_seeds=list(range(204,212)), candidate_seeds=[0]+list(range(201,209)), paired_seeds=list(range(204,209)), old_consumed_baseline_excluded=[0,201,202,203], gains=[0.,2.,4.], duration_s=12., forward_m_s=2., kinematic_radius_m=.0625, physical_tire_radius_m=.06369999796152115, new_lane_max_abs_y_m=.3, original_speed_pose_support_contact_gate_retained=True, heading_source='first_sensor_estimated_relative_yaw_only', no_worldXY_input=True, full_D0_D7_physical_path=True, hardware=False, source_manifest=[])
for name in ('heading_hold_controller_v2.py','run_heading_hold_case_v3.py','streamed_trace_rows_v1.py','prepare_r36_heading_v3.py',Path(__file__).name):
    raw = (R/name).read_bytes()
    (D/name).write_bytes(raw)
    protocol['source_manifest'].append(dict(path=str(R/name), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
(D/'PROTOCOL.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')

def run(job):
    k, seed = job
    case = f'r36b_heading_k{round(k)}_{seed}'
    config = dict(case_id=case, seed=seed, nominal=seed==0, mode='forward', duration_s=12., command_at_s=1., forward_m_s=2., controller=dict(controller, heading_hold_k=k), kinematic_radius_m=.0625, feedback='sensors', upright_arming_prior=True, accel_reference='wheel_midpoint')
    cp = D/(case+'.json')
    cp.write_text(json.dumps(config, indent=2), encoding='utf-8')
    start = time.time()
    with (D/(case+'.log')).open('xb') as log:
        rc = subprocess.run([sys.executable, '-B', str(R/'run_heading_hold_case_v3.py'), '--config', str(cp), '--out', str(R/'results'/case)], cwd=R, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT).returncode
    rp = R/'results'/case/'result.json'
    result = json.loads(rp.read_bytes()) if rp.exists() else {}
    row = dict(case=case, k=k, seed=seed, returncode=rc, start=start, end=time.time(), complete=result.get('complete'), base_gate=result.get('proposed_gate_passed'), lane_pass=result.get('heading_lane_TRAIN_pass'), peak_abs_y_m=result.get('peak_abs_y_m'), mean_v=result.get('tail_velocity_mean_m_s'), v_RMS=result.get('tail_v_tracking_RMSE'), controls=result.get('controls'), physics_callbacks=result.get('physics_callbacks'), trace=result.get('trace_artifact'))
    print(json.dumps(row), flush=True)
    return row

rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for offset in range(0, len(jobs), 4):
        chunk = list(pool.map(run, jobs[offset:offset+4]))
        rows.extend(chunk)
        if any(row['returncode'] for row in chunk):
            (D/'SOFTWARE_ABORT.json').write_text(json.dumps(dict(rows=rows, unstarted=jobs[offset+4:]), indent=2), encoding='utf-8')
            raise RuntimeError('new R36 software error; unstarted cases aborted')
summary = {}
for k in (0.,2.,4.):
    dr_rows = [r for r in rows if r['k']==k and r['seed']!=0]
    paired = [r for r in dr_rows if r['seed'] in range(204,209)]
    summary[str(k)] = dict(n_DR=len(dr_rows), complete_DR=sum(bool(r['complete']) for r in dr_rows), base_pass_DR=sum(bool(r['base_gate']) for r in dr_rows), lane_pass_DR=sum(bool(r['lane_pass']) for r in dr_rows), paired_n=len(paired), paired_base_pass=sum(bool(r['base_gate']) for r in paired), paired_lane_pass=sum(bool(r['lane_pass']) for r in paired), nominal=[r for r in rows if r['k']==k and r['seed']==0])
(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='R36_HEADING_TRAIN26_NOT_HOLDOUT', summary=summary, rows=rows), indent=2), encoding='utf-8')
print('SUMMARY', json.dumps(summary), flush=True)
